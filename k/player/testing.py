import k.db as kdb
from .core import Resource, Tracker
from .ext import MultiTracker, StaticTracker
from .ui import Player as UI


class Player(UI):
    def __init__(self, k):
        trks = [
            Tracker(Resource(1)),
            StaticTracker(Resource(10), 100, 420),
            Tracker(Resource(2)),
            Tracker(Resource(3))
        ]

        super().__init__(k, MultiTracker(trks))

    def op_start(self):
        pass

    def op_stop(self):
        pass

    def op_seek(self):
        pass

    def op_hold(self):
        pass

    def op_unhold(self):
        pass

