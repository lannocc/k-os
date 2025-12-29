import k.db as kdb
from .ui import Player as UI
from .ext import MultiTracker


class Player(UI):
    def __init__(self, k, seq_id, loop=None, jumps=None):
        self.seq_id = id

        trks = [ ]
        for seg in kdb.list_segments(seq_id):
            pass #FIXME

        super().__init__(k, MultiTracker(trks), loop, jumps)

