import asyncio
import datetime
import requests
import telethon.types
from telethon.sync import TelegramClient
import traceback
from url import url_handler
import configparser

# Import config parser
config = configparser.ConfigParser()
config.sections()
config.read("config.ini")
# Enter your Telegram API token here
API_ID = config["CRAWLER"]["API_ID"]
API_HASH = config["CRAWLER"]["API_HASH"]

# Enter the starting channel USERNAME here
START_CHANNEL_USERNAME = int(config["CRAWLER"]["START_CHANNEL_USERNAME"])

# Postgres
# engine = create_engine(config["CRAWLER"]["POSTGRES"])
# Base.metadata.create_all(bind=engine)
# Session = SessionLocal()

# Server
SERVER = config["CRAWLER"]["SERVER"]


async def crawl_channel(client: TelegramClient, channel_id: int):
    """Gets channel from DB and parses messages

    Args:
        client (TelegramClient): Telegram UserAPI client
    """
    async with client:
        try:
            channel = await client.get_entity(channel_id)
            # Update channels table
            if not channel.megagroup:
                print(f"Crawling channel: {channel.title}")

                requests.delete(SERVER + "/connections/", params={'channel_id': channel_id})

                async for message in client.iter_messages(channel):
                    await message_processing(client, channel, message)

                print(channel.title, "crawl completed")

            response = requests.delete(SERVER + "/queue/", params={"channel_id": channel_id})
            # print(response.status_code, response.json())
        except Exception as e:
            traceback.print_exc()
            raise "Exception"


async def message_processing(
    client: TelegramClient,
    channel: telethon.types.Channel,
    message: telethon.types.Message,
):
    """Processes message: checks for links, mentions and forwards

    Args:
        client (TelegramClient): Telegram UserAPI client
        channel (telethon.types.Channel): Telegram Channel class object
        message (telethon.types.Message): Current message - Telegram Message class object
    """
    print(f"Currenty on message: {message.id}", end="\r", flush=True)
    if message.fwd_from:
        if type(message.fwd_from.from_id) == telethon.types.PeerChannel:
            # Get the channel ID from the forwarded message
            forwarded_channel_id = message.fwd_from.from_id.channel_id
            destination_channel = await url_handler(client, forwarded_channel_id)
            if destination_channel and not destination_channel.megagroup:
                await update_channels(destination_channel)
                await update_connections(channel, destination_channel, message)
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
                await update_connections(channel, destination_channel, message)


async def update_channels(channel: telethon.types.Channel):
    requests.post(
        SERVER + "/queue/",
        json={"id": channel.id, "date": str(datetime.datetime.now())},
        headers={"Content-type": "application/json"},
    )

    # To channel database
    payload = {
        "id": channel.id,
        "title": channel.title,
        "username": channel.username,
        "date": str(channel.date),
    }
    response = requests.post(SERVER + "/channel/", json=payload)


async def update_connections(
    origin: telethon.types.Channel,
    destination: telethon.types.Channel,
    message: telethon.types.Message,
):
    """Updates connections in PostgresQL

    Args:
        origin (telethon.types.Channel): Origin channel
        destination (telethon.types.Channel): Destination channel
        message (telethon.types.Message): Current Message in which connection was detected
    """
    response = requests.get(
        SERVER + "/connection_by_date/",
        params={"id_origin": origin.id, "id_destination": destination.id, "date": str(message.date)},
    )
    if response.status_code == 404:
        response = requests.post(
            SERVER + "/connection/",
            json={
                "id_origin": origin.id,
                "id_destination": destination.id,
                "strength": 1,
                "date": str(message.date),
            },
            headers={"Content-type": "application/json"},
        )
    elif response.status_code == 200:
        response = requests.patch(
            SERVER + "/connection/",
            params={
                "id_origin": origin.id,
                "id_destination": destination.id,
                "date": str(message.date),
            },
        )


async def main():
    global save_thread

    try:
        client = TelegramClient("session_name", API_ID, API_HASH)
        await client.start()

        queue_channel = requests.get(SERVER + "/queue/")
        if queue_channel.status_code == 404:
            response = input(
                """Your queue seems empty. Do you wanna add default starting channel defined in CONFIG? (y/n) 
By default starting channel set to channel of the creator of this scanner
Answer: """
            )[0]
            if response == "y":
                channel_username = START_CHANNEL_USERNAME
            else:
                channel_username = input("Enter your starting Channel username. Answer:")

            channel = await client.get_entity(channel_username)
            queue_channel = requests.post(
                SERVER + "/queue/",
                json={"id": channel.id, "date": str(datetime.datetime.now())},
                headers={"Content-type": "application/json"},
            )
        while queue_channel.status_code == 200:
            # Create new thread in place completed one
            channel_id = queue_channel.json()["id"]
            await crawl_channel(client, channel_id)

            queue_channel = requests.get(SERVER + "/queue/")

    except KeyboardInterrupt:
        print("Exiting the crawler..")


asyncio.run(main())
