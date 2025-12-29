from k.ui import *
import time
from k.replay.ops import Action
from k.player.actions import PlayerPlay, PlayerPause, PlayerStop, PlayerSeek
from .frag import Chaos


class LoopPlayer:
    """
    A lightweight, audio-only player that consumes a recorded list of actions
    to create a repeatable audio loop.
    """
    def __init__(self, k, key, actions):
        self.k = k
        self.key = key
        self.actions = list(actions)  # Make a copy
        self.internal_player = None
        self.action_index = 0
        self.start_time = 0
        self.first_action_time = self.actions[0].t if self.actions else 0
        self.loop = True

    def play(self):
        self.action_index = 0
        self.start_time = time.perf_counter()

    def tick(self):
        # Tick the audio of the currently playing internal player, if any
        if self.internal_player and self.internal_player.go and self.internal_player.playing is not None:
            # We don't need the full UI tick, just the underlying tracker tick for audio processing.
            # This also avoids video decoding overhead.
            tock = self.internal_player.go.trk.tick()
            if tock is None: # Tracker finished
                self.internal_player.kill()
                self.internal_player = None

        if not self.actions or (self.action_index >= len(self.actions) and not self.loop):
            return

        now = time.perf_counter()
        elapsed = now - self.start_time

        # This part needs to be a loop to catch up on missed/simultaneous actions
        while self.action_index < len(self.actions):
            action = self.actions[self.action_index]
            # Action timestamps are relative to the first action in the recording
            action_time = (action.t - self.first_action_time)

            if elapsed >= action_time:
                # Execute action
                if isinstance(action, PlayerPlay):
                    if self.internal_player:
                        self.internal_player.kill()
                    # The Chaos player handles creating its own Resource and Tracker
                    self.internal_player = Chaos(self.k, action.frag_id)
                    if self.internal_player.go:
                        self.internal_player.play()
                    else:
                        self.internal_player = None  # Failed to load
                elif self.internal_player and self.internal_player.go:
                    if isinstance(action, PlayerPause):
                        self.internal_player.pause()
                    elif isinstance(action, PlayerStop):
                        self.internal_player.stop()
                    elif isinstance(action, PlayerSeek):
                        self.internal_player.go.trk.seek(action.frame)
                
                self.action_index += 1
            else:
                # Next action is in the future, so we can stop checking for now.
                break

        if self.action_index >= len(self.actions) and self.loop:
            self.play() # Restart the loop

    def kill(self):
        if self.internal_player:
            self.internal_player.kill()