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


async def crawl_channel(client):
    async with client:
        with Session.begin() as session:
            channel_id = (
                session.query(TelegramQueue)
                .order_by(TelegramQueue.date)
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

async def update_channels(channel):
    with Session.begin() as session:
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
            with Session.begin() as session:
                ChannelsInQueue = session.query(TelegramQueue).count()
            if ChannelsInQueue > 0:
                await crawl_channel(client)

                # Wait for all tasks to be completed
            
    except KeyboardInterrupt:
        print("Exiting the crawler..")


asyncio.run(main())
