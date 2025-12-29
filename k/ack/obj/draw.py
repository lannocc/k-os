from k.ui import *
from . import Object

from abc import ABC
from math import ceil


class Drawable(Object, ABC):
    IDX_KEY = 0
    IDX_COLOR = 9

    def __init__(self, pos, size):
        try:
            super().__init__(pos, pygame.Surface(size, depth=8))

        except pygame.error as e:
            print(f'size: {size}')
            raise e

        self.surf.set_colorkey(self.IDX_KEY)
        self.surf.fill(self.IDX_KEY)

    def key(self, color):
        self.surf.set_palette_at(self.IDX_KEY, color)

    def rect(self, border=0, rounded=False):
        size = self.size()

        pygame.draw.rect(
            self.surf, self.IDX_COLOR, pygame.Rect((0, 0), size),
            border // 2 if rounded else border,
            border // 2 if rounded else 0)

        return self

    def ellipse(self, border=0):
        size = self.size()

        pygame.draw.ellipse(
            self.surf, self.IDX_COLOR, pygame.Rect((0, 0), size), border)

        return self

    def blit(self, obj):
        self.surf.blit(obj.surf, (0, 0))
        return self

    def blot(self, pos, size, rounded=False):
        if rounded:
            pygame.draw.circle(
                self.surf, self.IDX_COLOR, pos, ceil(size/2))

        else:
            pygame.draw.rect(
                self.surf, self.IDX_COLOR, pygame.Rect(
                    (pos[0] - round(size/2), pos[1] - round(size/2)),
                    (size, size)))

        return self

    def line(self, pos_from, pos_to, size):
        #print(f'line: {pos_from} -> {pos_to}')
        pygame.draw.line(
            self.surf, self.IDX_COLOR, pos_from, pos_to, size)

        return self

class Drawing(Drawable):
    def __init__(self, pos, size, color):
        super().__init__(pos, size)

        self.color = color
        self.key(BLACK if color != BLACK else WHITE)
        self.surf.set_palette_at(self.IDX_COLOR, self.color)


class Selector(Drawable):
    FPS = 27
    STEP = 9
    MIN = 42
    MAX = 128

    def __init__(self, pos, size):
        super().__init__(pos, size)

        self.alpha(self.MAX)

    def color(self, color):
        self.surf.set_palette_at(self.IDX_COLOR, color)

    def alpha(self, alpha):
        self.surf.set_alpha(alpha)

