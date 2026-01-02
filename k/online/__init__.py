from k.ui import *
import k.storage as media

import sys
import os
from os.path import join
import traceback


KON_W = 244
KON_H = 20
KON_X = WIDTH - KON_W - 5
#KON_Y = HEIGHT - 27
KON_Y = 5


class Panel(KPanel):
    def __init__(self, k, anchors):
        super().__init__(k, anchors)

        self.img_msg = pygame_gui.elements.UIImage(
            image_surface=media.get_gfx('message.png'),
            manager=k.sui,
            relative_rect=pygame.Rect((KON_X, KON_Y), (KON_W, KON_H)))
        self.img_msg.hide()

        self.img_offline = pygame_gui.elements.UIImage(
            image_surface=media.get_gfx('offline.png'),
            manager=k.sui,
            relative_rect=pygame.Rect((KON_X, KON_Y), (KON_W, KON_H)))

        self.img_connected = pygame_gui.elements.UIImage(
            image_surface=media.get_gfx('connected.png'),
            manager=k.sui,
            relative_rect=pygame.Rect((KON_X, KON_Y), (KON_W, KON_H)))
        self.img_connected.hide()

        self.img_live = pygame_gui.elements.UIImage(
            image_surface=media.get_gfx('live.png'),
            manager=k.sui,
            relative_rect=pygame.Rect((KON_X, KON_Y), (KON_W, KON_H)))
        self.img_live.hide()

        self.lbl_connect = pygame_gui.elements.UILabel(
            text='Online handlers installed (click to connect):',
            manager=k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=SPACER)

        self.mods = []
        self.btn_mods = []
        above = self.lbl_connect
        print('online mods: ', end='')
        sys.stdout.flush()

        for modfn in sorted(os.listdir(join('k', 'online'))):
            if modfn.startswith('.') or modfn.startswith('_'):
                continue

            if modfn.endswith('.py'):
                modfn = modfn[:-3]

            print(modfn, end='')
            sys.stdout.flush()
            idx = len(self.mods)

            try:
                #FIXME SECURITY (attack possible through filename)
                exec(f'from k.online.{modfn} import Mod as KOnline{idx}')
                exec(f'self.mods.append(KOnline{idx}(self.k))')

                try:
                    mod = self.mods[-1]
                    mod.init()

                    btn = pygame_gui.elements.UIButton(
                        text=modfn,
                        manager=k.gui,
                        container=self.container,
                        anchors=target(above, 'top'),
                        relative_rect=SPACER)
                    self.btn_mods.append((btn, mod))
                    above = btn
                    
                    print('/OK ', end='')
                    sys.stdout.flush()

                except Exception as e:
                    print('/FAIL(init) ', end='')
                    sys.stdout.flush()
                    self.mods = self.mods[:-1]

            except ModuleNotFoundError as e:
                print('/FAIL(module) ', end='')
                sys.stdout.flush()

            except SyntaxError as e:
                print('/FAIL(syntax) ', end='')
                sys.stdout.flush()

            except ImportError as e:
                print('/FAIL(class) ', end='')

            except Exception as e:
                print('/FAIL(unknown) ', end='')
                sys.stdout.flush()
                raise e

        print(f'[{len(self.mods)} loaded]')

        self.handler = None

    def go_offline(self, logout=True):
        if logout and self.handler and self.handler is not True:
            self.handler.logout()

        self.handler = None

        self.img_msg.hide()
        self.img_live.hide()
        self.img_connected.hide()
        self.img_offline.show()

        #for btn, mod in self.btn_mods:
        #    btn.enable()

        if self.k.cur_panel == self.k.panel_online:
            self.k.panel_swap(self.k.btn_home, self.k.panel_home)

        else:
            self.k.panel_swap(None, self.k.panel_online)

        self.k.status()

    def go_online(self, mod=None):
        self.img_msg.hide()
        self.img_offline.hide()
        self.img_live.hide()

        if mod:
            if mod.login():
                self.handler = mod
                self.img_connected.show()

            else:
                print(f'LOGIN FAILED: {mod}')
                self.k.status('E')
                self.img_offline.show()
        else:
            self.img_connected.show()
            self.handler = False # dummy handler

        self.k.status()

    def go_live(self):
        if not self.handler:
            self.handler = True # dummy handler

        self.img_msg.hide()
        self.img_offline.hide()
        self.img_connected.hide()

        print('COMING SOON')
        self.img_live.show()
        self.k.status()

    def toggle(self):
        if self.handler:
            self.go_offline()

        elif self.handler is None:
            self.go_online()

        else:
            self.go_live()

    def click(self, element, target=None):
        for btn, mod in self.btn_mods:
            if btn == element:
                self.go_offline()
                #btn.disable()
                self.go_online(mod)
                self.k.panel_swap(None, mod.panel)

    def mouse_button_down(self, event):
        x = event.pos[0]
        y = event.pos[1]

        if x >= KON_X and x < KON_X + KON_W \
                and y >= KON_Y + (HEIGHT - STATUS) \
                and y < KON_Y + (HEIGHT - STATUS) + KON_H:

            if self.handler:
                #self.go_offline()
                if self.k.cur_panel == self.handler.panel:
                    self.go_offline()
                else:
                    self.k.panel_swap(None, self.handler.panel)
            else:
                self.k.panel_swap(None, self.k.panel_online)

    def tick(self):
        if self.handler:
            self.handler.tick()


class Mod():
    def __init__(self, k, panel):
        self.k = k
        self.panel = panel

    def init(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

