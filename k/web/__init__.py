import websockets
from websockets.exceptions import ConnectionClosedError

import asyncio
import json
from importlib import import_module


PORT = 42981
PREAMBLE = '::K-OS::'
MAX_SIZE = 9_018_081 # max websocket message size (bytes)

MODULES = [
    'art',
    'video',
]


class Master:
    def __init__(self, kdb, printer=print):
        self.kdb = kdb
        self.print = printer

        for module in MODULES:
            setattr(self, module, None)

    def run(self):
        run_async(self.main, printer=self.print)

    async def main(self):
        self.print('setting up application modules...')
        for name in MODULES:
            self.print(f'   / {name}')
            mod = import_module(f'.{name}', package='k.web')
            mod = mod.Module(self.kdb, self.web, printer=self.print)
            setattr(self, name, mod)

        self.print('setting up websocket...')
        self.print(f'   / websocket server listening port {PORT}')
        async with websockets.serve(self.handler, '', PORT,
                                    max_size=MAX_SIZE):
            await asyncio.Future() # run forever

    async def handler(self, websocket):
        #addr = f'{websocket.id} {websocket.remote_address}'
        addr = f'{websocket.remote_address}'
        self.print(f'W+ got connection: {addr}')

        try:
            async for message in websocket:
                if not message.startswith(PREAMBLE):
                    self.print(f' --IGNORED-- {message}')
                    continue

                message = message[len(PREAMBLE):]
                req = json.loads(message)
                self.print(f'w    {addr} -> {req}')

                for mod, data in req.items():
                    try:
                        await getattr(self, mod).handle(websocket, data)

                    except AttributeError as e:
                        self.print(f' !!UNKNOWN (module)!! {mod} !! {e}')

            self.print(f'W- finished {addr}')

        except ConnectionClosedError:
            self.print(f'W- closed {addr} [CONNECTION CLOSED]')

        except Exception as e:
            name = type(e).__name__
            self.print(f'W- terminated {addr} [ERROR: {name}] !! {e}')
            raise e

    async def web(self, websocket, data, tag):
        assert tag
        #addr = f'{websocket.id} {websocket.remote_address}'
        addr = f'{websocket.remote_address}'
        data = { tag: data }
        #msg = json.dumps(data)
        msg = self.kdb.StoreEncoder().encode(data)
        self.print(f'W    {addr} <- {msg}')
        await websocket.send(msg)


def exception_handler(printer=print):
    def exception(loop, context):
        future = context.get('future')
        if not future: return
        func = future.get_coro().__name__
        msg = context.get('exception', context['message'])
        name = type(msg).__name__
        printer(f'!!EE!! ({func}) {name} !! {msg}')
    return exception


def run_async(amain, printer=print):
    async def emain():
        asyncio.get_running_loop().set_exception_handler(
                exception_handler(printer=printer))
        return await amain()
    return asyncio.run(emain())

