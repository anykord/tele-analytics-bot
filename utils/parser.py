import asyncio, re
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, ChannelInvalidError

class TeleParser:
    def __init__(self, api_id, api_hash, session_name="tele_parser_session"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session = session_name

    async def _fetch(self, link, limit):
        client = TelegramClient(self.session, self.api_id, self.api_hash)
        await client.start()
        m = re.search(r"t\.me/(joinchat/)?([A-Za-z0-9_]+)", link)
        if not m:
            await client.disconnect()
            return []
        target = m.group(2)
        msgs = []
        try:
            async for message in client.iter_messages(target, limit=limit):
                if not message.message:
                    continue
                msgs.append({
                    "id": message.id,
                    "date": message.date.isoformat(),
                    "sender": getattr(message.sender, 'username', str(getattr(message.sender, 'id', ''))),
                    "text": message.message
                })
        except (ChannelPrivateError, ChannelInvalidError):
            pass
        await client.disconnect()
        return msgs

    def parse_from_link(self, link, limit=1000):
        return asyncio.get_event_loop().run_until_complete(self._fetch(link, limit))

