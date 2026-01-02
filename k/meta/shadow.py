from k.ui import *
import k.meta


SW = int(PWIDTH / 2)
SH = int(PHEIGHT / 2)


class Mod(k.meta.Mod):
    def __init__(self, meta):
        super().__init__(meta)

        self.size_normal()
        #self.pos = None

    def toggle_size(self):
        if self.big:
            self.size_normal()
        else:
            self.size_big()

    def size_normal(self):
        self.x = self.meta.kx + WIDTH - PWIDTH
        self.y = self.meta.ky
        self.w = PWIDTH
        self.h = PHEIGHT
        self.recenter()
        self.big = False

    def size_big(self):
        self.x = self.meta.kx
        self.y = self.meta.ky
        self.w = WIDTH
        self.h = HEIGHT - STATUS
        self.recenter()
        self.big = True

    def recenter(self):
        self.cx = int(self.x + self.w/2)
        self.cy = int(self.y + self.h/2)

    def kick(self, event):
        #if self.focused and event.type == pygame.MOUSEMOTION:
        #    self.pos = event.pos

        #elif event.type == pygame.KEYDOWN and event.key == pygame.SCROLLOCK:
        #    self.toggle_size()
        pass

    def tick(self):
        #if self.meta.metamode and not self.focused:
        #    return
        #if not self.meta.fullscreen and not self.meta.metamode:
        #    return

        if self.meta.k.player.big != self.big:
            self.toggle_size()

        #pygame.draw.line(self.meta.screen, WHITE,
        #    (self.x, 0), (self.x + self.w, self.y))
        #pygame.draw.line(self.meta.screen, WHITE,
        #    (self.x + self.w, self.y), (self.meta.size[0], self.y + self.h))

        if (not self.meta.metamode and not self.meta.fullscreen) \
                or (self.meta.gaming and not self.meta.fullscreen):

            return

        pos = self.meta.mouse()

        x = pos[0] if self.focused else self.cx
        for y in range(self.y, self.y + self.h):
            color = self.meta.screen.get_at((x, y))

            if self.meta.fullscreen:
                pygame.draw.line(self.meta.screen, color,
                    (self.x + self.w, y), (self.meta.size[0], y))
            else:
                pygame.draw.line(self.meta.screen, color,
                    (self.x - SW, y), (self.x, y))

        y = pos[1] if self.focused else self.cy
        for x in range(self.x, self.x + self.w):
            color = self.meta.screen.get_at((x, y))

            if self.meta.fullscreen:
                pygame.draw.line(self.meta.screen, color,
                    (x, 0), (x, self.y))
            else:
                pygame.draw.line(self.meta.screen, color,
                    (x, self.y + PHEIGHT), (x, self.y + PHEIGHT + SH))

        if self.focused or not self.meta.anyfocus:
            if self.meta.metamode and not self.big:
                color = self.meta.screen.get_at((self.x, self.y))
                pygame.draw.rect(self.meta.screen, color, pygame.Rect(
                    (self.meta.kx, 0), (self.x - self.meta.kx, self.y)))

                color = self.meta.screen.get_at((self.meta.kx + WIDTH - 1,
                    self.meta.ky + PHEIGHT - 1))
                pygame.draw.rect(self.meta.screen, color, pygame.Rect(
                    (self.meta.kx + WIDTH, self.meta.ky + PHEIGHT),
                    (self.meta.kx, HEIGHT - PHEIGHT - STATUS)))

            #if self.big and self.h < HEIGHT - STATUS:
            #    gap = HEIGHT - STATUS - self.h
            #    factor = gap / 256
            #    for x in range(self.x, self.x + self.w):
            #        color = self.meta.screen.get_at((x, self.y + self.h - 1))
            #        for y in range(self.y + self.h,
            #                self.meta.ky + HEIGHT - STATUS):
            #            print(f'{x},{y}')
            #            #(gap - (y - self.y - self.h)) * factor
            #            self.meta.screen.set_at((x, y), color)

            if self.meta.metamode and self.meta.fullscreen and not self.big:
                for x in range(self.x, self.x + self.w):
                    color = self.meta.screen.get_at((x, self.y + self.h - 1))
                    pygame.draw.line(self.meta.screen, color,
                        (x, self.y + self.h),
                        (x, self.y + HEIGHT - STATUS - 1))

                for y in range(self.y, self.y + self.h):
                    color = self.meta.screen.get_at((self.x, y))
                    pygame.draw.line(self.meta.screen, color,
                        (self.meta.kx, y), (self.x - 1, y))

        if self.focused:
            pygame.draw.line(self.meta.screen, YELLOW,
                (pos[0], self.y), (pos[0], self.y + self.h))
            pygame.draw.line(self.meta.screen, YELLOW,
                (self.x, pos[1]), (self.x + self.w, pos[1]))

