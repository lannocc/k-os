from k.ui import *
import k.storage as media
from k.player.ui import PRECT, VPRECT
from .tool.color import Tool as Color
from .tool.wiggle import Tool as Wiggle
from .tool.rect import Tool as Rect
from .tool.ellipse import Tool as Ellipse
from .tool.adjust import Tool as Adjust
from .obj import Null, Image
from .obj.draw import Selector

from datetime import datetime
import random


class Blackboard:
    def __init__(self, k):
        self.k = k

        self.back_black = pygame.Surface((WIDTH, HEIGHT-STATUS-1))
        self.back_black.fill(BLACK)
        self.back_white = pygame.Surface((WIDTH, HEIGHT-STATUS-1))
        self.back_white.fill(WHITE)
        self.back = self.back_black
        self.surf = pygame.Surface((WIDTH, HEIGHT-STATUS-1), pygame.SRCALPHA)

        self.objects = [ ]
        self.selects = [ ]
        self.selecting = None
        self.overlay = None

        if self.k.shifting and self.k.player.players:
            image = self.surf.copy() # transparency blank
            images = [ ]
            for player in self.k.player.players:
                try:
                    if player.panel_chaos.image:
                        images.append(player.panel_chaos.image)
                except AttributeError:
                    pass
            if images:
                ri = images[random.randint(0, len(images)-1)]
                if self.k.control:
                    image.blit(ri, (0, 0), pygame.Rect(
                        (0, 0), (WIDTH - PWIDTH, HEIGHT - STATUS - 1)))
                    image.blit(ri, (WIDTH - PWIDTH, VPRECT[3]), pygame.Rect(
                        (WIDTH - PWIDTH, VPRECT[3]),
                        (PWIDTH, HEIGHT - STATUS - 1 - VPRECT[3])))
                else:
                    image.blit(ri, (0, 0))
            image.blit(self.k.screen.copy(), (0, PRECT[3]), VPRECT)
            self.add_obj(Image(image))

        self.colors = [
            None, # special "diverting" color
            GRAY,
            CYAN,
            MAGENTA,
            YELLOW,
            RED,
            GREEN,
            BLUE,
            WHITE,
            BLACK,
        ]

        self.tools = {
            pygame.K_BACKQUOTE: Color(self),
            pygame.K_w: Wiggle(self),
            pygame.K_r: Rect(self),
            pygame.K_e: Ellipse(self),
            pygame.K_a: Adjust(self),
        }
        self.tool = None
        self.tooling = None
        self.tool_pick(self.tools[pygame.K_w])

        self.start = None
        self.pos = None

        self.control = False
        self.select = False

        self.paint_back()

    def add_obj(self, obj):
        self.objects.append(obj)

        if isinstance(obj, Selector):
            if not self.selects:
                self.selecting = [Clock(Selector.FPS), Selector.MAX, True, True]
            self.selects.append(len(self.objects) - 1)

            if self.back is self.back_black:
                obj.key(BLACK)
                obj.color(WHITE)
            else:
                obj.key(WHITE)
                obj.color(BLACK)

        return obj

    def del_obj(self):
        if not self.objects:
            return None

        obj = self.objects.pop()
        if isinstance(obj, Selector):
            self.selects.pop()
            if not self.selects:
                self.selecting = None

        return obj

    def set_obj(self, obj):
        self.del_obj()
        return self.add_obj(obj)

    def obj(self):
        if not self.objects:
            return None

        return self.objects[-1]

    def tool_pick(self, tool, cancel=False):
        print(f'tool_pick: {tool}')
        if self.tooling:
            if self.tool_stop() and cancel:
                self.del_obj()

        prev_tool = self.tool
        self.tool = tool
        prev_overlay = self.overlay
        self.overlay = tool.pick(prev_tool)

        if self.overlay:
            self.paint_overlay()

        elif prev_overlay:
            self.paint_back()
            self.paint_surf()

        if self.tooling:
            self.tool.start(self.start if cancel else self.pos)

    def tool_start(self, pos):
        self.start = pos
        self.last_obj = self.obj()
        self.tool.start(self.start)

    def tool_stop(self):
        self.tool.stop()
        obj = self.obj()
        if not obj or obj is self.last_obj:
            return False

        size = obj.size()
        if isinstance(obj, Null) or size[0] < 1 or size[1] < 1:
            self.del_obj()
            return False

        else:
            return True

    def tool_at(self, pos):
        self.pos = pos

        paint = self.tool.use(self.pos, self.tooling == pygame.BUTTON_MIDDLE)

        if paint:
            self.paint() #FIXME

        else:
            if self.overlay:
                self.paint_back()
                self.paint_surf()

        #elif area is not None:
        #    self.paint_obj((area[0], area[1]), area)
        #    self.paint_surf((area[0], area[1]), area)

        return paint

    def paint(self):
        #print('ack full paint')
        if self.overlay:
            self.paint_overlay()

        else:
            self.paint_back()
            self.surf = pygame.Surface((WIDTH, HEIGHT-STATUS-1),
                pygame.SRCALPHA)
            self.paint_objects()
            self.paint_surf()

    def paint_back(self):
        self.k.blit(self.back, (0, 0))

    def paint_objects(self):
        for obj in self.objects:
            show = True
            if isinstance(obj, Null):
                show = False
            elif isinstance(obj, Selector):
                show = self.select or self.selecting[3]

            if show:
                # FIXME: use blits() here?
                self.surf.blit(obj.surf, obj.pos)

    #def paint_obj(self, pos=None, area=None):
    #    self.surf.blit(self.objects[-1][0], pos if pos else (0, 0), area)

    def paint_surf(self, pos=None, area=None):
    #    #print(f'paint_surf: {pos} -> {area}')
        self.k.blit(self.surf, pos if pos else (0, 0), area)

    #def paint_surf(self, area=None):
    #    self.k.blit(self.surf, (0, 0), area)

    def paint_overlay(self):
        self.k.blit(self.overlay, (0, 0))

    def tick(self):
        if self.k.player.is_playing(True):
            self.paint_surf((PRECT[0], PRECT[1]), PRECT)

        #if not self.tooling and self.objects:
        #    for obj in self.objects:
        #        obj.surf.set_palette_at(9, CYAN)

        if not self.tooling and self.selecting and self.selecting[3]:
            clock = self.selecting[0]
            clock.tick()

            if clock.ready():
                val = self.selecting[1]
                rev = self.selecting[2]

                if rev:
                    val -= Selector.STEP
                    if val < Selector.MIN:
                        val = Selector.MIN
                        rev = False

                else:
                    val += Selector.STEP
                    if val > Selector.MAX:
                        val = Selector.MAX
                        rev = True

                self.selecting[1] = val
                self.selecting[2] = rev

                for idx in self.selects:
                    self.objects[idx].alpha(val)

            self.paint()

    def kick(self, event):
        #print(f'ack kick: {event}')

        if event.type == pygame.WINDOWFOCUSGAINED \
                or event.type == pygame.WINDOWEXPOSED:
            self.paint()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT \
                    or event.button == pygame.BUTTON_MIDDLE:

                if not self.tooling:
                    self.tooling = event.button
                    self.tool_start(event.pos)
                    self.tool_at(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == self.tooling:
                self.tool_stop()
                self.tooling = None

                if self.overlay:
                    self.paint_overlay()

                else:
                    self.paint()

            elif event.button == pygame.BUTTON_WHEELUP:
                self.tool.up()
                if self.tooling:
                    self.tool_at(event.pos)

            elif event.button == pygame.BUTTON_WHEELDOWN:
                self.tool.down()
                if self.tooling:
                    self.tool_at(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.tooling:
                self.tool_at(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                self.control = True
                self.tool.constraints()
                if self.tooling:
                    self.tool_at(self.pos)

            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.select = True
                self.tool.selector()
                paint = True
                if self.tooling:
                    if self.tool_at(self.pos):
                        paint = False
                if paint:
                    self.paint()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                self.control = False
                self.tool.constraints()
                if self.tooling:
                    self.tool_at(self.pos)

            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.select = False
                self.tool.selector()
                paint = True
                if self.tooling:
                    if self.tool_at(self.pos):
                        paint = False
                if paint:
                    self.paint()

            elif event.key in self.tools:
                tool = self.tools[event.key]

                if tool is self.tool:
                    tool = tool.toggle()

                    if tool:
                        self.tool_pick(tool)

                    if self.tooling:
                        self.tool_at(self.pos)

                else:
                    self.tool_pick(tool, True)

                    if self.tooling:
                        self.tool_at(self.pos)

            elif event.unicode >= '1' and event.unicode <= '9':
                self.tool.choice(1 + ord(event.unicode) - ord('1'))
                if self.tooling:
                    self.tool_at(self.pos)

            #elif event.key == pygame.K_0:
            #    self.tool.choice(0)
            #    if self.tooling:
            #        self.tool_at(self.pos)

            elif event.key == pygame.K_b:
                if self.back is self.back_black:
                    self.back = self.back_white
                    skey = WHITE
                    scolor = BLACK

                else:
                    self.back = self.back_black
                    skey = BLACK
                    scolor = WHITE

                for idx in self.selects:
                    obj = self.objects[idx]
                    obj.key(skey)
                    obj.color(scolor)

                self.paint()

            elif event.key == pygame.K_SPACE:
                if self.selecting:
                    self.selecting[3] = not self.selecting[3]
                    self.paint()

            elif event.key == pygame.K_d:
                if self.objects:
                    self.del_obj()
                    self.paint()

            elif event.key == pygame.K_s:
                name = file_date_time(datetime.now())
                print(f'saving: {name}')

                media.save_ack_image(self.surf, name)

                #FIXME: use subsurface here instead:
                screen = pygame.Surface((WIDTH, HEIGHT-STATUS-1))
                screen.blit(self.k.screen, (0, 0))
                media.save_ack_image(screen, f'{name}_combined')

            elif event.key == pygame.K_c:
                obj = self.obj()
                if obj:
                    #with BytesIO() as io:
                    #    pygame.image.save(obj[0], io, 'png')
                    #    try:
                    #        pygame.scrap.put('image/png', io.getvalue())
                    #
                    #    except pygame.error:
                    #        fn = media.clipboard(io.getvalue())
                    #        pygame.scrap.put('text/plain;charset=utf-8',
                    #            bytes(f'file://{fn}', 'UTF-8'))

                    media.put_clipboard_image(obj.surf)

            elif event.key == pygame.K_v:
                print('clipboard contents:')
                #for mtype in pygame.scrap.get_types():
                #    print(f'   {mtype}')
                #    if 'text' in mtype:
                #        print(f'      {pygame.scrap.get(mtype)}')

                surf = media.get_clipboard_image()
                if surf is not None:
                    self.add_obj(Image(surf))
                    self.paint()

    def kill(self):
        pass

