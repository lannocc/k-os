from version import VVHEN


INSTALLED = {
    'help': 'please wait',
    'ver': VVHEN,
}


def install(cmd, data):
    INSTALLED[cmd] = data

def help():
    txt = 'installed commands:'
    for cmd in INSTALLED:
        txt += ' '+cmd
    return txt

install('help', help)


def shell(cmdline):
    if not cmdline:
        return None

    cmdline = cmdline.strip()
    space = cmdline.find(' ')

    if space > 0:
        return (cmdline[:space], cmdline[space+1:])
    else:
        return (cmdline,)


def call(*args):
    if not args or len(args) < 1:
        return None

    cmd = args[0]
    if not cmd:
        return None

    if cmd in INSTALLED:
        data = INSTALLED[cmd]

        if isinstance(data, Handler):
            args = args[1:]
            if args:
                return data.call(*args)
            else:
                return data.call()
        elif callable(data):
            args = args[1:]
            if args:
                return data(*args)
            else:
                return data()
        elif isinstance(data, str):
            return data
        else:
            return str(data)

    else:
        return Exception(f'unknown command: {cmd}')


class Handler:
    def __init__(self, k):
        self.k = k

    def call(self, *args):
        pass

