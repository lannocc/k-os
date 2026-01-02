from k.ui import *
from .general import Panel as General
from .player import Panel as Player
from .ack import Panel as Ack

from html import escape


INTRO = '''
Use this screen to learn the functions assigned to various keys. Simply click one or more of the key buttons displayed below to learn their assignments. Use the 'Reset Keys' button to unclick any key buttons. Alternatively, when the 'Discover' button is toggled, simply press and hold any key or combination of keys on your actual keyboard to find their function.
'''


class Panel(KPanel):
    def __init__(self, k, anchors):
        super().__init__(k, anchors)

        self.txt_intro = pygame_gui.elements.UITextBox(
            html_text=escape(INTRO.strip()).replace('\n', '<br>'),
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (WIDTH-PWIDTH-20, 80)))

        self.btn_general = pygame_gui.elements.UIButton(
            text='General',
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.txt_intro, 'top'),
            relative_rect=pygame.Rect((0, 10), (-1, -1)))
        self.panel_general = General(self,
            target(self.btn_general, 'top'), self.container)

        self.btn_ack = pygame_gui.elements.UIButton(
            text='Ack',
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.txt_intro, 'top', target(self.btn_general)),
            relative_rect=SPACER)
        self.panel_ack = Ack(self,
            target(self.btn_ack, 'top'), self.container)

        self.btn_player = pygame_gui.elements.UIButton(
            text='Player',
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.txt_intro, 'top', target(self.btn_ack)),
            relative_rect=SPACER)
        self.panel_player = Player(self,
            target(self.btn_player, 'top'), self.container)

        self.btn_all = pygame_gui.elements.UIButton(
            text='[ ] List All',
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.txt_intro, 'top'),
            relative_rect=pygame.Rect((395, 10), (-1, -1)))

        self.txt_all = None
        self.txt_keys = None
        self.txt_info = None
        self.key_info(None, None)

        self.btn_reset = pygame_gui.elements.UIButton(
            text='Reset Keys',
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.txt_keys, 'top'),
            relative_rect=pygame.Rect((0, 0), (130, 25)))
        self.btn_reset.disable()

        self.btn_discover = pygame_gui.elements.UIButton(
            text='[ ] Discover',
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.btn_reset, 'top'),
            relative_rect=pygame.Rect((0, 0), (130, 25)))

        self.cur_btn = self.btn_general
        self.cur_btn.disable()
        self.cur_panel = self.panel_general

        self.discover = False # Use None for "list all"

    def key_info(self, keys, info):
        if self.txt_keys: self.txt_keys.kill()
        if self.txt_info: self.txt_info.kill()

        self.txt_keys = pygame_gui.elements.UITextBox(
            html_text=escape(' '.join(keys) if keys else ''),
            manager=self.k.gui,
            container=self.container,
            #anchors=target(self.panel_general.container, 'top'),
            #relative_rect=pygame.Rect((0, 10), (130, 65)))
            relative_rect=pygame.Rect((0, 450), (130, 66)))

        self.txt_info = pygame_gui.elements.UITextBox(
            html_text=escape(info).replace('\n', '<br>') if info else '',
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.panel_general.container, 'top',
                target(self.txt_keys)),
            relative_rect=pygame.Rect((10, 10), (375, 115)))

    def show(self):
        super().show()
        if self.cur_panel is not self.panel_general:
            self.panel_general.hide()
        if self.cur_panel is not self.panel_player:
            self.panel_player.hide()
        if self.cur_panel is not self.panel_ack:
            self.panel_ack.hide()

    def hide(self):
        if self.discover is None:
            self.toggle_all()
        self.cur_panel.reset()
        super().hide()

    def toggle_all(self):
        if self.discover is not None:
            self.btn_general.disable()
            self.btn_ack.disable()
            self.btn_player.disable()
            self.cur_panel.hide()
            self.txt_keys.hide()
            self.txt_info.hide()
            self.btn_reset.hide()
            self.btn_discover.hide()
            self.btn_all.set_text('[x] List All')
            self.discover = None
            self.k.job(self._all_)

        else:
            self.txt_all.kill()
            self.btn_general.enable()
            self.btn_ack.enable()
            self.btn_player.enable()
            self.cur_btn.disable()
            self.cur_panel.show()
            self.txt_keys.show()
            self.txt_info.show()
            self.btn_reset.show()
            self.btn_discover.show()
            self.btn_all.set_text('[ ] List All')
            self.discover = False

    def toggle_discover(self):
        if self.discover is None: return
        self.discover = not self.discover
        self.cur_panel.reset()

        if self.discover:
            self.btn_discover.set_text('[x] Discover')
            #for key in self.cur_panel.keys.values():
            #    key.disable()
            self.k.status('K')

        else:
            self.btn_discover.set_text('[ ] Discover')
            self.k.status('N')

    def _all_(self):
        def pretty(items):
            return '<br>'.join([
                f'<b>{escape(items[0])}',
                '=' * len(items[0]) + '</b>',
                f'<i>{escape(items[1])}</i><br>',
                #'<br>'.join(' '.join(items[2][0]) + ' :: ' + items[2][1])
                '<br>'.join(filter(None, [None if info is None else \
                    '<b>' + escape(' '.join(keys)) + '</b> :: ' \
                        + escape(info).replace('\n', '<br>    ') \
                    for keys, info in items[2]
                ]))
            ])

        txt = '<br><br><br>'.join([pretty(panel.all()) for panel in [
            self.panel_general,
            self.panel_ack,
            self.panel_player
        ]])

        self.txt_all = pygame_gui.elements.UITextBox(
            html_text=txt,
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 130), (515, 435)))

    def keydown(self, key, mod):
        if self.discover:
            self.cur_panel.keydown(key)

    def keyup(self, key, mod):
        if self.discover:
            self.cur_panel.keyup(key)

    def click(self, element, target=None):
        if element is self.btn_general:
            self.panel_swap(self.btn_general, self.panel_general)

        elif element is self.btn_player:
            self.panel_swap(self.btn_player, self.panel_player)

        elif element is self.btn_ack:
            self.panel_swap(self.btn_ack, self.panel_ack)

        elif element is self.btn_all:
            self.toggle_all()

        elif element is self.btn_discover:
            self.toggle_discover()

        elif element is self.btn_reset:
            self.cur_panel.reset()

        else:
            return self.cur_panel.click(element, target)

        return True

