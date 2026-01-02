from k.ui import *
import k.storage as media
from k.replay.ops import *
from .ui import Player as UI
from .core import get_size_to_fit


class Player(UI):
    def __init__(self, k, replay_id, capture):
        super().__init__(k, CapTracker(replay_id, capture))

    def paint_video(self):
        pass #FIXME


class CapTracker():
    def __init__(self, replay_id, capture):
        #print(f'CapTracker frames: {len(capture)}')
        self.replay_id = replay_id
        self.capture = capture

        self.frames = len(self.capture)
        self.begin = 0
        self.end = self.frames - 1

        self.resize = None
        self.size = None #FIXME
        self.reset()

    def reset(self):
        self.clock = CapClock(self.capture)
        self.frame = 0

        self.img_orig = None
        self.img = None

        self.playing = None
        self.refresh()

    def refresh(self):
        pass

    def play(self):
        if self.playing:
            return

        self.playing = True

    def pause(self):
        if self.playing is False:
            return

        self.playing = False

    def stop(self):
        if self.playing is None:
            return

        self.reset()

    def seek(self, frame):
        print(f'seek: {frame}')
        pass #FIXME

    def tick(self):
        if self.playing is None:
            return None

        self.clock.tick()
        if not self.clock.ready():
            return False

        if self.playing:
            self.frame += 1
            if self.frame > self.end:
                self.reset()

        return self.img

    def size_to_fit(self, width, height):
        print(f'size_to_fit: {width}, {height}')

        resize = get_size_to_fit((100, 100), (width, height)) #FIXME

        #FIXME
        self.resize = resize
        self.size = resize

        self.img = pygame.Surface((width, height)) #FIXME
        self.refresh()


class CapClock(Clock):
    def __init__(self, capture):
        self.capture = capture

        item = capture[0]
        self.offset = item.t if isinstance(item, Action) else item

        self.reset()

    def reset(self):
        super().reset()
        self.idx = 0

        print(self.started)

    def _next_(self):
        if self.idx >= len(self.capture) - 1:
            print('##?? all done ??##')
            return 0

        item = self.capture[self.idx]
        t = item.t if isinstance(item, Action) else item
        t -= self.offset
        t /= PRECISION

        return self.started + t

    def _set_(self):
        super()._set_()
        self.idx += 1

