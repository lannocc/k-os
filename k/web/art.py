import k.storage as media


class Module:
    def __init__(self, kdb, web, printer=print):
        self.kdb = kdb
        self.web = web
        self.print = print

    async def handle(self, websocket, req):
        images = list(reversed(sorted(media.list_ack_images())))
        await self.web(websocket, images, 'images')

