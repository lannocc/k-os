from k.ui import *
import k.meta
from k.meta.shadow import SW, SH
import k.cmd

import random


PPX = 10
PPY = 10
FOCUS = (42, 27, 9)
EMPTY = (0, 27, 27)

STYLES = [
    (RED, 1),
    (GREEN, 2)
]


class Mod(k.meta.Mod):
    def __init__(self, meta):
        if meta.fullscreen:
            super().__init__(meta, 0, meta.ky, meta.kx, HEIGHT - STATUS)
        else:
            super().__init__(meta, 0, SH, WIDTH - PWIDTH - SW, PHEIGHT)

        self.go = False

    def init(self):
        self.game = None

        self.clk_game = Clock(3)
        self.clk_fold = None
        self.clk_drop = None

        self.paint()

    def tick(self):
        if self.meta.fullscreen and not self.meta.metamode:
            return
        if not self.clk_fold and (not self.go or not self.focused):
            return

        if self.clk_fold:
            self.clk_fold.tick()
            if self.clk_fold.ready():
                #self.log('tetrisk folding', self.clk_fold.step)

                if self.clk_fold.out:
                    if self.clk_fold.step >= self.y:
                        self.clk_fold = None
                    else:
                        self.clk_fold.step += 1
                else:
                    if self.clk_fold.step <= 0:
                        self.clk_fold = None
                    else:
                        self.clk_fold.step -= 1

                self.paint_folding()

        if self.clk_drop:
            self.clk_drop.tick()
            if self.clk_drop.ready():
                if not self.game.down():
                    self.clk_drop = None
                self.paint_updates()

        self.clk_game.tick()
        if not self.game or not self.clk_game.ready():
            return

        self.log('tetrisk tick')
        self.game.next()
        self.paint_updates()
        #self.paint_grid()

        #self.paint_primer()
        #self.paint_gridlines()

    def kick(self, event):
        #if event.type == pygame.MOUSEBUTTONDOWN:
        #    if self.focused:
        #        if self.go:
        #            self.stop()
        #        else:
        #            self.start()

        if event.type == pygame.MOUSEBUTTONUP:
            if self.focused:
                if self.go:
                    #self.stop()
                    self.meta.set_game(None)

                else:
                    self.start()

            #if self.meta.gaming == self \
            #        and not self.meta.is_mod_focus(self,
            #                     event.pos[0], event.pos[1]):
            #    self.stop()

        elif event.type == pygame.KEYDOWN:
            self.log('tetrisk key', event)

            #self.clock.reset()
            #prev_img = self.buffer_img

            if event.key == pygame.K_DELETE:
                self.stop()

            elif self.game:
                if event.key == pygame.K_END:
                    if self.clk_drop:
                        self.clk_drop = None
                    else:
                        self.clk_drop = Clock(27)

                elif not self.clk_drop:
                    if event.key == pygame.K_DOWN:
                        self.game.down()
                        self.paint_updates()

                    elif event.key == pygame.K_RIGHT:
                        self.game.right()
                        self.paint_updates()

                    elif event.key == pygame.K_LEFT:
                        self.game.left()
                        self.paint_updates()

                    elif event.key == pygame.K_UP:
                        self.game.up()
                        self.paint_updates()

    def start(self):
        self.meta.set_game(self)
        self.go = True

        if self.clk_fold:
            self.clk_fold.fps = 45
        else:
            self.clk_fold = Clock(45)
            self.clk_fold.step = 0
        self.clk_fold.out = True

        w = int(self.w / PPX)
        h = int(self.h / PPY)
        self.log(f'tetrisk starting {w}x{h} game grid')
        self.paint_primer()

        self.game = Game(w, h)

    def stop(self):
        self.go = False
        self.meta.set_game(None)
        #self.unfocus()

        if self.clk_fold:
            self.clk_fold.fps = 100
        else:
            self.clk_fold = Clock(100)
            self.clk_fold.step = self.y
        self.clk_fold.out = False

    def paint(self, gridlines=False):
        self.paint_primer()
        self.paint_folding()
        self.paint_grid()
        if gridlines:
            self.paint_gridlines()

    def paint_primer(self):
        pygame.draw.rect(self.meta.screen,
            FOCUS if self.focused else EMPTY,
            pygame.Rect((self.x, self.y), (self.w, self.h)))

    def paint_folding(self):
        if not self.clk_fold and not self.go:
            return

        color = self.meta.screen.get_at((self.x, self.y))
        gap = self.y - self.clk_fold.step if self.clk_fold else 0
        #self.log('tetrisk folding paint', color, gap)

        for y in range(gap, self.y):
            scale = (y - gap) / (self.y - gap)
            c = pygame.Color(int(scale * color[0]),
                             int(scale * color[1]),
                             int(scale * color[2]))
            pygame.draw.line(self.meta.screen, c,
                (self.x, y), (self.x + self.w - 1, y))

    def paint_gridlines(self):
        if not self.game:
            return

        for gy in range(len(self.game.grid)):
            row = self.game.grid[gy]
            pygame.draw.line(self.meta.screen, WHITE,
                (0, self.y + PPY*(gy+1)),
                (PPX*len(row), self.y + PPY*(gy+1)))

            for gx in range(len(row)):
                pygame.draw.line(self.meta.screen, WHITE,
                    (PPX*(gx+1), self.y + PPY*gy),
                    (PPX*(gx+1), self.y + PPY*(gy+1)))

    def paint_grid(self):
        if not self.game:
            return

        for y in range(len(self.game.grid)):
            row = self.game.grid[y]
            for x in range(len(row)):
                self.paint_tile(y, x)

    def paint_tile(self, y, x):
        color = self.game.grid[y][x]
        if not color:
            color = FOCUS if self.focused else EMPTY
        pygame.draw.rect(self.meta.screen, color, pygame.Rect(
            (PPX*x, self.y + PPY*y), (PPX, PPY)))

    def paint_updates(self):
        if not self.game or not self.game.updates:
            return

        for y, x in self.game.updates:
            self.paint_tile(y, x)

        self.game.updates = []

    def focus(self):    
        super().focus()
        self.paint(False)
        #self.clock.reset()

    def unfocus(self):
        super().unfocus()
        self.paint(True)
        #self.clock.reset()


