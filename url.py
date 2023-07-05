import telethon 
async def url_handler(client, url):
    channel_link = None
    if type(url) == int:
        channel_link = url
    elif type(url) == str:
        if len(url) == 0:
            return None
        if url[0] == '@':
            channel_link = url
        elif url[:4] == 'http':
            url_array = url.split('/')
            if url_array[2] == 't.me' or url_array[2] == 'telegram.me':
                channel_link = '@' + url_array[3]
        elif url[:5] == "t.me/":
            url_array = url.split('/')
            channel_link = '@' + url_array[1]
    
    if channel_link:
        try:
            entity = await client.get_entity(channel_link)
            if type(entity) == telethon.types.Channel:
                return entity
        except Exception:
            return None