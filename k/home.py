from k.ui import *
from version import *
import k.storage as media
from k.labels import Panel as Labels
from k.keys import Panel as Keys


INFO = '''ORDER IN CHAOS

This is the "K" Operating System. K in this context stands in for many things such as keyframe or knife, but also generically.

Purpose:
- make art
- play video
- hack python
- perform musically
- train logic (AI)
- grow fun community
'''

EXTRA = '''

From a complete and fully-formed object / idea to noise, randomness, or the absence of anything... there are those points where change occurs and entropy is added; that is K.

_________
'''

SIGNED = 'THANK YOU for running this program.\n' \
       + 'Email ' + SAW + ' @ ' + THEY + ' if you want to help...\n' \
       + '  --' + ME

IMAGE = media.get_gfx('title.png')


class Panel(KPanel):
    def __init__(self, k, anchors):
        super().__init__(k, anchors)

        self.image = pygame_gui.elements.UIImage(
            image_surface=IMAGE,
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((10, 10), (180, 180)))

        self.tagline = pygame_gui.elements.UILabel(
            text='> Disorderly Conduct ^',
            manager=k.gui,
            container=self.container,
            anchors=target(self.image, 'top'),
            relative_rect=SPACER)

        if self.k.testing:
            self.btn_testing = pygame_gui.elements.UIButton(
                text='TEST ME',
                manager=k.gui,
                container=self.container,
                relative_rect=pygame.Rect((250, 111), (-1, -1)))
        else:
            self.btn_testing = None

        self.btn_keys = pygame_gui.elements.UIButton(
            text='HotKeys',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((420, 175), (90, 25)))
        self.panel_keys = Keys(k, target(k.btn_home, 'top'))

        self.btn_labels = pygame_gui.elements.UIButton(
            text='Labels',
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((420, 200), (90, 25)))
        self.panel_labels = Labels(k, target(k.btn_home, 'top'))

        self.info = pygame_gui.elements.UITextBox(
            html_text=(INFO+EXTRA+SIGNED).replace('\n', '<br>'),
            manager=k.gui,
            container=self.container,
            relative_rect=pygame.Rect((9, 234), (WIDTH-PWIDTH-36, 336)))

        self.version = pygame_gui.elements.UILabel(
            text=f'v/ {VVHEN}',
            #manager=k.gui,
            #relative_rect=pygame.Rect((WIDTH/2 - 125, HEIGHT-30), (250, -1)))
            manager=k.sui,
            relative_rect=pygame.Rect((WIDTH/2 - 125, 3), (250, -1)))

        #self.status_rect = pygame.Rect((5, HEIGHT-27), (152, 20))
        self.status_rect = pygame.Rect((5, 5), (152, 20))
        self.status = {}

        for mode in MODES:
            status = pygame_gui.elements.UIImage(
                image_surface=media.get_gfx(MODES[mode]),
                manager=k.sui,
                relative_rect=self.status_rect)
            status.hide()
            self.status[mode] = status

    def click(self, element, target=None):
        if self.btn_testing and element is self.btn_testing:
            from k.player.testing import Player
            self.k.player.open(Player(self.k))

        elif element is self.btn_keys:
            self.k.panel_swap(None, self.panel_keys)

        elif element is self.btn_labels:
            self.k.panel_swap(None, self.panel_labels)

        else:
            return False

        return True

