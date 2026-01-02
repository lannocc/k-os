from k.ui import *
import k.meta
from k.meta.shadow import SW, SH
import k.cmd


class Mod(k.meta.Mod):
    def __init__(self, meta):
        if meta.fullscreen:
            super().__init__(meta,
                2*meta.size[0]/3 + 5, meta.ky + HEIGHT + 5,
                meta.size[0]/3 - 10, meta.ky - 10)
        else:
            super().__init__(meta,
                2*meta.size[0]/3 + 5, meta.ky + PHEIGHT + SH + 5,
                meta.size[0]/3 - 10, HEIGHT - STATUS - PHEIGHT - SH - 10)

        self.history = []
        self.last = -1
        self.renders = []

    def init(self):
        self.prompt = self.meta.font2.render('chat > ', True, ORANGE)
        pygame.draw.rect(self.meta.screen, (27, 0, 0),
            pygame.Rect((self.x, self.y), (self.w, self.h)))
        self.meta.screen.blit(self.prompt, (self.x,
            self.y + self.h - self.prompt.get_height()))

        self.clock = Clock(7)
        self.cursor = False
        self.buffer = ''
        self.buffer_img = self.meta.font2.render('', True, YELLOW)

    def tick(self):
        if not self.last + 1 < len(self.history):
            if not self.focused:
                return

        else:
            for cmdline in self.history[self.last+1:]:
                color = YELLOW
                if cmdline[1] is None:
                    #color = (100, 155, 100)
                    color = (81, 81, 81)
                img = self.meta.font3.render(cmdline[0] if cmdline[0] else '',
                        True, color)
                self.renders.append(img)

                if cmdline[1] is not None:
                    #color = (200, 255, 81)
                    color = (100, 155, 100)
                    if isinstance(cmdline[1], Exception):
                        color = RED
                    img = self.meta.font2.render(f'{cmdline[1]}', True, color)
                    self.renders.append(img)

                self.last += 1

            pygame.draw.rect(self.meta.screen, (27, 0, 0),
                pygame.Rect((self.x, self.y), (self.w, self.h)))

            showing = 0
            height = self.prompt.get_height()
            self.meta.screen.blit(self.prompt, (self.x,
                self.y + self.h - height))

            for img in reversed(self.renders):
                if height + img.get_height() > self.h:
                    break

                height += img.get_height()
                self.meta.screen.blit(img, (self.x,
                    self.y + self.h - height))
                showing += 1

            self.renders = self.renders[-showing:]

        if self.focused:
            self.clock.tick()
            if self.clock.ready():
                self.cursor = not self.cursor
                self.draw_cursor()

    def kick(self, event):
        if event.type == pygame.KEYDOWN:
            self.log('chat key', event)

            self.clock.reset()
            prev_img = self.buffer_img

            self.cursor = False
            self.draw_cursor()

            if event.key == pygame.K_BACKSPACE:
                prev_img = self.buffer_img
                self.buffer = self.buffer[:-1]

            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.history.append((self.buffer, 'chat available soon'))
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

            self.buffer_img = self.meta.font2.render(self.buffer, True, YELLOW)

            if prev_img.get_width() > self.buffer_img.get_width():
                pygame.draw.rect(self.meta.screen, (27, 0, 0),
                    pygame.Rect((self.x + self.prompt.get_width() + \
                        self.buffer_img.get_width(),
                        self.y + self.h - self.prompt.get_height()),
                        (prev_img.get_width() - self.buffer_img.get_width(),
                        self.buffer_img.get_height())))

            else:
                diff = self.buffer_img.get_width() - prev_img.get_width()
                self.meta.screen.blit(self.buffer_img,
                    (self.x + self.prompt.get_width() + prev_img.get_width(),
                    self.y + self.h - self.buffer_img.get_height()),
                    pygame.Rect((self.buffer_img.get_width() - diff, 0),
                        (diff, self.buffer_img.get_height())))

    def draw_cursor(self):
        color = YELLOW if self.cursor else (27, 0, 0)
        pygame.draw.rect(self.meta.screen, color,
            pygame.Rect((self.x + self.prompt.get_width() + \
                    self.buffer_img.get_width(),
                self.y + self.h - self.prompt.get_height()),
                (3, self.prompt.get_height())))

    def focus(self):    
        super().focus()
        self.border(ORANGE)
        self.clock.reset()

    def unfocus(self):
        super().unfocus()
        self.border(BLACK)

        if self.cursor:
            self.cursor = False
            self.draw_cursor()

        self.clock.reset()

