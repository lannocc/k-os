from k.ui import *
import k.db as kdb
import k.storage as media
from .library import Panel as Library
from .review import Panel as Review
from .ops import *

from datetime import datetime


class Panel(KPanel):
    def __init__(self, k, anchors, container=None):
        super().__init__(k, anchors, container)

        samples_end_x = k.SAMPLES_X + k.SAMPLES_W
        player_indicator_start_x = k.PLAYER_INDICATOR_X
        available_space = player_indicator_start_x - samples_end_x

        timer_width = 100
        timer_x = samples_end_x + (available_space - timer_width) // 2

        self.lbl_timer = pygame_gui.elements.UILabel(
            text='',
            manager=k.sui,
            relative_rect=pygame.Rect((timer_x, 3), (timer_width, -1)))

        self.btn_library = pygame_gui.elements.UIButton(
            text='Library',
            manager=k.gui,
            container=self.container,
            relative_rect=SPACER)

        self.btn_review = pygame_gui.elements.UIButton(
            text='Review',
            manager=k.gui,
            container=self.container,
            anchors=target(self.btn_library),
            relative_rect=SPACER)
        self.btn_review.disable()

        self.panel_library = Library(k,
            target(self.btn_library, 'top'), self.container)
        self.panel_library.hide()

        self.panel_review = Review(k,
            target(self.btn_review, 'top'), self.container)
        self.panel_review.hide()

        self.cur_btn = self.btn_library
        self.cur_btn.disable()
        self.cur_panel = self.panel_library

        self.reset()

    def reset(self):
        self.replay_id = None

        self.ops = None
        self.clock = None
        self.start = None
        self.start_perf = None
        self.capture = False

        self.lbl_timer.set_text('--:--:--')

    def show(self):
        super().show()
        if self.cur_panel != self.panel_library:
            self.panel_library.hide()
        if self.cur_panel != self.panel_review:
            self.panel_review.hide()

        #self.cur_panel.show()

    def init_replay(self):
        if self.clock:
            return

        self.ops = [ ]

        self.start = datetime.now()
        self.replay_id = kdb.insert_replay(self.start)
        media.start_replay(self.replay_id)

        self.clock = Clock(1)
        self.start_perf = self.clock.started

    def op(self, op):
        if not self.clock:
            return

        if not self.capture:
            if isinstance(op, MouseAction) or isinstance(op, KeyAction):
                return

        self.ops.append(op)

    def screen(self):
        if not self.clock or not self.capture:
            return

        name = time.perf_counter() - self.start_perf
        name = int(name * PRECISION)

        media.save_replay_image(self.replay_id, self.k.screen, name)

    def toggle_capture(self):
        self.capture = not self.capture
        return self.capture

    def break_replay(self, synchronous=False):
        self.k.player.pause()

        if not self.clock:
            return

        if self.capture:
            self.screen()
            self.op(StopCapture())
            self.capture = False

        #print(self.ops)
        #print(Action.format_all(self.ops))

        if synchronous:
            self._save_replay_()
        else:
            self.k.job(self._save_replay_)

    def _save_replay_(self):
        data = Action.format_all(self.ops, self.start_perf)
        kdb.finish_replay(self.replay_id, datetime.now(), data)
        self.reset()

    def tick(self):
        if not self.clock:
            return

        self.clock.tick()

        if not self.clock.ready():
            return

        self.update_timer()

    def update_timer(self):
        t = datetime.now() - self.start
        text = hhmmss(t.seconds)
        if self.capture: text = f'<{text}>'
        self.lbl_timer.set_text(text)
        self.k.status()

    def click(self, element, target=None):
        if element == self.btn_library:
            self.panel_swap(self.btn_library, self.panel_library)

        elif element == self.btn_review:
            self.panel_swap(self.btn_review, self.panel_review)

        else:
            self.cur_panel.click(element, target)
