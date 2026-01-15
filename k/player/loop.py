from k.ui import *
import time
from k.replay.ops import Action, PRECISION
from k.player.actions import *
from .frag import HeadlessPlayer

import io
import traceback
import json
import os
import k.storage as media
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class MicroMusicPlayer:
    """A lightweight, self-contained version of music.Mode for loop playback."""
    def __init__(self, sample, base_fps, ffmpeg_available, volume=1.0):
        pygame.mixer.init()  # Ensure mixer is ready
        self.sample = sample
        self.base_fps = base_fps
        self.ffmpeg_available = ffmpeg_available
        self.volume = volume
        self.active_notes = {}
        # This mapping is copied from k/player/music.py
        self.key_to_semitone = {
            pygame.K_q: 0, pygame.K_w: 2, pygame.K_e: 4, pygame.K_r: 5, pygame.K_t: 7,
            pygame.K_y: 9, pygame.K_u: 11, pygame.K_i: 12, pygame.K_o: 14, pygame.K_p: 16,
            pygame.K_z: -12, pygame.K_s: -11, pygame.K_x: -10, pygame.K_d: -9, pygame.K_c: -8,
            pygame.K_v: -7, pygame.K_g: -6, pygame.K_b: -5, pygame.K_h: -4, pygame.K_n: -3,
            pygame.K_j: -2, pygame.K_m: -1,
        }

    def keydown(self, key):
        if key not in self.key_to_semitone or not self.sample or key in self.active_notes:
            return False
        current_pos_ms = self._get_current_pos_ms() if self.active_notes else 0
        self._play_note(key, start_ms=current_pos_ms)
        return True

    def keyup(self, key):
        if key in self.active_notes:
            note_data = self.active_notes.pop(key)
            if note_data['channel']:
                note_data['channel'].stop()
            return True
        return False

    def kill(self):
        for note_data in self.active_notes.values():
            if note_data['channel']:
                note_data['channel'].stop()
        self.active_notes.clear()

    def update_active_note_volume(self):
        for note_data in self.active_notes.values():
            if note_data['channel']:
                note_data['channel'].set_volume(self.volume)

    def _get_current_pos_ms(self):
        if not self.active_notes: return 0
        try:
            key = list(self.active_notes.keys())[0]
            note_data = self.active_notes[key]
        except (IndexError, KeyError): return 0
        if not note_data['channel'].get_busy(): return 0
        elapsed_ms = pygame.time.get_ticks() - note_data['start_ticks']
        total_pos_ms = elapsed_ms + note_data['start_offset_ms']
        sample_len_ms = note_data['sample_len_ms']
        return (total_pos_ms % sample_len_ms) if sample_len_ms > 0 else total_pos_ms

    def _play_note(self, key, start_ms=0):
        self.kill() # Stop current note
        semitones = self.key_to_semitone.get(key, 0)
        try:
            shifted_sample = self._get_pitched_sample(semitones)
            if not shifted_sample: return

            final_sample, sample_len_ms = shifted_sample, len(shifted_sample)
            play_from_pos_ms = (start_ms % sample_len_ms) if start_ms > 0 and sample_len_ms > 0 else 0
            if play_from_pos_ms > 0:
                final_sample = shifted_sample[play_from_pos_ms:] + shifted_sample[:play_from_pos_ms]

            audio_stream = io.BytesIO()
            final_sample.export(audio_stream, format="wav")
            audio_stream.seek(0)
            sound = pygame.mixer.Sound(audio_stream)
            channel = sound.play(loops=-1)
            if channel:
                channel.set_volume(self.volume)
                self.active_notes[key] = {
                    'channel': channel, 'start_ticks': pygame.time.get_ticks(),
                    'sample_len_ms': sample_len_ms, 'start_offset_ms': play_from_pos_ms}
        except Exception as e:
            print(f"ERROR in MicroMusicPlayer: {e}")
            traceback.print_exc()

    def _get_pitched_sample(self, semitones):
        if not self.sample: return None
        if not PYDUB_AVAILABLE: return self.sample
        try:
            if semitones == 0: return self.sample
            ratio = 2.0 ** (semitones / 12.0)
            pitched_sample = self.sample._spawn(self.sample.raw_data, overrides={"frame_rate": int(self.sample.frame_rate * ratio)})
            if self.ffmpeg_available:
                try:
                    playback_speed = 1.0 / ratio
                    if playback_speed >= 0.5:
                        return pitched_sample.speedup(playback_speed=playback_speed)
                    else:
                        temp_sample = pitched_sample
                        while playback_speed < 0.5:
                            temp_sample = temp_sample.speedup(playback_speed=0.5)
                            playback_speed /= 0.5
                        return temp_sample.speedup(playback_speed=playback_speed)
                except Exception as e:
                    print(f"WARNING: pydub/ffmpeg failed time-stretch. Audio speed will be incorrect. {e}")
            return pitched_sample
        except Exception as e:
            print(f"ERROR in _get_pitched_sample: {e}")
            traceback.print_exc()
            return None


