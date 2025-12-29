from k.ui import c, Counter
from .caching import Dream

import cv2

import threading
import queue
import sys


class ImageEngine(threading.Thread):
    def __init__(self):
        self.go = True
        self.rate = Counter()

        self.videos = { }
        self.load = queue.SimpleQueue()
        self.loaded = threading.Event()
        self.ready = threading.Event()
        self.trip = queue.SimpleQueue()
        self.fire = queue.SimpleQueue()
        self.ember = None
        self.stoked = False

        super().__init__(name="imagination")

    def run(self):
        print("imagine running wild")

        while self.go:

            # combustion
            with self.rate:
                target = None
                try:
                    while idea := self.trip.get_nowait():
                        if idea[0] is None:
                            self.odometer()
                        elif idea[2] is not None and idea[3] is not None:
                            target = idea

                except queue.Empty:
                    pass

                if target is not None:
                    res = target[0]
                    frame = target[1]
                    pos = target[2]
                    size = target[3]
                    try:
                        spark = self.videos[res].it(frame, size)
                        self.fire.put_nowait((pos, spark.tobytes(), size))
                        self.ember = (pos, None, size)
                    except KeyError:
                        # resource has been removed
                        self.ember = None

            # refuel
            gassed = True
            try:
                while res := self.load.get_nowait():
                    if not self.go:
                        self.loaded.set()
                        break

                    print(f' [IE] video file load: {res.vfn}')
                    dream = Dream(cv2.VideoCapture(res.vfn))
                    res.frames = int(dream.mind.get(cv2.CAP_PROP_FRAME_COUNT))
                    res.fps = dream.mind.get(cv2.CAP_PROP_FPS)
                    res.size = dream.cache[0].shape[0]
                    res.video = dream

                    self.videos[res] = dream
                    self.loaded.set()

            except queue.Empty:
                gassed = False

            # idle
            if target is None and not gassed and self.ember:   
                self.fire.put_nowait(self.ember)

            elif self.go:
                self.ready.wait()
                self.ready.clear()

        print("I.E. "+c.Fore.BLACK+c.Style.BRIGHT+"exhausted"+c.Style.RESET_ALL)

    def unplug(self, resource):
        dreaming = self.videos[resource]
        del self.videos[resource]
        dreaming.awake()

    def rev(self):
        self.ready.set()

    def odometer(self):
        think = Counter()
        have = Counter()
        know = Counter()
        find = Counter()

        for dream in self.videos.values():
            think += dream.rate_size
            have += dream.rate_have
            know += dream.rate_know
            find += dream.rate_find

        cb = c.Fore.BLACK + c.Back.WHITE + c.Style.DIM
        bc = c.Style.RESET_ALL

        print(' '+c.Style.DIM+'[IE]'+c.Style.NORMAL \
              #+ f'   {cb}have{bc} @ {have}   {cb}know{bc} @ {know}' \
              #+ f'   {cb}find{bc} @ {find}   {cb}think{bc} @ {think}')
              + f'    {cb}think{bc} {think}    {cb}have{bc} {have}' \
              + f'    {cb}know{bc} {know}    {cb}find{bc} {find}')

        self.stoked = False

    def choke(self):
        self.go = False
        self.rev()

    def fuel(self, resource):
        self.load.put_nowait(resource)
        self.rev()

        while resource not in self.videos:
            if not self.go:
                return

            self.loaded.wait()

        self.loaded.clear()

    def throttle(self, resource, frame):
        self.trip.put_nowait((resource, frame, None, None))

    def speed(self, resource, frame, pos, size):
        self.trip.put_nowait((resource, frame, pos, size))

    def burn(self, pipe, muffler, housing=None):
        flame = None
        try:
            while flame := self.fire.get_nowait():
                pass
        except queue.Empty:
            pass

        if flame is None or not self.go:
            return None

        mounted = flame[0]
        spark = flame[1]
        bang = flame[2]

        if housing:
            mounted[0] += housing[0]
            mounted[1] += housing[1]

        if spark is None:
            if self.stoked:
                print('.', end='')
            else:
                print('stoking ember.', end='')
                self.stoked = True

            sys.stdout.flush()

            # FIXME: half-fade / glow
            return None

        else:
            return pipe.blit(muffler(spark, bang, "BGR"), mounted)

    def score(self):
        self.trip.put_nowait((None, None, None, None))
        self.rev()

