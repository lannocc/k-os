import k.storage as media


class Module:
    def __init__(self, kdb, web, printer=print):
        self.kdb = kdb
        self.web = web
        self.print = print

    async def handle(self, websocket, req):
        if 'channel' in req:
            channel = req['channel']
            videos = self.kdb.list_videos(channel_id=channel)
            await self.web(websocket, videos, 'videos')

        else:
            channels = self.kdb.list_channels()
            await self.web(websocket, channels, 'channels')

