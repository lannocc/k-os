from k.ui import *
from ..obj.draw import Drawing, Selector

from abc import ABC, abstractmethod


class Tool(ABC):
    def __init__(self, ack):
        self.ack = ack

    @abstractmethod
    def pick(self, prev):
        pass

    def toggle(self):
        pass

    def selector(self):
        pass

    def constraints(self):
        pass

    def choice(self, c):
        pass

    def up(self):
        pass

    def down(self):
        pass

    def start(self, pos):
        pass

    def stop(self):
        pass

    @abstractmethod
    def use(self, pos, middle=False):
        pass


class Draws(Tool, ABC):
    def __init__(self, ack, choice=1, size=0):
        self.ack = ack
        self.size = size
        self.choice(choice)

    def choice(self, c):
        self.c = c
        self.color = self.ack.colors[c]

    def up(self):
        self.size += 1
        if self.size > WIDTH:
            self.size = WIDTH

    def down(self):
        self.size -= 1
        if self.size < 0:
            self.size = 0

    def draw_select(self, pos, middle_out, constrain=None):
        x = self.ack.start[0]
        y = self.ack.start[1]
        w = pos[0] - x
        h = pos[1] - y

        self.flip_x = False
        self.flip_y = False

        if w < 0:
            w = abs(w)
            x -= w
            self.flip_x = True

        if h < 0:
            h = abs(h)
            y -= h
            self.flip_y = True

        if middle_out:
            w *= 2
            h *= 2
            x = pos[0] if self.flip_x else pos[0] - w
            y = pos[1] if self.flip_y else pos[1] - h

        if constrain is None:
            constrain = self.ack.control

        if constrain:
            normal = max(w, h)
            if middle_out:
                if w < h:
                    x -= (h - w)//2
                elif h < w:
                    y -= (w - h)//2
            w = normal
            h = normal

        return self.ack.set_obj(
            Drawing((x, y), (w, h), self.color) \
                if not self.ack.select else \
                    Selector((x, y), (w, h))
        )

