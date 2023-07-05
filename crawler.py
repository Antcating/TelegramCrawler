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

# Import config parser
config = configparser.ConfigParser()
config.sections()

config.read("config.ini")
# Enter your Telegram API token here
API_ID = config["API_ID"]
API_HASH = config["API_HASH"]

# Enter the starting channel ID here
START_CHANNEL_ID = config["START_CHANNEL_ID"]

# Create a lock for thread synchronization
lock = threading.Lock()

# Start the save mechanism in a separate thread
save_thread = threading.Thread()

# Date of split in analysis
DATE_BREAK = datetime.datetime(2022, 2, 24, 3, 0, 0, tzinfo=datetime.timezone.utc)

# Global variables
visited_links = set()
crawled_links = 0
channel_queue = Queue()
connection_strength = dict()
nodes = dict()

async def crawl_channel(client):
    global save_thread
    async with client:
        channel_id = channel_queue.get()
        try:
            channel = await client.get_entity(channel_id)
            if channel.id not in visited_links:
                nodes[channel.id] = channel
                visited_links.add(channel.id)
            # Check if the request was successful
            print(f"Crawling channel: {channel.title}")

            async for message in client.iter_messages(channel):
                await message_processing(client, channel, message)

            print(channel.title, "crawl completed")
            channel_queue.task_done()

            save_thread = threading.Thread(target=save_crawled_channels(channel))
            save_thread.start()
            save_thread.join()
        # except telethon.errors.ChannelPrivateError as e:
        #     print(f"Error crawling channel {channel_id}: {e}")
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
            if destination_channel:
                await update_channels(channel, destination_channel, message, 0)
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

            if destination_channel:
                await update_channels(channel, destination_channel, message, 1)


def save_crawled_channels(channel):
    print("Saving files: ", channel.title)
    global visited_links, connection_strength, nodes
    # Save the visited links set to a file
    with open("output/visited_links.pkl", "wb") as file:
        pickle.dump(visited_links, file)
    # Save the channel queue to a file
    with open("output/channel_queue.pkl", "wb") as file:
        pickle.dump(list(channel_queue.queue), file)
    # Save the connection strength dictionary to a file
    with open("output/connection_strength_" + str(channel.id) + ".pkl", "wb") as file:
        pickle.dump(connection_strength, file)
    with open("output/nodes_" + str(channel.id) + ".pkl", "wb") as file:
        pickle.dump(nodes, file)
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


async def update_channels(origin, destination, message, type):
    global crawled_links, visited_links, connection_strength, nodes
    # Acquire the lock before updating the visited links set
    with lock:
        # Check if the channel has already been visited
        if destination.id not in visited_links:
            visited_links.add(destination.id)
            nodes[destination.id] = destination
            crawled_links += 1
            # Add the forwarded channel to the queue for crawling
            channel_queue.put(destination.id)

        # Update the connection strength

        if message.date < DATE_BREAK:
            date_stamp = "before"
        elif message.date >= DATE_BREAK:
            date_stamp = "after"
        if origin.id not in connection_strength:
            connection_strength[origin.id] = {}
            connection_strength[origin.id]["before"] = {}
            connection_strength[origin.id]["after"] = {}

        if destination.id not in connection_strength[origin.id][date_stamp]:
            connection_strength[origin.id][date_stamp][destination.id] = {
                "origin_id": origin.id,
                "origin_title": origin.title,
                "destination_id": destination.id,
                "destination_title": destination.title,
                "strength": 1,
                "type": type,
            }
        else:
            connection_strength[origin.id][date_stamp][destination.id]["strength"] += 1

            if (
                type == 0
                and connection_strength[origin.id][date_stamp][destination.id]["type"]
                == 1
            ):
                connection_strength[origin.id][date_stamp][destination.id]["type"] = 0


async def main():
    global save_thread

    try:
        client = TelegramClient("session_name", API_ID, API_HASH)
        await client.start()
        load_crawled_channels()
        # save_thread = threading.Thread(target=save_crawled_channels)
        # save_thread.start()

        # Add the starting channel to the queue if it's not in the visited links set
        if START_CHANNEL_ID not in visited_links:
            channel_queue.put(START_CHANNEL_ID)

        while True:
            # Create new thread in place completed one
            if not channel_queue.empty():
                await crawl_channel(client)

            # Wait for all tasks to be completed
        channel_queue.join()

    except KeyboardInterrupt:
        print("Exiting the crawler..")


asyncio.run(main())
