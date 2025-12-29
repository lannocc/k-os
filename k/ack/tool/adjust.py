from k.ui import *
from . import Tool as Base


class Tool(Base):
    def __init__(self, ack):
        super().__init__(ack)

    def pick(self, prev):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def start(self, pos):
        obj = self.ack.obj()
        if not obj: return

        self.pos = obj.pos

    def use(self, pos, middle):
        obj = self.ack.obj()
        if not obj: return

        start = self.ack.start

        obj.pos = (
            pos[0] - start[0] + self.pos[0],
            pos[1] - start[1] + self.pos[1]
        )

        #return pygame.Rect((0, 0), (WIDTH, HEIGHT-STATUS-1)) #FIXME
        return obj

