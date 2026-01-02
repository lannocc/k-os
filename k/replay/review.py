from k.ui import *
import k.db as kdb
import k.storage as media
from .ops import *
from k.player.capture import Player


class Panel(KPanel):
    def __init__(self, k, anchors, container=None):
        super().__init__(k, anchors, container)

        self.replay_id = None

        self.btn_close = pygame_gui.elements.UIButton(
            text='X',
            manager=k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=SPACER)

        self.inp_name = pygame_gui.elements.UITextEntryLine(
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_close),
            relative_rect=pygame.Rect((10, 10), (380, -1)))

        self.btn_name = pygame_gui.elements.UIButton(
            text='Name',
            manager=k.gui,
            container=self.container,
            anchors=target(self.inp_name),
            relative_rect=SPACER)

        self.lbl_captures = pygame_gui.elements.UILabel(
            text='',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_close, 'top'),
            relative_rect=SPACER)

        self.con_captures = None
        self.captures = [ ]

    def open_replay(self, replay_id):
        self.close_replay()
        replay = kdb.get_replay(replay_id)

        self.replay_id = replay_id
        self.ops = Action.parse_all(replay['data'])

        name = replay['name']
        if not name:
            name = ''
        self.inp_name.set_text(name)

        self.con_captures = pygame_gui.elements.UIScrollingContainer(
            manager=self.k.gui,
            container=self.container,
            anchors=target(self.lbl_captures, 'top'),
            relative_rect=pygame.Rect((10, 10), (500, 400)))

        images = sorted([
            int(name) for name in media.list_replay_images(self.replay_id) ])
        captures = [ ]
        capture = [ ]

        for op in self.ops:
            while images:
                if images[0] <= op.t:
                    capture.append(images.pop(0))
                else:
                    break

            if isinstance(op, MouseAction) or isinstance(op, KeyAction):
                capture.append(op)

            elif isinstance(op, StopCapture):
                capture.append(op)
                captures.append(capture)
                capture = [ ]

        if capture:
            captures.append(capture)

        if images:
            print(f'uh oh... still have images after last capture: {images}')

        count = len(captures)
        label = f'{count} capture'
        if count != 1: label += 's'
        if count != 0: label += ':'
        self.lbl_captures.set_text(label)

        y = 0
        for capture in captures:
            if not capture:
                print('ignoring empty capture set')
                continue

            entry = Capture(self.k, self.con_captures.get_container(), y,
                self.replay_id, capture)
            self.captures.append(entry)
            y += entry.get_rect().height

        self.k.panel_replay.panel_library.refresh(self.replay_id)

    def close_replay(self):
        self.replay_id = None
        self.ops = None

        if self.con_captures:
            self.con_captures.kill()
        self.captures = [ ]

        panel = self.k.panel_replay
        panel.panel_library.refresh()
        panel.panel_swap(panel.btn_library, panel.panel_library)
        panel.btn_review.disable()

    def click(self, element, target=None):
        if element == self.btn_close:
            self.close_replay()

        elif element == self.btn_name:
            kdb.set_replay_name(self.replay_id, self.inp_name.get_text())
            self.k.panel_replay.panel_library.refresh(self.replay_id)

        else:
            for entry in self.captures:
                entry.click(element, target)


class Capture(KPanel):
    def __init__(self, k, container, y, replay_id, capture):
        super().__init__(k, container=container, relative_rect=pygame.Rect(
            (0, y), (480, 30)))

        self.replay_id = replay_id
        self.capture = capture

        item = capture[0]
        start = item.t if isinstance(item, Action) else item

        item = capture[-1]
        stop = item.t if isinstance(item, Action) else item

        dur = hhmmss((stop - start) / PRECISION, True)

        self.lbl_duration = pygame_gui.elements.UILabel(
            text=f'duration: {dur}',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((0, 0), (200, 20)))

        self.btn_play = pygame_gui.elements.UIButton(
            text='Play',
            manager=self.k.gui,
            container=self.container,
            relative_rect=pygame.Rect((400, 0), (80, 25)))

    def click(self, element, target=None):
        if element == self.btn_play:
            self.k.job(self.play)

    def play(self):
        self.k.player.open(Player(self.k, self.replay_id, self.capture))
        self.k.player.play()

