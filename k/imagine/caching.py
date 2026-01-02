from k.ui import *

import cv2

import threading


class Dream(threading.local):
    LEVEL = 1981

    def __init__(self, capture):
        super().__init__()

        self.mind = capture

        good, spark = self.mind.read()
        if not good:
            raise ValueError(f'can\'t get it: {capture}')

        self.frame = 0
        self.cloud = [   self.frame   ] # up to LEVEL
        self.cache = [ Thought(spark) ] # back from LEVEL

        self.rate_have = Counter()
        self.rate_know = Counter()
        self.rate_find = Counter()
        self.rate_size = Counter()

    def awake(self):
        self.mind.release()

    def it(self, frame, size=None):
        remember = None

        if frame == self.cloud[0]:
            with self.rate_have:
                remember = self.cache[-1]

        else:
            if frame in self.cloud:
                with self.rate_have:
                    level = self.cloud.index(frame)
                    del self.cloud[level]
                    remember = self.cache.pop(-level-1)

            else:
                if frame == self.frame:
                    rate = self.rate_know

                else:
                    rate = self.rate_find

                with rate:
                    if rate is self.rate_find:
                        self.mind.set(cv2.CAP_PROP_POS_FRAMES, frame)

                    good, spark = self.mind.read()
                    if not good:
                        raise ValueException('cap off :: out of it')
                    self.frame = frame + 1

                    if len(self.cloud) > Dream.LEVEL:
                        del self.cloud[Dream.LEVEL:]
                        del self.cache[:-Dream.LEVEL]

                    remember = Thought(spark)

            self.cloud.insert(0, frame)
            self.cache.append(remember)

        with self.rate_size:
            return remember.goods(size)


class Thought:
    def __init__(self, image, other=None):
        self.origin = image
        self.shape = [ image.shape[1::-1], other ]
        self.spark = None
        self.rate = Counter()

    def goods(self, size=None):
        if size is None or size == self.shape[0]:
            return self.origin

        with self.rate:
            if size != self.shape[1]:
                self.shape[1] = size
                self.spark = None

            if self.spark is None:
                self.spark = cv2.resize(self.origin, self.shape[1])

        return self.spark

