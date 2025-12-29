from k.ui import *
import k.storage as media
from . import Draws
from .color import divert
from ..obj import Null
from ..obj.draw import Drawing, Selector


class Tool(Draws):
    def __init__(self, ack):
        super().__init__(ack, size=4)

        self.rounded = True

    def cursor(self):
        self.mouse = media.get_gfx('wiggle.gif')
        back = self.ack.back.get_at((9, 9))
        self.mouse.set_palette_at(0, divert(divert(back, 3), 3))
        self.mouse.set_palette_at(1, divert(back, 3))
        self.mouse.set_colorkey(1)
        self.mouse.set_palette_at(2, divert(self.color))
        self.mouse.set_palette_at(3, self.color)

        pygame.mouse.set_cursor(pygame.Cursor((13, 13), self.mouse))

    def pick(self, prev):
        #pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        self.cursor()

    def toggle(self):
        self.rounded = not self.rounded

    def selector(self):
        if self.ack.tooling:
            obj = self.ack.obj()
            size = obj.size()

            return self.ack.set_obj(
                Drawing(obj.pos, size, self.color) \
                    if not self.ack.select else \
                        Selector(obj.pos, size)

            ).blit(obj)

    def constraints(self):
        if self.ack.tooling:
            if self.ack.control:
                self.ack.add_obj(Null())

            else:
                size = (WIDTH, HEIGHT-STATUS-1)
                self.ack.add_obj(
                    Drawing((0, 0), size, self.color) \
                        if not self.ack.select else \
                            Selector((0, 0), size)

                )

    def choice(self, c):
        super().choice(c)
        self.cursor()

    def down(self):
        super().down()
        if self.size < 1:
            self.size = 1

    def start(self, pos):
        self.constraints()
        if not self.ack.control:
            self.ack.obj().blot(pos, self.size, self.rounded)

    def use(self, pos, middle=False):
        if pos != self.ack.start:
            if self.ack.control:
                obj = self.draw_select(pos, middle, False)
                size = obj.size()
                obj.line(
                    (size[0] if self.flip_x else 0,
                     size[1] if self.flip_y else 0),
                    (size[0] if not self.flip_x else 0,
                     size[1] if not self.flip_y else 0),
                    self.size)

            else:
                obj = self.ack.obj()
                obj.line(self.ack.start, pos, self.size)
                self.ack.start = pos

            return obj

    def stop(self):
        if self.ack.pos != self.ack.start:
            self.ack.obj().blot(self.ack.pos, self.size, self.rounded)

