from k.ui import *
from .core import get_size_to_fit

import cv2


class MultiTracker():
    def __init__(self, trks, begin=0, end=None):
        self.begin = begin
        frames = 0

        self.trks = [ ]
        for trk in trks:
            #print(f'trk frames: {trk.frames}')
            self.trks.append((frames, trk))
            frames += trk.frames

        if end is None:
            self.frames = frames - begin
            self.end = self.frames - 1
        else:
            self.frames = end - begin + 1
            self.end = end

        self.reset()

    def reset(self):
        self.playing = None

        for offset, trk in self.trks:
            trk.reset()

        self.set_idx(0, True)
        idx = self.get_new_idx(self.begin)
        if idx is not None:
            self.set_idx(idx)
        self.frame = self.begin

    def set_idx(self, idx, first_time=False):
        #print(f'indexing to tracker: {idx} ({first_time})')

        if not first_time:
            offset, trk = self.trks[self.idx]
            trk.reset()

        self.idx = idx
        self.offset, self.trk = self.trks[self.idx]
        self.res = self.trk.res
        self.size = self.trk.size

        if self.playing:
            self.trk.play()
        elif self.playing is False:
            self.trk.pause()

    def get_new_idx(self, frame):
        if frame < self.offset:
            #print(f'frame before current tracker: {frame}')
            for idx in range(self.idx - 1, -1, -1):
                offset, trk = self.trks[idx]
                if frame >= offset:
                    return idx

        elif frame >= self.offset + self.trk.frames:
            #print(f'frame after current tracker: {frame}')
            for idx in range(self.idx + 1, len(self.trks)):
                offset, trk = self.trks[idx]
                if frame < offset + trk.frames:
                    return idx

        else:
            return None

    def play(self):
        if self.playing:
            return

        self.trk.play()
        self.playing = True

    def pause(self):
        if not self.playing:
            return

        self.trk.pause()
        self.playing = False

    def stop(self):
        if self.playing is None:
            return

        self.reset()

    def seek(self, frame):
        #print(f'frame seek: {frame}')

        if frame < self.begin:
            frame = self.begin
        elif frame > self.end:
            frame = self.end

        idx = self.get_new_idx(frame)
        if idx is not None:
            self.set_idx(idx)

        self.frame = frame

        frame = frame - self.offset + self.trk.begin
        self.trk.seek(frame)

    def tick(self):
        if self.playing is None:
            return None

        tock = self.trk.tick()

        if tock is None:
            #print('no tock')
            idx = self.idx + 1
            if idx >= len(self.trks):
                self.reset()
            else:
                self.set_idx(idx)
                tock = self.trk.tick()

        if self.playing and tock is not False:
            self.frame += 1
            if self.frame > self.end:
                self.reset()

        return tock

    def size_to_fit(self, width, height):
        for offset, trk in self.trks:
            trk.size_to_fit(width, height)

        self.size = self.trk.size


class StaticTracker():
    def __init__(self, resource, frame, count):
        self.res = resource
        self.pframe = frame
        self.frames = count

        self.begin = 0
        self.end = self.frames - 1

        self.resize = None
        self.size = self.res.size
        self.reset()

    def reset(self):
        self.clock = Clock(self.res.fps)
        self.frame = 0

        self.img_orig = None
        self.img = None

        self.res.stop()
        self.playing = None

        self.refresh()

    def refresh(self):
        img = self.res.get(self.pframe)

        if self.img is None or img is not self.img_orig:
            if self.resize:
                self.img = cv2.resize(img, self.resize)
            else:
                self.img = img

            self.img_orig = img
            self.img = pygame.image.frombuffer(self.img.tobytes(), self.size,
                "BGR")

    def play(self):
        if self.playing:
            return

        self.clock.reset()
        #self.res.play()
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
        if frame < self.begin:
            frame = self.begin
        elif frame > self.end:
            frame = self.end

        self.frame = frame
        self.clock.reset()

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
        resize = get_size_to_fit(self.res.size, (width, height))

        if resize[0] != self.res.size[0] or resize[1] != self.res.size[1]:
            self.resize = resize
            self.size = resize
        else:
            self.resize = None
            self.size = self.res.size

        self.img = None
        self.refresh()


class HoldingTracker():
    def __init__(self, resource, frame, count):
        self.res = resource
        self.pframe = frame
        self.frames = count

        self.begin = 0
        self.end = self.frames - 1

        self.resize = None
        self.size = self.res.size
        self.reset()

    def reset(self):
        self.clock = Clock(self.res.fps)
        self.frame = 0

        self.img_orig = None
        self.img = None

        self.res.stop()
        self.playing = None

        self.refresh()

    def refresh(self):
        img = self.res.get(self.pframe)

        if self.img is None or img is not self.img_orig:
            if self.resize:
                self.img = cv2.resize(img, self.resize)
            else:
                self.img = img

            self.img_orig = img
            self.img = pygame.image.frombuffer(self.img.tobytes(), self.size,
                "BGR")

    def play(self):
        if self.playing:
            return

        self.clock.reset()
        self.res.play()
        self.playing = True

    def pause(self):
        if self.playing is False:
            return

        self.res.pause()
        self.playing = False

    def stop(self):
        if self.playing is None:
            return

        self.reset()

    def seek(self, frame):
        if frame < self.begin:
            frame = self.begin
        elif frame > self.end:
            frame = self.end

        self.frame = frame
        self.clock.reset()

    def tick(self):
        if self.playing is None:
            return None

        self.res.get(self.pframe, True)

        self.clock.tick()
        if not self.clock.ready():
            return False

        if self.playing:
            self.frame += 1
            if self.frame > self.end:
                self.reset()

        return self.img

    def size_to_fit(self, width, height):
        resize = get_size_to_fit(self.res.size, (width, height))

        if resize[0] != self.res.size[0] or resize[1] != self.res.size[1]:
            self.resize = resize
            self.size = resize
        else:
            self.resize = None
            self.size = self.res.size

        self.img = None
        self.refresh()