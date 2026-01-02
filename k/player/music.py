from k.ui import *
import io
# from just_playback import Playback  <- No longer used for individual note playback

import pygame
import os
import sys
import traceback

try:
    from pydub import AudioSegment
    from pydub.exceptions import CouldntDecodeError
    import pydub.utils
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    CouldntDecodeError = None # Define for exception handling even if pydub is missing
    AudioSegment = None
    pydub = None


class Mode:
    """
    Encapsulates all logic and state for the Auto-Tune Music Mode.
    """
    def __init__(self, k):
        self.k = k
        self.active = False
        self.sample = None
        self.sample_start_frame = 0
        self.sample_end_frame = 0
        self.base_fps = 0

        self.active_notes = {}  # {pygame_key: {'channel': Channel, 'start_ticks': int, ...}}
        self.original_volume = None
        self.slotted_samples = {}

        self.ffmpeg_checked = False
        self.ffmpeg_available = False

        # This mapping provides a two-octave+ range based on a standard virtual
        # piano layout for QWERTY keyboards.
        self.key_to_semitone = {
            # High octave (starts at C=0 as requested)
            pygame.K_q: 0,   # C
            pygame.K_w: 2,   # D
            pygame.K_e: 4,   # E
            pygame.K_r: 5,   # F
            pygame.K_t: 7,   # G
            pygame.K_y: 9,   # A
            pygame.K_u: 11,  # B
            pygame.K_i: 12,  # C'
            pygame.K_o: 14,  # D'
            pygame.K_p: 16,  # E'

            # Low octave (one octave down)
            pygame.K_z: -12, # C
            pygame.K_s: -11, # C#
            pygame.K_x: -10, # D
            pygame.K_d: -9,  # D#
            pygame.K_c: -8,  # E
            pygame.K_v: -7,  # F
            pygame.K_g: -6,  # F#
            pygame.K_b: -5,  # G
            pygame.K_h: -4,  # G#
            pygame.K_n: -3,  # A
            pygame.K_j: -2,  # A#
            pygame.K_m: -1,  # B
        }
        self.qwerty_keys = set(self.key_to_semitone.keys())

    def toggle(self):
        """Engages or disengages music mode."""
        if not self.active:
            self.engage()
        else:
            self.disengage()

        print(f'music mode is {"ON" if self.active else "OFF"}')
        self.k.status('U' if self.active else 'N')

    def engage(self):
        """Attempts to capture an audio sample to enable music mode."""
        print("Attempting to engage Music Mode...")
        pygame.mixer.init()

        if not PYDUB_AVAILABLE:
            print("ERROR: pydub library not found. Music Mode is disabled.")
            self.active = False
            return

        if not self.ffmpeg_checked:
            self.ffmpeg_checked = True # Check only once

            # On Windows, pydub may have trouble finding ffmpeg.
            # We can try to set the path explicitly if ffmpeg.exe is in the project root.
            if sys.platform == "win32":
                try:
                    # Prefer the bundled executables if they exist.
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    ffmpeg_path = os.path.join(project_root, "ffmpeg.exe")
                    ffprobe_path = os.path.join(project_root, "ffprobe.exe")
                    if os.path.exists(ffmpeg_path):
                        AudioSegment.converter = ffmpeg_path
                    if os.path.exists(ffprobe_path):
                        AudioSegment.ffprobe = ffprobe_path
                except Exception as e:
                    print(f"Could not set pydub ffmpeg path: {e}")

            try:
                pydub.utils.get_prober_name() # This will raise if not found
                self.ffmpeg_available = True
                print("pydub backend (ffmpeg) found. Music mode time correction is enabled.")
            except (IOError, OSError):
                self.ffmpeg_available = False
                print("\n" + "="*60)
                print("WARNING: pydub backend (ffmpeg/avlib) not found.")
                print("Music Mode pitch shifting will not have time correction,")
                print("resulting in 'chipmunk' or slowed-down audio effects.")
                print("\nTo fix this on Windows:")
                print("1. Download ffmpeg from https://ffmpeg.org/download.html")
                print("   (e.g., the 'gyan.dev' Full Build is a good choice)")
                print("2. Unzip the file, and find the 'bin' folder inside.")
                print("3. Copy 'ffmpeg.exe' and 'ffprobe.exe' from the 'bin' folder")
                print("   into the root directory of this 'k' project.")
                print("="*60 + "\n")


        success = False
        if self.k.player.players:
            player = self.k.player.players[-1]
            actual_player = getattr(player, 'go', player)

            if hasattr(actual_player, 'trk') and actual_player.trk and hasattr(actual_player.trk, 'res'):
                trk = actual_player.trk
                res = trk.res
                afn = res.afn
                self.base_fps = res.fps

                selection_made = (hasattr(actual_player, 'loop_begin') and actual_player.loop_begin > 0) or \
                                 (hasattr(actual_player, 'loop_end') and actual_player.loop_end < trk.frames - 1)

                if selection_made:
                    print("Using selection for audio capture.")
                    start_frame = trk.begin + actual_player.loop_begin
                    end_frame = trk.begin + actual_player.loop_end
                else:
                    print("No selection, using entire clip for audio capture.")
                    start_frame = trk.begin
                    end_frame = trk.end

                self.sample_start_frame = start_frame
                self.sample_end_frame = end_frame

                start_ms = (start_frame / self.base_fps) * 1000
                end_ms = (end_frame / self.base_fps) * 1000

                try:
                    print(f"Capturing audio from {afn} between {start_ms:.2f}ms and {end_ms:.2f}ms")
                    audio = AudioSegment.from_file(afn)
                    self.sample = audio[start_ms:end_ms]
                    print(f"Successfully captured {len(self.sample)}ms audio sample.")
                    success = True
                except (FileNotFoundError, CouldntDecodeError) as e:
                    print(f"ERROR: Could not load or decode audio file '{afn}': {e}")
                except Exception as e:
                    self.k.bug(e)
            else:
                print("Music Mode requires an active clip player.")
        else:
            print("No active player to capture audio from.")

        self.active = success
        if success:
            # Pre-cache existing slots after successful engagement
            print("Pre-caching audio for existing selection slots...")
            if hasattr(actual_player, 'selection_regions'):
                for slot_key in actual_player.selection_regions.keys():
                    self.cache_sample_for_slot(slot_key, actual_player)

        if not success:
            self.sample = None

    def disengage(self):
        """Disables music mode and clears the audio sample."""
        self.active = False
        self.sample = None
        #self.slotted_samples.clear()
        for note_data in self.active_notes.values():
            if note_data['channel']:
                note_data['channel'].stop()
        self.active_notes.clear()

        if self.original_volume is not None:
            if self.k.player.players:
                player = self.k.player.players[-1]
                actual_player = getattr(player, 'go', player)
                if hasattr(actual_player, 'trk') and hasattr(actual_player.trk, 'res'):
                    actual_player.trk.res.audio.set_volume(self.original_volume)
                    actual_player.music_mode_override = False
            self.original_volume = None

    def clear_cache(self):
        """Clears all cached audio samples."""
        self.slotted_samples.clear()
        self.sample = None
        print("Music mode audio cache cleared.")

    def cache_sample_for_slot(self, slot_key, player_instance):
        """Caches an audio segment for a given selection slot key."""
        if not (hasattr(player_instance, 'selection_regions') and slot_key in player_instance.selection_regions):
            return

        if hasattr(player_instance, 'trk') and player_instance.trk and hasattr(player_instance.trk, 'res'):
            trk = player_instance.trk
            res = trk.res
            afn = res.afn
            base_fps = res.fps

            loop_begin, loop_end = player_instance.selection_regions[slot_key]
            start_frame = trk.begin + loop_begin
            end_frame = trk.begin + loop_end

            # Check if a valid cache for this exact selection already exists.
            if slot_key in self.slotted_samples:
                cached_data = self.slotted_samples[slot_key]
                if cached_data['start_frame'] == start_frame and cached_data['end_frame'] == end_frame:
                    # The cache is for the same frames, so we assume it's valid.
                    # The cache is cleared when the player is killed, so we don't need to check afn.
                    print(f"Audio for slot {pygame.key.name(slot_key)} already cached. Skipping.")
                    return # Already cached, do nothing.

            start_ms = (start_frame / base_fps) * 1000
            end_ms = (end_frame / base_fps) * 1000

            try:
                audio = AudioSegment.from_file(afn)
                sample = audio[start_ms:end_ms]
                self.slotted_samples[slot_key] = {
                    'sample': sample,
                    'start_frame': start_frame,
                    'end_frame': end_frame,
                    'base_fps': base_fps
                }
                print(f"Audio for slot {pygame.key.name(slot_key)} cached ({len(sample)}ms).")
            except (FileNotFoundError, CouldntDecodeError) as e:
                print(f"ERROR: Could not load or decode audio for slot {pygame.key.name(slot_key)}: {e}")
            except Exception as e:
                self.k.bug(e)

    def load_slotted_sample(self, slot_key):
        """Loads a cached audio sample for music playback."""
        player = self.k.player.players[-1]
        actual_player = getattr(player, 'go', player)

        # First, ensure the sample is cached if it's not already.
        if slot_key not in self.slotted_samples and hasattr(actual_player, 'selection_regions'):
            if slot_key in actual_player.selection_regions:
                print(f"Sample for slot {pygame.key.name(slot_key)} not cached. Caching now...")
                self.cache_sample_for_slot(slot_key, actual_player)
            else:
                 print(f"Cannot cache sample for slot {pygame.key.name(slot_key)}: No selection region found.")
                 return

        # Now, try to load it.
        if slot_key in self.slotted_samples:
            data = self.slotted_samples[slot_key]
            self.sample = data['sample']
            self.sample_start_frame = data['start_frame']
            self.sample_end_frame = data['end_frame']
            self.base_fps = data['base_fps']

            # Stop any currently playing note before swapping
            for note_data in self.active_notes.values():
                if note_data['channel']:
                    note_data['channel'].stop()
            self.active_notes.clear()

            print(f"Loaded audio sample from slot {pygame.key.name(slot_key)}.")
        else:
            print(f"Failed to load audio sample for slot {pygame.key.name(slot_key)}.")

    def tick(self):
        """Called every frame. Looping for held notes is now handled by pygame.mixer."""
        if not self.active:
            return
        # Looping is handled by `sound.play(loops=-1)`, so the manual
        # re-triggering logic from just_playback is no longer needed.
        pass

    def _get_current_pos_ms(self):
        """Calculates the current playback position in milliseconds."""
        if not self.active_notes:
            return 0

        # Assuming only one note can be active at a time
        try:
            key = list(self.active_notes.keys())[0]
            note_data = self.active_notes[key]
        except (IndexError, KeyError):
            return 0

        if not note_data['channel'].get_busy():
            return 0

        elapsed_ms = pygame.time.get_ticks() - note_data['start_ticks']

        # The sample itself might have been started from an offset
        # because of how _play_note cyclically shifts the buffer.
        # So we add the initial offset to the elapsed time.
        total_pos_ms = elapsed_ms + note_data['start_offset_ms']

        sample_len_ms = note_data['sample_len_ms']
        if sample_len_ms > 0:
            return total_pos_ms % sample_len_ms

        return total_pos_ms

    def _play_note(self, key, start_ms=0):
        """Stops any current note and plays a new one from a given start time."""
        for note_data in self.active_notes.values():
            if note_data['channel']:
                note_data['channel'].stop()
        self.active_notes.clear()

        semitones = self.key_to_semitone.get(key, 0)

        try:
            shifted_sample = self._get_pitched_sample(semitones)
            if not shifted_sample:
                return

            final_sample = shifted_sample
            sample_len_ms = len(shifted_sample)

            play_from_pos_ms = 0
            if start_ms > 0 and sample_len_ms > 0:
                play_from_pos_ms = start_ms % sample_len_ms
                part1 = shifted_sample[play_from_pos_ms:]
                part2 = shifted_sample[:play_from_pos_ms]
                final_sample = part1 + part2

            # Play from memory using pygame.mixer
            audio_stream = io.BytesIO()
            final_sample.export(audio_stream, format="wav")
            audio_stream.seek(0)

            sound = pygame.mixer.Sound(audio_stream)
            channel = sound.play(loops=-1) # Loop indefinitely until keyup

            if channel:
                self.active_notes[key] = {
                    'channel': channel,
                    'start_ticks': pygame.time.get_ticks(),
                    'sample_len_ms': sample_len_ms,
                    'start_offset_ms': play_from_pos_ms
                }
            print(f"Playing note: {pygame.key.name(key)} ({semitones} semitones) from {start_ms:.2f}ms")
        except Exception as e:
            self.k.bug(e)

    def _get_pitched_sample(self, semitones):
        """Applies pitch shifting to the base audio sample."""
        if not self.sample:
            return None

        try:

            if semitones == 0:
                shifted_sample = self.sample
            else:
                # Naively change pitch and speed by modifying the sample rate.
                ratio = 2.0 ** (semitones / 12.0)
                pitched_sample = self.sample._spawn(self.sample.raw_data, overrides={
                    "frame_rate": int(self.sample.frame_rate * ratio)
                })

                if self.ffmpeg_available:
                    try:
                        # Time-stretch the audio back to its original duration to correct the speed.
                        playback_speed = 1.0 / ratio

                        # When up-shifting pitch, playback_speed is < 1.0 (slowing down).
                        # FFmpeg's 'atempo' filter, used by pydub's speedup, has a valid
                        # range of [0.5, 100.0]. Values outside this range will fail.
                        # Pydub does not automatically chain filters, so for extreme
                        # slowdowns (playback_speed < 0.5), we must do it manually.
                        if playback_speed >= 0.5:
                            # This covers all down-shifting (playback_speed > 1.0) and
                            # moderate up-shifting.
                            shifted_sample = pitched_sample.speedup(playback_speed=playback_speed)
                        else:
                            # Handle extreme up-shifting (requires slowdown < 0.5) by
                            # chaining multiple 'atempo' filters.
                            temp_sample = pitched_sample
                            while playback_speed < 0.5:
                                temp_sample = temp_sample.speedup(playback_speed=0.5)
                                playback_speed /= 0.5
                            shifted_sample = temp_sample.speedup(playback_speed=playback_speed)
                    except Exception as time_stretch_error:
                        print(f"WARNING: pydub/ffmpeg failed time-stretch for {semitones} semitones. Audio speed will be incorrect. Error: {time_stretch_error}")
                        shifted_sample = pitched_sample
                else:
                    # No time correction available, use the pitch-shifted but speed-altered sample.
                    shifted_sample = pitched_sample

            return shifted_sample
        except Exception as e:
            self.k.bug(e)
            return None

    def keydown(self, key):
        """Handles a key press event when music mode is active."""
        if key not in self.qwerty_keys or not self.sample or key in self.active_notes:
            return False

        if self.k.f_key_capturing:
            from k.player.actions import PlayerNoteOn
            self.k.f_key_current_actions.append(PlayerNoteOn(key))

        current_pos_ms = 0
        is_pitch_change = bool(self.active_notes)

        # First key press in music mode: mute main player and set up override loop.
        if not is_pitch_change and self.k.player.players:
            player = self.k.player.players[-1]
            actual_player = getattr(player, 'go', player)

            self.original_volume = actual_player.trk.res.audio.volume
            actual_player.trk.res.audio.set_volume(0.0)

            # Set temporary loop override on the player
            loop_start_relative = self.sample_start_frame - actual_player.trk.begin
            loop_end_relative = self.sample_end_frame - actual_player.trk.begin
            actual_player.music_mode_override = True
            actual_player.music_mode_loop_begin = loop_start_relative
            actual_player.music_mode_loop_end = loop_end_relative
            actual_player.seek(loop_start_relative)

        # If a note is already playing (pitch change), get its current position.
        if is_pitch_change:
            current_pos_ms = self._get_current_pos_ms()

        self._play_note(key, start_ms=current_pos_ms)
        return True  # Event handled

    def seek_by_frame(self, absolute_frame):
        """Seeks the currently playing audio sample to a new position based on a video frame."""
        if not self.active or not self.active_notes:
            return

        frame_offset = absolute_frame - self.sample_start_frame
        pos_ms = (frame_offset / self.base_fps) * 1000 if self.base_fps > 0 else 0
        if pos_ms < 0:
            pos_ms = 0

        # Efficiency check: don't re-seek if already close to the target position.
        try:
            key = list(self.active_notes.keys())[0]
            note_data = self.active_notes[key]
        except (IndexError, KeyError):
            return

        current_pos_ms = self._get_current_pos_ms()
        sample_len_ms = note_data['sample_len_ms']

        if sample_len_ms > 0 and abs((current_pos_ms % sample_len_ms) - (pos_ms % sample_len_ms)) < 50: # 50ms threshold
            return

        self._play_note(key, start_ms=pos_ms)

    def keyup(self, key):
        """Handles a key release event when music mode is active."""
        if key in self.active_notes:
            if self.k.f_key_capturing:
                from k.player.actions import PlayerNoteOff
                self.k.f_key_current_actions.append(PlayerNoteOff(key))

            note_data = self.active_notes.pop(key)
            if note_data['channel']:
                note_data['channel'].stop()

            print(f"Stopping note: {pygame.key.name(key)}")

            # Last key released, restore main player audio and behavior
            if not self.active_notes and self.original_volume is not None:
                if self.k.player.players:
                    player = self.k.player.players[-1]
                    actual_player = getattr(player, 'go', player)
                    actual_player.trk.res.audio.set_volume(self.original_volume)
                    actual_player.music_mode_override = False
                self.original_volume = None
            return True
        return False
