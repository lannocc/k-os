import k.cmd


class Commands(k.cmd.Handler):
    def __init__(self, k):
        super().__init__(k)

    def call(self, *args):
        if not args:
            return 'player commands: play pause stop big normal kill'

        print(args)
        cmd = args[0]
        print(cmd)

        if cmd == 'play':
            return self.k.player.play()

        elif cmd == 'pause':
            return self.k.player.pause()

        elif cmd == 'stop':
            return self.k.player.stop()

        elif cmd == 'big':
            return self.k.player.size_big()

        elif cmd == 'normal':
            return self.k.player.size_normal()

        elif cmd == 'kill':
            return self.k.player.kill()

        else:
            return Exception(f'unknown player command: {cmd}')
   
