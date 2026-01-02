import k.db as kdb
from .frag import Chaos


class Player(Chaos):
    def __init__(self, k, seq_id, idx, loop=None, jumps=None):
        self.seq_id = seq_id
        self.idx = idx

        seg = kdb.get_segment(seq_id, idx)

        super().__init__(k, seg['fragment'], loop, jumps)

