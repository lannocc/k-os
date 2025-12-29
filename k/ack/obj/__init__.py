from k.ui import *

from abc import ABC


class Object(ABC):
    def __init__(self, pos=(0, 0), surf=None):
        self.pos = pos

        if surf is None:
            surf = pygame.Surface((WIDTH, HEIGHT-STATUS-1), pygame.SRCALPHA)

        elif not isinstance(surf, pygame.Surface):
            surf = pygame.Surface(surf, pygame.SRCALPHA)

        self.surf = surf

    def size(self):
        return self.surf.get_size()


class Null(Object):
    def __init__(self):
        super().__init__((-1, -1), pygame.Surface((0, 0), depth=8))


class Image(Object):
    def __init__(self, surf, pos=(0, 0)):
        super().__init__(pos, surf)

