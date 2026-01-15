import k.db as kdb
import k.storage as media
from .ui import Player as UI
from k.replay.ops import Action
from .core import Resource, Tracker
from .video import Player as Video

import os


class Chaos(UI):
    def __init__(self, k, frag_id, loop=None, jumps=None, selection_regions_json=None):
        # We intentionally do NOT call super().__init__()

        self.frag_id = frag_id
        self.k = k # Store k for action recording

        go = 'ko'
        try:
            frag = kdb.get_frag(self.frag_id)
            frag_type = frag['media']
            source = frag['source']
            start = frag['start']
            stop = frag['stop']

            if frag_type == kdb.MEDIA_VIDEO:
                # Ensure all required assets are present before creating a Resource.
                # This handles playing clips from newly imported projects where media
                # has not yet been downloaded.
                streams = kdb.list_video_streams(source)
                if not streams:
                    print(f"Stream info for video {source} not found. Processing video.")
                    self.k.jab(media.finish_adding_video, source, 'D')
                    self.k.jab(media.extract_audio_from_video, source, 'B')
                    streams = kdb.list_video_streams(source) # Re-fetch
                    if not streams:
                        raise ValueError(f"Could not get stream info for video {source} after processing.")

                # Even if DB info exists, files might have been deleted.
                video = kdb.get_video(source)
                channel = kdb.get_channel(video['channel'])
                stream = streams[0] #FIXME
                vfn = media.get_video_filename(channel['ytid'], video['ytid'], stream['itag'], stream['subtype'])
                if not os.path.exists(vfn):
                    print(f"Video file missing: {vfn}. Re-downloading.")
                    self.k.jab(media.finish_adding_video, source, 'D')
                afn = media.get_audio_filename(channel['ytid'], video['ytid'])
                if not os.path.exists(afn):
                    print(f"Audio file missing: {afn}. Extracting.")
                    self.k.jab(media.extract_audio_from_video, source, 'B')

                res = Resource(source, k.imagine)
                trk = Tracker(res, begin=start, end=stop)
                go = Video(k, trk, loop, jumps, selection_regions_json=selection_regions_json, frag_id=self.frag_id)

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

    def get_or_create_frag_id(self):
        if not self.go:
            return None
        return self.go.get_or_create_frag_id()

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

        self.go.seek(frame)

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

    def keydown(self, key, mod, keys_down=None):
        if not self.go:
            return

        self.go.keydown(key, mod, keys_down)

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


class HeadlessPlayer:
    """A non-UI, audio-only player for a single fragment."""
    def __init__(self, k, frag_id, volume=1.0):
        self.k = k
        self.frag_id = frag_id
        self.playing = None
        self.trk = None
        self.volume = volume
        print(f"    [HeadlessPlayer] Initializing for frag {self.frag_id}")

        try:
            frag = kdb.get_frag(self.frag_id)
            frag_type = frag['media']
            source = frag['source']
            start = frag['start']
            stop = frag['stop']

            if frag_type == kdb.MEDIA_VIDEO:
                # TODO: This creates a new Resource for every loop player.
                # A shared resource cache would be more efficient to avoid
                # reloading the same audio file multiple times. For now,
                # this is functionally correct.
                res = Resource(source, imagine=None, audio_only=True)
                self.trk = Tracker(res, begin=start, end=stop)
                if self.trk:
                    self.trk.res.audio.set_volume(self.volume)
                print(f"    [HeadlessPlayer] Successfully initialized.")
            else:
                # Silently fail for unsupported media, as this is a background player
                print(f'LoopPlayer: frag {frag_id} has unsupported media type: {frag_type}')

        except Exception as e:
            print(f'!!! HeadlessPlayer failed to init for frag {frag_id}: {e}')
            self.trk = None

    def play(self):
        if self.playing or not self.trk:
            return
        print(f"    [HeadlessPlayer] Play called for frag {self.frag_id}")
        self.trk.play()
        self.playing = True

    def pause(self):
        if self.playing is False or not self.trk:
            return
        print(f"    [HeadlessPlayer] Pause called for frag {self.frag_id}")
        self.trk.pause()
        self.playing = False

    def stop(self):
        if self.playing is None or not self.trk:
            return
        print(f"    [HeadlessPlayer] Stop called for frag {self.frag_id}")
        self.trk.stop()
        self.playing = None

    def seek(self, frame):
        if not self.trk:
            return
        # The frame for seek is recorded from the main player's tracker.
        # Tracker.seek handles clamping it to its own begin/end bounds.
        self.trk.seek(frame)

    def tick(self):
        """ This is the audio-only tick, delegating to the now audio-safe Tracker. """
        if self.playing is None or not self.trk:
            return None # Finished or failed

        # Rely on the canonical Tracker.tick(), which is now safe for audio-only resources.
        tock = self.trk.tick()

        # Sync our state with the tracker's state after the tick.
        self.playing = self.trk.playing

        # A return value of None from trk.tick() signifies the tracker has finished and reset.
        return tock

    def kill(self, replace=False):
        print(f"    [HeadlessPlayer] Kill called for frag {self.frag_id}")
        if self.trk:
            self.stop()
            self.trk.res.kill()
            self.trk = None