class LoopPlayer:
    """
    A lightweight, audio-only player that consumes a recorded list of actions
    to create a repeatable audio loop.
    """
    def __init__(self, k, key, actions, duration, music_context=None, volume=1.0):
        self.k = k
        self.key = key
        self.actions = list(actions)  # Make a copy
        self.duration = duration
        self.volume = volume
        self.internal_player_muted = False
        self.relative_volume = 1.0
        self.music_relative_volume = 1.0
        self.internal_player = None
        self.music_player = None

        loaded_sample = None
        base_fps = None

        if PYDUB_AVAILABLE and isinstance(music_context, str):
            try:
                if music_context.endswith('.wav') and os.path.exists(music_context):
                    loaded_sample = AudioSegment.from_file(music_context)
                else:
                    context = json.loads(music_context)
                    video_id, start_frame, end_frame, base_fps = context['source_video_id'], context['start_frame'], context['end_frame'], context['base_fps']
                    audio_path = media.get_audio(video_id)
                    if audio_path and os.path.exists(audio_path):
                        full_audio = AudioSegment.from_file(audio_path)
                        start_ms = start_frame * 1000 / base_fps
                        end_ms = end_frame * 1000 / base_fps
                        loaded_sample = full_audio[int(start_ms):int(end_ms)]
                    else:
                        print(f"ERROR: Could not find audio for video {video_id} at {audio_path}")
            except Exception as e:
                print(f"ERROR loading music context from for loop player: {e}")
                traceback.print_exc()
        elif isinstance(music_context, dict): # Live object from in-session loop
            loaded_sample = music_context['sample']
            base_fps = music_context['base_fps']

        if loaded_sample:
             self.music_player = MicroMusicPlayer(
                loaded_sample,
                base_fps,
                k.music.ffmpeg_available,
                self.volume
            )

        self.action_index = 0
        self.start_time = 0
        #self.first_action_time = self.actions[0].t if self.actions else 0
        self.loop = True
        self.key_name = pygame.key.name(self.key).upper()
        self.will_loop = False
        self.speed = 1.0
        self.direction = 1

    def play(self):
        self.action_index = 0
        self.start_time = time.perf_counter()
        if self.internal_player:
            self.internal_player.kill()
            self.internal_player = None
        if self.music_player:
            self.music_player.kill()
        self.internal_player_muted = False
        self.relative_volume = 1.0
        self.music_relative_volume = 1.0
        self.speed = 1.0
        self.direction = 1
        #print(f"[LoopPlayer:{self.key_name}] Starting loop.")

    def set_volume(self, volume):
        self.volume = volume
        self.apply_internal_player_volume()
        self.apply_music_player_volume()

    def apply_internal_player_volume(self):
        if self.internal_player and self.internal_player.trk:
            combined_volume = self.volume * self.relative_volume
            if not self.internal_player_muted:
                self.internal_player.trk.res.audio.set_volume(combined_volume)
            else:
                self.internal_player.trk.res.audio.set_volume(0.0)

    def apply_music_player_volume(self, note_volume=None):
        if self.music_player:
            base_vol = note_volume if note_volume is not None else self.music_relative_volume
            self.music_player.volume = self.volume * base_vol
            self.music_player.update_active_note_volume()

    def tick(self):
        # Tick the audio of the currently playing internal player, if any
        if self.internal_player and self.internal_player.playing is not None:
            tock = self.internal_player.tick()
            if tock is None: # Player finished or was killed
                #print(f"[LoopPlayer:{self.key_name}] Internal player finished.")
                self.internal_player.kill()
                self.internal_player = None

        if not self.actions:
            return

        now = time.perf_counter()
        elapsed = now - self.start_time

        # Check if we are about to loop to update the UI indicator
        loop_lookahead_time = 0.1  # 100ms
        if self.loop and self.duration > 0:
            time_until_loop = self.duration - elapsed
            if 0 < time_until_loop <= loop_lookahead_time:
                self.will_loop = True
            else:
                self.will_loop = False
        else:
            self.will_loop = False

        # Check if the loop needs to restart based on its total duration
        if self.loop and self.duration > 0 and elapsed >= self.duration:
            # Adjust start time for smooth looping without drift
            self.start_time += self.duration
            elapsed = now - self.start_time
            self.action_index = 0
            if self.music_player:
                self.music_player.kill()
            #print(f"[LoopPlayer:{self.key_name}] Loop restarting.")
            # We don't kill the internal_player here. The first PlayerPlay action
            # in the loop will handle re-seeking or recreating it efficiently.

        if self.action_index >= len(self.actions) and not self.loop:
            return

        # This part needs to be a loop to catch up on missed/simultaneous actions
        while self.action_index < len(self.actions):
            action = self.actions[self.action_index]
            # Action timestamps are integer microseconds. Convert to float seconds for comparison.
            action_time = action.t / PRECISION

            if elapsed >= action_time:
                # Execute action
                #print(f"[LoopPlayer:{self.key_name}] T+{elapsed:.3f}s :: Executing {type(action).__name__} (scheduled at {action_time:.3f}s)")
                if isinstance(action, PlayerSetVolume):
                    self.relative_volume = action.volume
                    self.apply_internal_player_volume()
                elif isinstance(action, PlayerSetMusicVolume):
                    self.music_relative_volume = action.volume
                    self.apply_music_player_volume()
                elif isinstance(action, PlayerPlay):
                    # Re-create player only if necessary
                    if not (self.internal_player and self.internal_player.trk and self.internal_player.frag_id == action.frag_id):
                        if self.internal_player:
                            self.internal_player.kill()
                        self.internal_player = HeadlessPlayer(self.k, action.frag_id, 1.0)

                    if self.internal_player and self.internal_player.trk: # Check for successful initialization
                        self.internal_player.trk.set_speed(self.speed)
                        self.internal_player.trk.set_direction(self.direction)
                        start_frame = action.start_frame if action.start_frame is not None else self.internal_player.trk.begin
                        self.internal_player.seek(start_frame)
                        self.internal_player.play()
                        self.apply_internal_player_volume()
                    else:
                        self.internal_player = None  # Failed to load
                elif isinstance(action, PlayerNoteOn) and self.music_player:
                    if not self.music_player.active_notes:  # First note is starting
                        self.internal_player_muted = True
                        self.apply_internal_player_volume()
                    
                    note_volume = getattr(action, 'volume', self.music_relative_volume)
                    self.apply_music_player_volume(note_volume=note_volume)
                    self.music_player.keydown(action.key)
                elif isinstance(action, PlayerNoteOff) and self.music_player:
                    self.music_player.keyup(action.key)
                    if not self.music_player.active_notes:  # Last note was released
                        self.internal_player_muted = False
                        self.apply_internal_player_volume()
                elif isinstance(action, PlayerPlaybackSpeed):
                    self.speed = action.speed
                    self.direction = action.direction
                    if self.internal_player and self.internal_player.trk:
                        self.internal_player.trk.set_speed(self.speed)
                        self.internal_player.trk.set_direction(self.direction)
                elif self.internal_player and self.internal_player.trk:
                    if isinstance(action, PlayerPause):
                        #print("    -> Pausing playback")

                        self.internal_player.pause()
                    elif isinstance(action, PlayerStop):
                        #print("    -> Stopping playback")

                        self.internal_player.stop()
                    elif isinstance(action, PlayerSeek):
                        #print(f"    -> Seeking to frame: {action.frame}")
                        self.internal_player.seek(action.frame)

                self.action_index += 1
            else:
                # Next action is in the future, so we can stop checking for now.
                break

    def kill(self):
        #print(f"[LoopPlayer:{self.key_name}] Kill called.")
        if self.internal_player:
            self.internal_player.kill()
        if self.music_player:
            self.music_player.kill()