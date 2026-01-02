from k.ui import *
import k.db as kdb
import k.storage as media
from .core import Resource, Tracker
from .ext import MultiTracker, StaticTracker, HoldingTracker
from .ui import Player as UI


class Player(UI):
    def __init__(self, k, replay_id):
        self.replay_id = replay_id

        self.res = { }
        for video in kdb.list_replay_videos(replay_id):
            self.res[video['video']] = Resource(video['video'])

        ops = kdb.list_replay_ops(replay_id)
        if len(ops) < 2:
            raise ValueError(
                f'need at least 2 replay_ops for replay: {replay_id}')
        elif ops[-1]['operation'] != kdb.OP_STOP:
            op = ops[-1]
            raise ValueError(f'expecting OP_STOP as last replay_op: {op["id"]}')

        trks = [ ]
        for i in range(len(ops) - 1):
            op = ops[i]
            res = self.res[op['video']]
            nop = ops[i+1]
            dur = nop['millis'] - op['millis']
            frame = op['frame']
            count = int(res.fps * dur / 1000)

            if count < 1:
                print(f'discarding miniscule replay_op: {op["id"]}')

            if op['operation'] == kdb.OP_START:
                trks.append(Tracker(res, frame, frame + count - 1))

            elif op['operation'] == kdb.OP_STOP:
                trks.append(StaticTracker(res, frame, count))

            elif op['operation'] == kdb.OP_HOLD:
                trks.append(HoldingTracker(res, frame, count))

            else:
                raise ValueError(f'unsupported replay_op: {op["id"]}')

        video = kdb.get_video(kdb.get_replay_first_op(replay_id)['video'])
        channel = kdb.get_channel(video['channel'])
        thumb = media.get_video_thumbnail(channel['ytid'], video['ytid'])
        thumb = pygame.image.load(thumb)

        super().__init__(k, MultiTracker(trks), thumb)

    def kill(self, replace=False):
        super().kill(replace)

        for res in self.res.values():
            res.kill()

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

