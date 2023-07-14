import asyncio
import datetime
import telethon.types
from telethon.sync import TelegramClient
from queue import Queue
import threading
import pickle
import traceback
from url import url_handler
import configparser

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session

from db_class import TelegramChannel, TelegramConnection, TelegramQueue, Base

# Import config parser
config = configparser.ConfigParser()
config.sections()

config.read("config.ini")
# Enter your Telegram API token here
API_ID = config["MAIN"]["API_ID"]
API_HASH = config["MAIN"]["API_HASH"]

# Enter the starting channel ID here
START_CHANNEL_ID = int(config["MAIN"]["START_CHANNEL_ID"])

# Create a lock for thread synchronization
lock = threading.Lock()

# Start the save mechanism in a separate thread
save_thread = threading.Thread()

# Date of split in analysis
DATE_BREAK = datetime.datetime(2022, 2, 24, 3, 0, 0, tzinfo=datetime.timezone.utc)

# Postgres
engine = create_engine(config["MAIN"]["POSTGRES"])
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)

# Global variables
visited_links = set()
channel_queue = Queue()
nodes = dict()


async def crawl_channel(client):
    global save_thread
    async with client:
        with Session.begin() as session:
            channel_id = (
                session.query(TelegramQueue)
                .order_by(TelegramQueue.date.desc())
                .limit(1)
                .one()
                .id
            )
        try:
            channel = await client.get_entity(channel_id)

            # Update channels table
            if not channel.megagroup:
                await update_channels(channel)

                # Check if the request was successful
                print(f"Crawling channel: {channel.title}")

                async for message in client.iter_messages(channel):
                    await message_processing(client, channel, message)

                print(channel.title, "crawl completed")
                channel_queue.task_done()

                save_thread = threading.Thread(target=save_crawled_channels(channel))
                save_thread.start()
                save_thread.join()

            with Session.begin() as session:
                session.query(TelegramQueue).filter_by(id=channel_id).delete()
        except Exception as e:
            traceback.print_exc()
            raise "Exception"


async def message_processing(client, channel, message):
    print(f"Currenty on message: {message.id}", end="\r", flush=True)
    if message.fwd_from:
        if type(message.fwd_from.from_id) == telethon.types.PeerChannel:
            # Get the channel ID from the forwarded message
            forwarded_channel_id = message.fwd_from.from_id.channel_id
            destination_channel = await url_handler(client, forwarded_channel_id)
            if destination_channel and not destination_channel.megagroup:
                await update_channels(destination_channel)
                await update_connections(channel, destination_channel, message, 0)
    elif message.entities:
        for entity in message.entities:
            destination_channel = None
            if type(entity) == telethon.types.MessageEntityMention:
                url = message.message[entity.offset : entity.offset + entity.length]

                destination_channel = await url_handler(client, url)
            elif type(entity) == telethon.types.MessageEntityTextUrl:
                url = entity.url

                destination_channel = await url_handler(client, url)
            elif type(entity) == telethon.types.MessageEntityUrl:
                url = message.message[entity.offset : entity.offset + entity.length]

                destination_channel = await url_handler(client, url)

            if destination_channel and not destination_channel.megagroup:
                await update_channels(destination_channel)
                await update_connections(channel, destination_channel, message, 0)


def save_crawled_channels(channel):
    print("Saving files: ", channel.title)
    global visited_links
    # Save the visited links set to a file
    with open("output/visited_links.pkl", "wb") as file:
        pickle.dump(visited_links, file)
    # Save the channel queue to a file
    with open("output/channel_queue.pkl", "wb") as file:
        pickle.dump(list(channel_queue.queue), file)
    connection_strength = dict()
    nodes = dict()
    print("Saving completed")


def load_crawled_channels():
    print("Initial loading...")
    global visited_links
    try:
        # Load the visited links set from a file
        with open("visited_links.pkl", "rb") as file:
            visited_links = pickle.load(file)
    except FileNotFoundError:
        visited_links = set()

    try:
        # Load the channel queue from a file
        with open("output/channel_queue.pkl", "rb") as file:
            saved_queue = pickle.load(file)
            for item in saved_queue:
                channel_queue.put(item)
    except FileNotFoundError:
        pass


async def update_channels(channel):
    global visited_links
    with Session.begin() as session:
        # Acquire the lock before updating the visited links set
        # Check if the channel has already been visited
        if channel.id not in visited_links:
            visited_links.add(channel.id)
            # Add the forwarded channel to the queue for crawling
            channel_queue.put(channel.id)
        if not session.query(
            session.query(TelegramQueue).filter_by(id=channel.id).exists()
        ).scalar():
            ChannelQueue = TelegramQueue(id=channel.id, date=datetime.datetime.now())
            session.merge(ChannelQueue)
        # To channel database
        ChannelRow = TelegramChannel(
            id=channel.id,
            title=channel.title,
            username=channel.username if channel.username else 0,
            date=channel.date,
        )
        session.merge(ChannelRow)


async def update_connections(origin, destination, message, type):
    with Session.begin() as session:
        if message.date < DATE_BREAK:
            date_stamp = "before"
        elif message.date >= DATE_BREAK:
            date_stamp = "after"

        # TelegramConnections.update()
        if not session.query(TelegramConnection).filter_by(
            id_origin=origin.id, id_destination=destination.id
        ):
            ConnectionRow = TelegramConnection(
                id_origin=origin.id,
                id_destination=destination.id,
                strength=1,
                type=type,
            )
            session.merge(ConnectionRow)

        else:
            session.query(TelegramConnection).filter_by(
                id_origin=origin.id, id_destination=destination.id
            ).update(
                {
                    TelegramConnection.strength: TelegramConnection.strength + 1,
                    TelegramConnection.type: type,
                }
            )


async def main():
    global save_thread

    try:
        client = TelegramClient("session_name", API_ID, API_HASH)
        await client.start()
        load_crawled_channels()
        # save_thread = threading.Thread(target=save_crawled_channels)
        # save_thread.start()

        # Add the starting channel to the queue if it's not in the visited links set

        with Session.begin() as session:
            if not session.query(
                session.query(TelegramChannel).filter_by(id=START_CHANNEL_ID).exists()
            ).scalar():
                ChannelStart = TelegramQueue(
                    id=START_CHANNEL_ID, date=datetime.datetime.now()
                )
                session.merge(ChannelStart)
        while True:
            # Create new thread in place completed one
            if not channel_queue.empty():
                await crawl_channel(client)

                # Wait for all tasks to be completed
            channel_queue.join()

    except KeyboardInterrupt:
        print("Exiting the crawler..")


asyncio.run(main())
