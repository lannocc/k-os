import colorama as c
print('U.I. '+c.Fore.BLACK+c.Style.BRIGHT+'chaos'+c.Style.RESET_ALL+' begins')

import pygame
import pygame_gui

from contextlib import AbstractContextManager
import time


WIDTH = 1042
HEIGHT = 666
STATUS = 33 # status bar height
PWIDTH = 505 # player width
PHEIGHT = 284 # player height

MODES = {
    'N': 'normal.png',  # nothing specifically
    'E': 'error.png',   # something went wrong
    'B': 'busy.png',    # generic "doing something"
    'D': 'txfr.png',    # downloading
    'A': 'ack.png',     # blackboard
    'K': 'keys.png',    # keyboard discovery
    'Q': 'quit.png',    # quitting
    'C': 'confirm.png', # confirmation required
    'U': 'music.png',   # music mode
}

LOG_DISABLE = [
    'meta tick',
    'meta kick',
    'kush key',
]

BLACK   = pygame.Color(  0,   0,   0)
WHITE   = pygame.Color(255, 255, 255)
RED     = pygame.Color(255,   0,   0)
GREEN   = pygame.Color(  0, 255,   0)
BLUE    = pygame.Color(  0,   0, 255)
CYAN    = pygame.Color(  0, 255, 255)
MAGENTA = pygame.Color(255,   0, 255)
YELLOW  = pygame.Color(255, 255,   0)
GRAY    = pygame.Color(127, 127, 127)
GREY    = pygame.Color(128, 128, 128) #GRaY "Extra"
ORANGE  = pygame.Color(255, 128,   0)

SPACER = pygame.Rect((10, 10), (-1, -1))
PANEL_SPACER = pygame.Rect((10, 10), (WIDTH-20, HEIGHT-100)) #FIXME
ANCHOR = {"left":"left", "top":"top", "right":"left", "bottom":"top"}

SAMPLE_RATE = 44100

PLAY_SEEK_VERT = 3
PLAY_SEEK_VERT_CTRL = 42
PLAY_SEEK_VERT_SHIFT = 666
PAUSE_SEEK_VERT = 1
PAUSE_SEEK_VERT_CTRL = 3333
PAUSE_SEEK_VERT_SHIFT = 10000
SEEK_HORIZ = 10
SEEK_HORIZ_CTRL = 100
SEEK_HORIZ_SHIFT = 1000


# A generic object
class Meta():
    def __init__(self):
        pass


def target(element, direction='left', anchors=ANCHOR):
    anchors = anchors.copy()
    anchors[direction+'_target'] = element
    return anchors

def scroll_to_bottom(container):
    scroll = container.vert_scroll_bar
    if not scroll:
        return

    scroll.scroll_position = scroll.bottom_limit \
        - scroll.sliding_button.relative_rect.height
    scroll.start_percentage = scroll.scroll_position \
        / scroll.scrollable_height
    scroll.has_moved_recently = True
    scroll.redraw_scrollbar()

def hhmmss(secs, millis=False):
    s = int(secs % 60)
    m = int(secs / 60)
    h = int(m / 60)
    m = m % 60

    if s < 10:
        s = f'0{s}'
    if m < 10:
        m = f'0{m}'
    if h < 10:
        h = f'0{h}'

    text = f'{h}:{m}:{s}'

    if millis:
        millis = int((secs % 1) * 1000)
        text += f'.{millis}'

    return text

