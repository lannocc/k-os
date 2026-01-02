from k.ui import *
import k.storage as media
from . import Tool as Base, Draws


def divert(color, d=2):
    r = color[0]
    g = color[1]
    b = color[2]

    r += 256//d
    g += 256//d
    b += 256//d

    if r > 255: r -= 256
    if g > 255: g -= 256
    if b > 255: b -= 256

    return pygame.Color(r, g, b)


class Tool(Base):
    def __init__(self, ack):
        super().__init__(ack)

        self.c = 1

        w = WIDTH
        h = HEIGHT-STATUS-1

        self.palette = media.load_palette()

        if not self.palette:
            self.palette = pygame.Surface((w, h))

            s = w/6
            w -= 1
            h -= 1

            for y in range(h+1):
                for x in range(w+1):
                    m = 1 if y < h/2 else (h-y)/(h/2)    # main
                    o = 0 if y >= h/2 else (h/2-y)/(h/2) # other/boost

                    r =             1 if x <= 2*s \
                       else (3*s-x)/s if x <= 3*s \
                       else         0 if x <= 5*s \
                       else (x-5*s)/s
                    g =             0 if x <= s \
                       else   (x-s)/s if x <= 2*s \
                       else         1 if x <= 4*s \
                       else (5*s-x)/s if x <= 5*s \
                       else         0
                    b =       (s-x)/s if x <= s \
                       else         0 if x <= 3*s \
                       else (x-3*s)/s if x <= 4*s \
                       else         1

                    r = int(255*r*m)
                    g = int(255*g*m)
                    b = int(255*b*m)

                    if o > 0:
                        if r == 0:
                            m = min(g, b)
                            r = int(255*o)
                            if r > m: r = m

                        if g == 0:
                            m = min(r, b)
                            g = int(255*o)
                            if g > m: g = m

                        if b == 0:
                            m = min(r, g)
                            b = int(255*o)
                            if b > m: b = m

                    try:
                        color = (r, g, b)
                        #color = divert(divert(divert(color, 3), 3), 3)
                        self.palette.set_at((x, y), color)

                    except ValueError as e:
                        print(f' {x},{y} -> {r},{g},{b}')
                        raise e

            media.save_palette(self.palette)

        #for v in range(1,6):
        #    pygame.draw.line(self.palette, WHITE, (v*s, 0), (v*s, h))

    def pick(self, prev):
        self.prev = prev
        if isinstance(prev, Draws):
            self.choice(prev.c)
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        return self.palette

    def toggle(self):
        if self.prev:
            self.prev.choice(self.c)
        return self.prev

    def selector(self):
        if self.ack.select:
            self.ack.overlay = None

        else:
            self.ack.overlay = self.palette

    def choice(self, c):
        self.c = c

    def at(self, pos, own=True):
        color = self.palette.get_at(pos) if own \
           else self.ack.k.screen.get_at(pos) #self.ack.surf.get_at(pos)
        self.ack.colors[self.c] = color

        self.mouse = pygame.Surface((50, 50), depth=8)
        self.mouse.set_palette_at(0, divert(color))
        self.mouse.set_colorkey(0)

        self.mouse.set_palette_at(42, color)
        self.mouse.fill(42)

        self.mouse.set_palette_at(81, divert(divert(color, 3), 3))
        pygame.draw.circle(
            self.mouse, 81, (25, 25), 5)

        self.mouse.set_at((25, 25), 0)

        pygame.mouse.set_cursor(pygame.Cursor((25, 25), self.mouse))

    def start(self, pos):
        self.at(pos)
        return None

    def use(self, pos, middle):
        if middle:
            self.at(pos)

        elif self.ack.select:
            self.at(pos, False)

        return None

    def stop(self):
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        return self.palette

