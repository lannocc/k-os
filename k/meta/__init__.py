from k.ui import *
import k.db as kdb

import sys
import traceback
import os
from os.path import join
from datetime import datetime


MODES['M'] = 'meta.png'

MOD_DISABLE = [
    'chat',
#    'shadow',
]


class L:
    def __init__(self, k):
        self.init_start = datetime.now()
        self.k = k
        self.go = False
        self.metamode = False
        self.gaming = False

        if k.dip('0'):
            print('metaL 0FF')
            return

        self.log = Log(self)
        self.log('meta init')

        if self.k.square:
            MOD_DISABLE.append('shadow')

        # chaos take-over ;-)
        pygame.init()
        pygame.display.set_caption('k-os [L]')
        self.k.chaos = self.chaos
        self.kstatus = self.k.status
        self.k.status = self.status

        self.mouse = pygame.mouse.get_pos

        self.fullscreen = False
        if k.dip('9'):
            print('on cloud 9')
            self.fullscreen = True

        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.win = pygame.Surface((WIDTH, HEIGHT))
            self.size = self.screen.get_size()
            self.kx = int((self.size[0] - WIDTH) / 2)
            self.ky = int((self.size[1] - HEIGHT) / 2)

            pygame.draw.line(self.screen, WHITE,
                (self.kx + WIDTH-PWIDTH-1, 0),
                (self.kx + WIDTH-PWIDTH-1, self.ky-1))
            pygame.draw.line(self.screen, WHITE,
                (0, self.ky + HEIGHT-STATUS),
                (self.kx-1, self.ky + HEIGHT-STATUS))
            pygame.draw.line(self.screen, WHITE,
                (self.kx + WIDTH, self.ky + HEIGHT-STATUS),
                (self.size[0], self.ky + HEIGHT-STATUS))

            def get_win_mouse_pos():
                pos = self.mouse()
                pos = (pos[0] - self.kx, pos[1] - self.ky)
                return pos
            pygame.mouse.get_pos = get_win_mouse_pos

        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.win = self.screen
            self.size = (WIDTH, HEIGHT)
            self.kx = 0
            self.ky = 0

        self.init_stop = datetime.now()

    def chaos(self):
        self.log('meta chaos')
        self.k.init(self.win)
        self.init()

        startup = (datetime.now() - self.init_start).total_seconds()
        self.log(f'startup took {startup} seconds')

        while self.go:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.go = False
                        break

                    if not self.metamode:
                        opos = None
                        if self.fullscreen and hasattr(event, 'pos'):
                            if event.pos[0] >= self.kx \
                                    and event.pos[0] < self.kx + WIDTH \
                                    and event.pos[1] >= self.ky \
                                    and event.pos[1] < self.ky + HEIGHT:

                                opos = event.pos
                                event.pos = (opos[0]-self.kx, opos[1]-self.ky)

                        self.k.kick(event)

                        if opos:
                            event.pos = opos

                    self.kick(event)

                self.k.tick(not self.metamode)
                if self.fullscreen and self.k.imagine is None:
                    self.screen.blit(self.win, (self.kx, self.ky))

                self.tick()

                if self.k.imagine:
                    self.k.imagine.burn(self.screen, pygame.image.frombuffer,
                        (self.kx, self.ky) if self.fullscreen else None)

                pygame.display.update()

            except KeyboardInterrupt:
                #print('meta keyboard interrupt')
                self.go = False

            except Exception as e:
                self.go = False
                print('--- UNCAUGHT EXCEPTION ---')
                print(e)
                print(traceback.format_exc())
                print('--------------------------')

        self.k.kill()
        self.kill()

    def init(self):
        self.metamask = pygame.Surface((WIDTH, HEIGHT-STATUS))
        self.metamask.set_alpha(200)
        self.metamask.fill((9, 81, 42))
        #self.metamode_revbig = False

        self.log('meta font init')
        self.fonts = pygame.font.get_fonts()
        self.fontdef = pygame.font.get_default_font()
        self.font1 = pygame.font.SysFont(self.fontdef, 12)
        self.font2 = pygame.font.SysFont(self.fontdef, 15)
        self.font3 = pygame.font.SysFont(self.fontdef, 20)
        self.font4 = pygame.font.SysFont(self.fontdef, 27)
        self.font5 = pygame.font.SysFont(self.fontdef, 42)
        self.font6 = pygame.font.SysFont(self.fontdef, 66)

        self.log('meta mod init')
        self.mods = []
        self.meta = {}
        self.anyfocus = False
        print('metaLmods: ', end='')
        sys.stdout.flush()

        #for modfn in glob.glob(glob.escape(join('k', 'meta'))+os.sep+'*.py'):
        for modfn in sorted(os.listdir(join('k', 'meta'))):
            if modfn.startswith('.') or modfn.startswith('_'):
                continue

            #print(' .', end='')
            if modfn.endswith('.py'):
                modfn = modfn[:-3]

            if modfn in MOD_DISABLE:
                continue

            print(modfn, end='')
            sys.stdout.flush()
            idx = len(self.mods)

            try:
                #FIXME SECURITY (attack possible through filename)
                exec(f'from k.meta.{modfn} import Mod as KMod{idx}')
                exec(f'self.mods.append(KMod{idx}(self))')

                try:
                    mod = self.mods[-1]
                    mod.init()
                    self.meta[mod] = Meta()

                    print('/OK ', end='')
                    sys.stdout.flush()

                except Exception as e:
                    self.log('init fail', mod, e)
                    print('/FAIL(init) ', end='')
                    sys.stdout.flush()
                    self.mods = self.mods[:-1]

            except ModuleNotFoundError as e:
                self.log('mod name fail', modfn, e)
                print('/FAIL(module) ', end='')
                sys.stdout.flush()

            except SyntaxError as e:
                self.log('mod syntax fail', modfn, e)
                print('/FAIL(syntax) ', end='')
                sys.stdout.flush()

            except ImportError as e:
                self.log('mod import fail', modfn, e)
                print('/FAIL(class) ', end='')
                sys.stdout.flush()

            except Exception as e:
                self.log('mod general fail', modfn, e)
                print('/FAIL(unknown) ', end='')
                sys.stdout.flush()
        
        print(f'[{len(self.mods)} loaded]')

        self.init_stop = datetime.now()
        self.go = True

    def tick(self):
        self.log('meta tick')
        #print('~', end='')
        #sys.stdout.flush()

        for mod in self.mods:
            try:
                mod.tick()
            except Exception as e:
                self.log('mod tick fail', mod, e)

    def kick(self, event):
        self.log('meta kick', event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.metamode:
                    self.toggle_metamode()
                else:
                    self.go = False

            elif event.key == pygame.K_TAB:
                self.toggle_metamode()

            elif self.metamode:
                if event.key == pygame.K_SCROLLOCK:
                    if self.fullscreen:
                        self.k.player.toggle_size()
                    else:
                    #    self.metamode_revbig = not self.metamode_revbig
                        self.toggle_metamode()
                        self.k.player.toggle_size()

                elif self.gaming:
                    self.kick_mod(self.gaming, event)

                else:
                    for mod in self.mods:
                        if mod.focused:
                            self.kick_mod(mod, event)

        elif event.type == pygame.MOUSEMOTION:
            if self.metamode:
                if self.gaming:
                    self.kick_mod(self.gaming, event)

                else:
                    x = event.pos[0]
                    y = event.pos[1]

                    for mod in self.mods:
                        if self.is_mod_focus(mod, x, y):
                            if not mod.focused:
                                mod.focus()

                        elif mod.focused:
                            mod.unfocus()

                        self.kick_mod(mod, event)

            #else:
                #if x < self.kx or x >= self.kx + WIDTH \
                #        or y < self.ky or y >= self.ky + HEIGHT:

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x = event.pos[0]
            y = event.pos[1]

            if self.metamode:
                if self.gaming:
                    self.kick_mod(self.gaming, event)

                else:
                    for mod in self.mods:
                        if mod.focused:
                            self.kick_mod(mod, event)

            elif not self.is_k_focus(x, y):
                self.toggle_metamode(True)

                for mod in self.mods:
                    if self.is_mod_focus(mod, x, y):

                        if not mod.focused:
                            mod.focus()
                            self.kick_mod(mod, event)

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.metamode:
                if self.gaming:
                    self.kick_mod(self.gaming, event)

                else:
                    for mod in self.mods:
                        if mod.focused:
                            self.kick_mod(mod, event)

                x = event.pos[0]
                y = event.pos[1]

                if self.is_k_focus(x, y) and not self.anyfocus:
                    self.toggle_metamode(False)

    def kick_mod(self, mod, event):
        try:
            mod.kick(event)
            return True

        except Exception as e:
            self.log('mod kick fail', mod, e)
            return False

    def status(self, mode='M'):
        self.kstatus(mode)

        if self.fullscreen:
            self.screen.blit(self.win, (self.kx, self.ky))

        pygame.display.update()

    def is_k_focus(self, x, y):
        return False if x < self.kx or x >= self.kx + WIDTH \
            or y < self.ky or y >= self.ky + HEIGHT \
            else True

    def is_mod_focus(self, mod, x, y):
        return True if x >= mod.x and x < mod.x + mod.w \
            and y >= mod.y and y < mod.y + mod.h \
            else False

    def toggle_metamode(self, metamode=None):
        if (metamode == True and self.metamode) \
                or (metamode == False and not self.metamode):
            return

        self.metamode = not self.metamode
        if self.metamode:
            self.log('metamode on')
            pygame.display.set_caption('k-os [metaL]')
            pygame.mouse.set_cursor(*pygame.cursors.diamond)
            self.status('M')
            if not self.fullscreen:
                if self.k.player.big:
                    self.k.player.size_normal()
                    #self.metamode_revbig = True
            self.win.blit(self.metamask, (0, 0))
            x = self.mouse()[0]
            y = self.mouse()[1]
            for mod in self.mods:
                if self.is_mod_focus(mod, x, y):
                    mod.focus()
                mod.paint()
        else:
            self.log('metamode off')
            pygame.display.set_caption('k-os [L]')
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            self.status('N')
            self.set_game()
            for mod in self.mods:
                if mod.focused:
                    mod.unfocus()
                mod.paint()
            #if not self.fullscreen:
            #    if self.metamode_revbig:
            #        self.k.player.size_big()
            #        self.metamode_revbig = False

    def set_game(self, gaming=None):
        if self.gaming == gaming:
            return

        self.gaming = gaming
        if self.gaming:
            self.log('game start', gaming)
        else:
            self.log('game stop')

    def mod_focus(self, mod):
        self.meta[mod].focus = True
        self.anyfocus = True

    def mod_unfocus(self, mod):
        self.meta[mod].focus = False

        for meta in self.meta.values():
            try:
                if meta.focus:
                    return
            except AttributeError:
                pass

        self.anyfocus = False

    def shell(self):
        raise Exception('no shell mod enabled')

    def kill(self):
        self.log('meta kill')
        self.go = False

        for mod in self.mods:
            mod.kill()

        kdb.con.close()
        print('meta no mo')


class Log:
    def __init__(self, meta):
        self.meta = meta
        self.hits = []
        self.blocks = LOG_DISABLE
        self.hit('log startup')

    def __call__(self, *args, **kwargs):
        return self.hit(*args, **kwargs)

    def hit(self, txt, *args, **kwargs):
        if txt in self.blocks:
            return

        #print(txt)
        #for arg in args:
        #    print(arg)

        self.hits.append((datetime.now(), txt, *args, *kwargs))

    def block(self, txt):
        if txt in self.blocks:
            return

        self.blocks.append(txt)


class Mod:
    def __init__(self, meta, x=-1, y=-1, w=0, h=0):
        self.meta = meta
        self.log = meta.log
        self.log(f'mod init: {self}')

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.focused = False

    def init(self):
        pass

    def tick(self):
        pass

    def focus(self):
        self.meta.mod_focus(self)
        self.focused = True

    def unfocus(self):
        self.meta.mod_unfocus(self)
        self.focused = False

    def border(self, color):
        pygame.draw.rect(self.meta.screen, color,
            pygame.Rect((self.x - 3, self.y - 3), (self.w + 6, self.h + 6)),
            width=3)

    def kick(self, event):
        pass

    def paint(self):
        pass

    def kill(self):
        pass

