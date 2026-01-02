from k.ui import *
import k.meta
from k.meta.shadow import SW, SH
import k.cmd

from io import StringIO
from contextlib import redirect_stdout


PS1 = 'kush $'

PRIMER = (0, 27, 0)
PROMPT = YELLOW
CURSOR = GREEN
OUTPUT = (100, 155, 100)
CANCEL = (81, 81, 81)
EXCEPT = RED


class Mod(k.meta.Mod):
    def __init__(self, meta):
        if meta.fullscreen:
            super().__init__(meta,
                1*meta.size[0]/3 + 5, meta.ky + HEIGHT + 5,
                meta.size[0]/3 - 10, meta.ky - 10)
        else:
            super().__init__(meta,
                1*meta.size[0]/3 + 5, meta.ky + PHEIGHT + SH + 5,
                meta.size[0]/3 - 10, HEIGHT - STATUS - PHEIGHT - SH - 10)

        self.meta.shell = self
        k.cmd.install('python', Python(self))

        self.history = []
        self.buffer = ''

    def __call__(self, *args, **kwargs):
        call = k.cmd.shell(args[0])
        result = k.cmd.call(*call)
        self.history.append((args[0], result))
        self.paint()

    def init(self):
        self.paint_primer()

        self.prompt = self.meta.font2.render(PS1, True, PROMPT)
        self.paint_prompt()

        self.renders = []
        self.next = 0
        self.paint_history()

        self.buffer_img = self.meta.font2.render(self.buffer, True, CURSOR)
        self.buffer_old = self.buffer_img
        self.paint_buffer()

        self.clock = Clock(3)
        self.cursor = False
        self.paint_cursor()

    def tick(self):
        if self.focused:
            self.clock.tick()
            if self.clock.ready():
                self.cursor = not self.cursor
                self.paint_cursor()

        if self.next >= len(self.history):
            return

        for cmdline in self.history[self.next:]:
            color = CANCEL if cmdline[1] is None else CURSOR
            cmd = self.meta.font3.render(cmdline[0] if cmdline[0] else '',
                    True, color)
            out = []

            if cmdline[1] is not None:
                color = OUTPUT
                if isinstance(cmdline[1], Exception):
                    color = EXCEPT
                for line in f'{cmdline[1]}'.split('\n'):
                    img = self.meta.font2.render(line, True, color)
                    out.append(img)

            self.renders.append((cmd, out))
            self.next += 1

        self.paint()

    def kick(self, event):
        if event.type == pygame.KEYDOWN:
            self.log('kush key', event)

            if event.key == pygame.K_BACKSPACE:
                self.buffer = self.buffer[:-1]

            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                call = k.cmd.shell(self.buffer)
                if call is None:
                    self.history.append((None, None))
                else:
                    result = k.cmd.call(*call)
                    self.history.append((self.buffer, result))
                self.buffer = ''

            elif (event.mod & pygame.KMOD_CTRL and event.key == pygame.K_c) \
                    or event.unicode == '\x03':
                self.history.append((self.buffer, None))
                self.buffer = ''

            elif (event.mod & pygame.KMOD_CTRL and event.key == pygame.K_d) \
                    or event.unicode == '\x04':
                self.unfocus()

            else:
                self.buffer += event.unicode

            self.cursor = False
            self.paint_cursor()

            self.buffer_img = self.meta.font2.render(self.buffer, True, CURSOR)
            self.paint_buffer()

            self.clock.reset()

    def paint(self):
        self.paint_primer()
        self.paint_prompt()
        self.paint_history()
        self.paint_buffer(True)
        self.paint_cursor()

    def paint_primer(self):
        pygame.draw.rect(self.meta.screen, PRIMER,
            pygame.Rect((self.x, self.y), (self.w, self.h)))

    def paint_prompt(self):
        self.meta.screen.blit(self.prompt, (self.x,
            self.y + self.h - self.prompt.get_height()))

    def paint_history(self):
        showing = 0
        height = self.prompt.get_height()
        cx = self.x + int(self.w / 2)

        for cmd, out in reversed(self.renders):
            ch = cmd.get_height()
            if height + ch > self.h:
                break

            self.meta.screen.blit(cmd,
                (cx + 5,
                self.y + self.h - height - ch))

            if out:
                h = 0

                for line in reversed(out):
                    lh = line.get_height()
                    if height + h + lh > self.h:
                        break

                    h += lh
                    lw = line.get_width()

                    self.meta.screen.blit(line,
                        (self.x + int(self.w/2) - lw,
                        self.y + self.h - height - h))

                if h > ch:
                    height += h - ch

            height += ch
            showing += 1

        self.renders = self.renders[-showing:]

    def paint_buffer(self, fresh=False):
        bx = self.x + self.prompt.get_width()
        by = self.y + self.h - self.prompt.get_height()

        if fresh:
            self.meta.screen.blit(self.buffer_img, (bx, by))

        else:
            bw = self.buffer_img.get_width()
            bh = self.buffer_img.get_height()
            ow = self.buffer_old.get_width()

            if bw < ow:
                pygame.draw.rect(self.meta.screen, PRIMER,
                    pygame.Rect((bx + bw, by), (ow - bw, bh)))

            elif bw > ow:
                self.meta.screen.blit(self.buffer_img, (bx + ow, by), 
                    pygame.Rect((ow, 0), (bw - ow, bh)))

        self.buffer_old = self.buffer_img

    def paint_cursor(self):
        color = CURSOR if self.cursor else PRIMER
        pygame.draw.rect(self.meta.screen, color,
            pygame.Rect((self.x + self.prompt.get_width() + \
                    self.buffer_img.get_width(),
                self.y + self.h - self.prompt.get_height()),
                (9, self.prompt.get_height())))

    def focus(self):    
        super().focus()
        self.border(YELLOW)
        self.clock.reset()
        self.paint()

    def unfocus(self):
        super().unfocus()
        self.border(BLACK)

        if self.cursor:
            self.cursor = False
            #self.paint_cursor()

        self.clock.reset()
        self.paint()


class Python(k.cmd.Handler):
    def __init__(self, kush):
        super().__init__(kush.meta.k)
        self.meta = kush.meta
        self.kush = kush

    def call(self, *args):
        if not args:
            return 'python command needs argument'

        stmt = args[0]
        self.kush.log('kush python exec', stmt)

        out = StringIO()
        with redirect_stdout(out):
            exec(stmt)
        return out.getvalue()

