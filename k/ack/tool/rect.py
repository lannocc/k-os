from k.ui import *
import k.storage as media
from . import Draws
from .color import divert
from ..obj import Null


class Tool(Draws):
    def __init__(self, ack):
        super().__init__(ack)

        self.rounded = False

    def cursor(self):
        self.mouse = media.get_gfx('rect_' \
            + ('normal' if self.size > 0 else 'full') + '.gif')
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

    def choice(self, c):
        super().choice(c)
        self.cursor()

    def up(self):
        mouse = (self.size == 0)
        super().up()
        if mouse:
            self.cursor()

    def down(self):
        mouse = (self.size > 0)
        super().down()
        if mouse and self.size == 0:
            self.cursor()

    def start(self, pos):
        self.ack.add_obj(Null())

    def use(self, pos, middle=False):
        return self.draw_select(
            pos, middle

        ).rect(self.size, self.rounded)