class Game():
    def __init__(self, w, h):
        self.grid = [[None for x in range(w)] for y in range(h)]
        self.shape = None
        self.updates = []

    def next(self):
        if not self.shape:
            self.shape = Shape(self)

        self.down()

    def set(self, y, x, color):
        if y < 0 or y >= len(self.grid):
            return False

        row = self.grid[y]
        if x < 0 or x >= len(row):
            return False

        if row[x] != color:
            row[x] = color
            self.updates.append((y, x))

        return True

    def clear(self, y, x):
        return self.set(y, x, None)

    def crash(self, y, x):
        if y < 0 or y >= len(self.grid):
            return True

        row = self.grid[y]
        if x < 0 or x >= len(row):
            return True

        if row[x]:
            return True

        return False

    def down(self):
        if not self.shape:
            return None

        if not self.shape.move_down():
            self.shape = None
            return False

        return True

    def right(self):
        if not self.shape:
            return None

        return self.shape.move_right()

    def left(self):
        if not self.shape:
            return None

        return self.shape.move_left()

    def up(self):
        if not self.shape:
            return None

        return self.shape.spin()


class Shape():
    def __init__(self, game):
        self.game = game
        self.y = -1
        self.x = random.randint(0, len(game.grid[0])-1)
        self.style = random.randint(0, len(STYLES)-1)
        self.rotation = random.randint(0, len(STYLES[self.style])-1)

    def move_down(self):
        g = self.game
        y = self.y
        x = self.x
        r = self.rotation
        c = STYLES[self.style][0]
        t = STYLES[self.style][1]

        if self.style == 0:
            if g.crash(y+1, x) or g.crash(y+1, x+1):
                return False

            g.clear(y-1, x)
            g.clear(y-1, x+1)
            g.set(y+1, x, c)
            g.set(y+1, x+1, c)

        elif self.style == 1:
            if g.crash(y+1, x):
                return False
            g.set(y+1, x, c)

            if r % t == 0:
                g.clear(y-3, x)

            elif r % t == 1:
                for b in range(1, 4):
                    if g.crash(y+1, x+b):
                        return False

                g.clear(y, x)
                for b in range(1, 4):
                    g.clear(y, x+b)
                    g.set(y+1, x+b, c)

        else:
            self.log(Exception('tetrisk unsupported style'),
                     'move_down', self.style)
            return

        self.y += 1
        return True

    def move_right(self):
        g = self.game
        y = self.y
        x = self.x
        r = self.rotation
        c = STYLES[self.style][0]
        t = STYLES[self.style][1]

        if self.style == 0:
            if g.crash(y, x+2) or g.crash(y-1, x+2):
                return False

            g.clear(y, x)
            g.clear(y-1, x)
            g.set(y, x+2, c)
            g.set(y-1, x+2, c)

        elif self.style == 1:
            if r % t == 0:
                for b in range(4):
                    if g.crash(y-b, x+1):
                        return False

                for b in range(4):
                    g.clear(y-b, x)
                    g.set(y-b, x+1, c)

            elif r % t == 1:
                if g.crash(y, x+4):
                    return False

                g.clear(y, x)
                g.set(y, x+4, c)

        self.x += 1
        return True

    def move_left(self):
        g = self.game
        y = self.y
        x = self.x
        r = self.rotation
        c = STYLES[self.style][0]
        t = STYLES[self.style][1]

        if self.style == 0:
            if g.crash(y, x-1) or g.crash(y-1, x-1):
                return False

            g.clear(y, x+1)
            g.clear(y-1, x+1)
            g.set(y, x-1, c)
            g.set(y-1, x-1, c)

        elif self.style == 1:
            if r % t == 0:
                for b in range(4):
                    if g.crash(y-b, x-1):
                        return False

                for b in range(4):
                    g.clear(y-b, x)
                    g.set(y-b, x-1, c)

            elif r % t == 1:
                if g.crash(y, x-1):
                    return False

                g.clear(y, x+3)
                g.set(y, x-1, c)

        self.x -= 1
        return True

    def spin(self):
        g = self.game
        y = self.y
        x = self.x
        r = self.rotation
        c = STYLES[self.style][0]
        t = STYLES[self.style][1]

        if self.style == 0:
            pass

        elif self.style == 1:
            if r % t == 0:
                if g.crash(y, x+1) or g.crash(y, x+2) or g.crash(y, x+3):
                    return False
                g.clear(y-1, x)
                g.clear(y-2, x)
                g.clear(y-3, x)
                g.set(y, x+1, c)
                g.set(y, x+2, c)
                g.set(y, x+3, c)

            elif r % t == 1:
                if g.crash(y-1, x) or g.crash(y-2, x) or g.crash(y-3, x):
                    return False
                g.clear(y, x+1)
                g.clear(y, x+2)
                g.clear(y, x+3)
                g.set(y-1, x, c)
                g.set(y-2, x, c)
                g.set(y-3, x, c)
 
        self.rotation += 1
        return True

