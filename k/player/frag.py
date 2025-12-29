import k.db as kdb
import k.storage as media
from .ui import Player as UI
from .core import Resource, Tracker
from .video import Player as Video


class Chaos(UI):
    def __init__(self, k, frag_id, loop=None, jumps=None):
        # We intentionally do NOT call super().__init__()

        self.frag_id = frag_id

        go = 'ko'
        try:
            frag = kdb.get_frag(self.frag_id)
            frag_type = frag['media']
            source = frag['source']
            start = frag['start']
            stop = frag['stop']

            if frag_type == kdb.MEDIA_VIDEO:
                res = Resource(source, k.imagine)
                trk = Tracker(res, begin=start, end=stop)
                go = Video(k, trk, loop, jumps)

            else:
                raise ValueError(
                    f'frag {frag_id} unsupported media type: {frag_type}')

        except Exception as e:
            print(f'Chaos--! frag {go} boom!-- player')
            print(f'     !!! {e}')
            go = None

        self.go = go

    def reset(self):
        if not self.go:
            return

        self.go.reset()

    def kill(self, replace=False):
        if not self.go:
            return

        self.go.kill(replace)

    @property
    def panel_chaos(self):
        if not self.go:
            return None

        return self.go.panel_chaos

    @property
    def playing(self):
        if not self.go:
            return None

        return self.go.playing

    @property
    def trk(self):
        if not self.go:
            return None

        return self.go.trk

    def play(self):
        if not self.go:
            return

        self.go.play()

    def pause(self):
        if not self.go:
            return

        self.go.pause()

    def stop(self):
        if not self.go:
            return

        self.go.stop()

    def seek(self, frame):
        if not self.go:
            return

        self.go.seek()

    def update_frame(self, frame):
        if not self.go:
            return

        self.go.update_frame(frame)

    def tick(self):
        if not self.go:
            return

        self.go.tick()

    def paint(self):
        if not self.go:
            return

        self.go.paint()

    def paint_thumb(self):
        if not self.go:
            return

        self.go.paint_thumb()

    def paint_video(self):
        if not self.go:
            return

        self.go.paint_video()

    def paint_image(self):
        if not self.go:
            return

        self.go.paint_image()

    def paint_loop_bar(self):
        if not self.go:
            return

        self.go.paint_loop_bar()

    def size_to_fit(self, width, height):
        if not self.go:
            return

        self.go.size_to_fit(width, height)

    def click(self, element, target=None):
        if not self.go:
            return

        self.go.click(element, target)

    def mouse_down(self, event):
        if not self.go:
            return

        self.go.mouse_down(event)

    def mouse_up(self, event):
        if not self.go:
            return

        self.go.mouse_up(event)

    def keydown(self, key, mod):
        if not self.go:
            return

        self.go.keydown(key, mod)

    def keyup(self, key, mod):
        if not self.go:
            return

        self.go.keyup(key, mod)

    def keyhold(self, key, magic=False):
        if not self.go:
            return

        self.go.keyhold(key, magic)

    def op_start(self):
        if not self.go:
            return

        self.go.op_start()

    def op_stop(self):
        if not self.go:
            return

        self.go.op_stop()

    def op_seek(self):
        if not self.go:
            return

        self.go.op_seek()

    def op_hold(self):
        if not self.go:
            return

        self.go.op_hold()

    def op_unhold(self):
        if not self.go:
            return

        self.go.op_unhold()


class Null(Tracker):
    def __init__(self, resource=None, begin=0, end=None):
        if not resource:
            resource = Void()

        super().__init__(resource, begin, end)

    def play(self):
        pass

    def pause(self):
        pass

    def tick(self):
        return None


class Void(Resource):
    def __init__(self, video_id=None):
        self.video_id = video_id

        self.frames = 0
        self.fps = 999

        self.img = None
        self.size = [0, 0]

    def kill(self):
        pass

    def get(self, frame, seeking=False):
        return None

    def play(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass