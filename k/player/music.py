from k.ui import *
import io
# from just_playback import Playback  <- No longer used for individual note playback

import pygame

try:
    from pydub import AudioSegment
    from pydub.exceptions import CouldntDecodeError
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    CouldntDecodeError = None # Define for exception handling even if pydub is missing


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

        self.active_notes = {}  # {pygame_key: pygame.mixer.Channel}
        self.original_volume = None

        self.key_to_semitone = {
            # White keys (C scale starting from 'a')
            pygame.K_a: 0,   # C
            pygame.K_s: 2,   # D
            pygame.K_d: 4,   # E
            pygame.K_f: 5,   # F
            pygame.K_g: 7,   # G
            pygame.K_h: 9,   # A
            pygame.K_j: 11,  # B
            pygame.K_k: 12,  # C'

            # Black keys
            pygame.K_w: 1,   # C#
            pygame.K_e: 3,   # D#
            pygame.K_t: 6,   # F#
            pygame.K_y: 8,   # G#
            pygame.K_u: 10,  # A#
        }
        self.qwerty_keys = set(self.key_to_semitone.keys())

    def toggle(self):
        """Engages or disengages music mode."""
        if not self.active:
            self.engage()
        else:
            self.disengage()

        print(f'music mode is {"ON" if self.active else "OFF"}')
        self.k.status('M' if self.active else 'N')

    def engage(self):
        """Attempts to capture an audio sample to enable music mode."""
        print("Attempting to engage Music Mode...")
        pygame.mixer.init()
        if not PYDUB_AVAILABLE:
            print("ERROR: pydub library not found. Music Mode is disabled.")
            self.active = False
            return

        success = False
        if self.k.player.players:
            player = self.k.player.players[-1]
            actual_player = getattr(player, 'go', player)

            if hasattr(actual_player, 'trk') and actual_player.trk and hasattr(actual_player.trk, 'res'):
                trk = actual_player.trk
                res = trk.res
                afn = res.afn
                fps = res.fps

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

                start_ms = (start_frame / fps) * 1000
                end_ms = (end_frame / fps) * 1000

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
        if not success:
            self.sample = None

    def disengage(self):
        """Disables music mode and clears the audio sample."""
        self.active = False
        self.sample = None
        for channel in self.active_notes.values():
            if channel:
                channel.stop()
        self.active_notes.clear()

        if self.original_volume is not None:
            if self.k.player.players:
                player = self.k.player.players[-1]
                actual_player = getattr(player, 'go', player)
                if hasattr(actual_player, 'trk') and hasattr(actual_player.trk, 'res'):
                    actual_player.trk.res.audio.set_volume(self.original_volume)
                    actual_player.music_mode_override = False
            self.original_volume = None

    def tick(self):
        """Called every frame. Looping for held notes is now handled by pygame.mixer."""
        if not self.active:
            return
        # Looping is handled by `sound.play(loops=-1)`, so the manual
        # re-triggering logic from just_playback is no longer needed.
        pass

    def keydown(self, key):
        """Handles a key press event when music mode is active."""
        if key not in self.qwerty_keys or not self.sample or key in self.active_notes:
            return False

        # First key press in music mode, mute main player and set up override loop
        if not self.active_notes and self.k.player.players:
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

        # Stop any other playing notes before starting a new one.
        for channel in self.active_notes.values():
            if channel:
                channel.stop()
        self.active_notes.clear()

        semitones = self.key_to_semitone.get(key, 0)

        try:
            # Pitch shift using pydub by changing the sample rate
            rate = self.sample.frame_rate * (2 ** (semitones / 12.0))
            shifted_sample = self.sample._spawn(self.sample.raw_data, overrides={"frame_rate": int(rate)})

            # Play from memory using pygame.mixer
            audio_stream = io.BytesIO()
            shifted_sample.export(audio_stream, format="wav")
            audio_stream.seek(0)

            sound = pygame.mixer.Sound(audio_stream)
            channel = sound.play(loops=-1) # Loop indefinitely until keyup

            self.active_notes[key] = channel
            print(f"Playing note: {pygame.key.name(key)} ({semitones} semitones)")
            return True  # Event handled
        except Exception as e:
            self.k.bug(e)
            return False

    def keyup(self, key):
        """Handles a key release event when music mode is active."""
        if key in self.active_notes:
            channel = self.active_notes.pop(key)
            if channel:
                channel.stop()

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