def date_time(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def file_date_time(dt):
    return dt.strftime('%Y-%m-%d_%H-%M-%S')


class KGUI(pygame_gui.UIManager):
    def __init__(self, resolution):
        super().__init__(resolution)

    def set_focus_set(self, focus):
        old_set = self.focused_set
        super().set_focus_set(focus)
        new_set = self.focused_set

        fix_text = False

        if old_set is not None:
            for item in old_set:
                if isinstance(item, pygame_gui.elements.UITextEntryLine):
                    fix_text = True
                    break

        if fix_text:
            if new_set is not None:
                for item in new_set:
                    if isinstance(item, pygame_gui.elements.UITextEntryLine):
                        fix_text = False
                        break

        if fix_text:
            #print('resetting key repeat')
            pygame.key.set_repeat(0)


class KPanel:
    def __init__(self, k, anchors=None, container=None,
                 relative_rect=PANEL_SPACER, visible=0):

        self.k = k

        self.container = pygame_gui.core.UIContainer(
            manager=k.gui,
            container=container,
            anchors=anchors,
            relative_rect=relative_rect,
            visible=visible)

    def kill(self):
        self.container.kill()

    def show(self):
        self.container.show()

    def hide(self):
        self.container.hide()

    def keydown(self, key, mod):
        return False

    def keyup(self, key, mod):
        return False

    def click(self, element, target=None):
        return False

    def get_rect(self):
        return self.container.get_relative_rect()

    def set_position(self, pos):
        self.container.set_relative_position(pos)

    def move_by(self, dx, dy):
        pos = self.get_rect()
        x = pos[0] + dx
        y = pos[1] + dy

        self.set_position((x, y))

    def panel_swap(self, btn, panel, kill=False):
        if self.cur_btn: self.cur_btn.enable()
        self.cur_btn = btn
        if self.cur_btn: self.cur_btn.disable()

        if self.cur_panel:
            self.cur_panel.kill() if kill else self.cur_panel.hide()
        self.cur_panel = panel
        if self.cur_panel: self.cur_panel.show()


class Clock():
    def __init__(self, fps=999):
        self.fps = fps
        self.reset()

    def reset(self):
        self.started = time.perf_counter()
        self.last = self.started
        self.last_frame = 0

    def tick(self):
        last = self.last
        self.last = time.perf_counter()
        return self.last - last

    def ready(self):
        next_frame = self._next_()

        if self.last >= next_frame:
            #self.last_frame = self.last
            self._set_()
            return True

        else:
            return False

    def wait(self):
        next_frame = self._next_()
        now = time.perf_counter()
        #print(f' {next_frame}  {now}')

        delta = next_frame - now
        #print(f' {delta}')

        if delta > 0:
            #print('waiting')
            time.sleep(delta)

        self._set_()

    def _next_(self):
        frames = int((self.last_frame - self.started) * self.fps)
        next_frame = self.started + ((frames + 1) / self.fps)
        #print(f'{frames} {self.last} {self.last_frame} {next_frame}')
        return next_frame

    def _set_(self):
        self.last_frame = time.perf_counter()

    #def get(self):
    #    return 1 / (time.perf_counter() - self.last)


class NullClock(Clock):
    def __init__(self):
        super().__init__(fps=None)

    def _next_(self):
        return 0


class Counter(AbstractContextManager):
    def __init__(self):
        super().__init__()
        self.score = [ ]
        self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.stop()
        return None

    def start(self):
        self.started = time.perf_counter()

    def stop(self):
        now = time.perf_counter()
        self.score.append((now, now - self.started))

        cut = 0
        for then, count in self.score:
            if now - then < 15:
                break
            cut += 1

        del self.score[:cut]

    def score1(self):
        return self._scoreX_(1)

    def score5(self):
        return self._scoreX_(5)

    def score15(self):
        return self._scoreX_(15)

    def _scoreX_(self, x):
        now = time.perf_counter()
        entries = 0
        score = 0

        for then, count in reversed(self.score):
            if now - then >= x:
                break

            entries += 1
            score += count

        return (entries/x, score/x)

    @staticmethod
    def _score_(score):
        fc = c.Style.BRIGHT + f'{round(score[0])}' + c.Style.RESET_ALL

        pc = f'{score[1]*100:.0f}'
        ipc = int(pc)

        if ipc == '0':
            pc = c.Fore.WHITE + c.Back.GREEN + c.Style.BRIGHT + pc
        elif ipc < 10:
            pc = c.Fore.GREEN + c.Style.BRIGHT + pc
        elif ipc <= 18:
            pc = c.Fore.GREEN + pc
        elif ipc <= 42:
            pc = c.Fore.YELLOW + c.Style.BRIGHT + pc
        elif ipc < 81:
            pc = c.Fore.YELLOW + pc # looks like orange in my terminal
        elif ipc < 90:
            pc = c.Fore.RED + c.Style.BRIGHT + pc # dark orange --lannocc
        else:
            pc = c.Fore.RED + pc

        pc += c.Style.RESET_ALL

        return f'{fc}/{pc}'

    def __str__(self):
        s1 = Counter._score_(self.score1())
        s5 = Counter._score_(self.score5())
        s15 = Counter._score_(self.score15())

        return f'{s1} {s5} {s15}'

    def __add__(self, other):
        result = Counter()
        result.score = sorted(self.score + other.score)
        return result


DEBUG_EVENTS = {
    pygame_gui.UI_BUTTON_PRESSED: 'UI_BUTTON_PRESSED',
    pygame_gui.UI_BUTTON_START_PRESS: 'UI_BUTTON_START_PRESS',
    pygame_gui.UI_BUTTON_DOUBLE_CLICKED: 'UI_BUTTON_DOUBLE_CLICKED',
    pygame_gui.UI_BUTTON_ON_HOVERED: 'UI_BUTTON_ON_HOVERED',
    pygame_gui.UI_BUTTON_ON_UNHOVERED: 'UI_BUTTON_ON_UNHOVERED',
    pygame_gui.UI_TEXT_ENTRY_CHANGED: 'UI_TEXT_ENTRY_CHANGED',
    pygame_gui.UI_TEXT_ENTRY_FINISHED: 'UI_TEXT_ENTRY_FINISHED',
    pygame_gui.UI_HORIZONTAL_SLIDER_MOVED: 'UI_HORIZONTAL_SLIDER_MOVED',
}

def debug_event(event):
    if event.type in DEBUG_EVENTS:
        print(f'^{DEBUG_EVENTS[event.type]}')

