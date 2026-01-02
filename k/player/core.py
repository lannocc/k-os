from k.ui import *
import k.db as kdb
import k.storage as media

import cv2
from just_playback import Playback

from os.path import exists


def get_size_to_fit(orig_size, fit_size):
    width = fit_size[0]
    scale = width / orig_size[0]
    height = int(orig_size[1] * scale)

    if height > fit_size[1]:
        scale = fit_size[1] / orig_size[1]
        height = fit_size[1]
        width = int(orig_size[0] * scale)

    return (width, height)


class Resource():
    def __init__(self, video_id, imagine=None, audio_only=False):
        self.video_id = video_id
        self.ie = imagine
        self.audio_only = audio_only

        video = kdb.get_video(video_id)
        channel = kdb.get_channel(video['channel'])
        stream = kdb.list_video_streams(video_id)[0] #FIXME

        self.vfn = media.get_video_filename(channel['ytid'], video['ytid'],
            stream['itag'], stream['subtype'])
        print(f'loading video resource: {self.vfn} (audio_only={self.audio_only})')

        if self.audio_only:
            self.ie = None
            # For audio-only, we still need metadata from the video file.
            video_capture = cv2.VideoCapture(self.vfn)
            self.frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = video_capture.get(cv2.CAP_PROP_FPS)
            video_capture.release()
            self.video = None
            self.img = None
            self.size = (0, 0)
        elif self.ie:
            self.ie.fuel(self)
            self.img = True

        else:
            self.video = cv2.VideoCapture(self.vfn)
            self.frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.video.get(cv2.CAP_PROP_FPS)

            success, self.img = self.video.read()
            if not success:
                raise ValueError(f'failed loading first frame: {self.vfn}')

            self.size = self.img.shape[1::-1]

        self.frame = 0

        self.afn = media.get_audio_filename(channel['ytid'], video['ytid'])
        print(f'    [Resource] loading audio samples: {self.afn}')
        if not exists(self.afn):
            media.extract_audio(self.vfn, self.afn)
        self.audio = Playback()
        self.audio.load_file(self.afn)
        print(f'    [Resource] Audio loaded successfully.')

    def kill(self):
        if self.ie:
            self.ie.unplug(self)
        elif self.video:
            self.video.release()
        self.audio.stop()

    def get(self, frame, seeking=False):
        #if frame < 0 or frame >= self.frames:
        #    raise ValueError(f'seek to invalid frame: {frame}')

        if frame != self.frame:
            if not self.audio_only:
                if frame != self.frame + 1:
                    if self.ie:
                        self.ie.throttle(self, frame)
                    else:
                        self.video.set(cv2.CAP_PROP_POS_FRAMES, frame)

            self.frame = frame

            if not self.audio_only:
                if self.ie:
                    self.ie.rev()
                    self.img = True
                else:
                    success, self.img = self.video.read()
                    if not success:
                        raise RuntimeError(f'failed to read video frame: {frame}')

        #actual = self.audio.get_time()
        actual = self.audio.curr_pos
        needed = frame / self.fps
        if seeking or abs(needed - actual) > 0.1:
            if not seeking:
                print('audio resync')
            self.audio.seek(needed)

        return True if self.audio_only else self.img

    def play(self):
        if self.audio.paused:
            self.audio.resume()
        elif not self.audio.active:
            self.audio.play()

    def pause(self):
        self.audio.pause()

    def stop(self):
        self.audio.stop()


class Tracker():
    def __init__(self, resource, begin=0, end=None):
        self.res = resource

        self.begin = begin
        if end is None:
            self.frames = self.res.frames - begin
            self.end = self.frames - 1
        else:
            self.frames = end - begin + 1
            self.end = end

        self.resize = None
        self.size = self.res.size
        self.reset()

    def reset(self):
        self.clock = Clock(self.res.fps)
        self.frame = self.begin
        self.seeking = False

        self.img_orig = None
        self.img = None

        self.res.stop()
        self.playing = None

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
        #print(f'   trk seek: {frame}')

        #if frame < self.begin or frame > self.end:
        #    raise ValueError(f'seek to invalid frame: {frame}')
        if frame < self.begin:
            frame = self.begin
        elif frame > self.end:
            frame = self.end

        self.frame = frame
        self.seeking = True
        self.clock.reset()

    def tick(self):
        if self.playing is None:
            return None

        self.clock.tick()

        if not self.clock.ready():
            return False

        img = self.res.get(self.frame, self.seeking)
        self.seeking = False

        if self.img is None or img is not self.img_orig:
            if img is True:
                self.img_orig = img
                self.img = img
            else:
                if self.resize:
                    self.img = cv2.resize(img, self.resize)
                else:
                    self.img = img

                self.img_orig = img
                self.img = pygame.image.frombuffer(self.img.tobytes(),
                    self.size, "BGR")

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