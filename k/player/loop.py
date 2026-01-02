from k.ui import *
import time
from k.replay.ops import Action, PRECISION
from k.player.actions import PlayerPlay, PlayerPause, PlayerStop, PlayerSeek
from .frag import HeadlessPlayer


class LoopPlayer:
    """
    A lightweight, audio-only player that consumes a recorded list of actions
    to create a repeatable audio loop.
    """
    def __init__(self, k, key, actions, duration):
        self.k = k
        self.key = key
        self.actions = list(actions)  # Make a copy
        self.duration = duration
        self.internal_player = None
        self.action_index = 0
        self.start_time = 0
        self.first_action_time = self.actions[0].t if self.actions else 0
        self.loop = True
        self.key_name = pygame.key.name(self.key).upper()

    def play(self):
        self.action_index = 0
        self.start_time = time.perf_counter()
        if self.internal_player:
            self.internal_player.kill()
            self.internal_player = None
        print(f"[LoopPlayer:{self.key_name}] Starting loop.")

    def tick(self):
        # Tick the audio of the currently playing internal player, if any
        if self.internal_player and self.internal_player.playing is not None:
            tock = self.internal_player.tick()
            if tock is None: # Player finished or was killed
                print(f"[LoopPlayer:{self.key_name}] Internal player finished.")
                self.internal_player.kill()
                self.internal_player = None

        if not self.actions:
            return

        now = time.perf_counter()
        elapsed = now - self.start_time

        # Check if the loop needs to restart based on its total duration
        if self.loop and self.duration > 0 and elapsed >= self.duration:
            # Adjust start time for smooth looping without drift
            self.start_time += self.duration
            elapsed = now - self.start_time
            self.action_index = 0
            print(f"[LoopPlayer:{self.key_name}] Loop restarting.")
            # We don't kill the internal_player here. The first PlayerPlay action
            # in the loop will handle re-seeking or recreating it efficiently.

        if self.action_index >= len(self.actions) and not self.loop:
            return

        # This part needs to be a loop to catch up on missed/simultaneous actions
        while self.action_index < len(self.actions):
            action = self.actions[self.action_index]
            # Action timestamps are relative to the first action in the recording (in seconds)
            action_time = action.t - self.first_action_time

            if elapsed >= action_time:
                # Execute action
                print(f"[LoopPlayer:{self.key_name}] T+{elapsed:.3f}s :: Executing {type(action).__name__} (scheduled at {action_time:.3f}s)")
                if isinstance(action, PlayerPlay):
                    # Efficiently re-seek if the same fragment is being played again.
                    if self.internal_player and self.internal_player.trk and self.internal_player.frag_id == action.frag_id:
                        print(f"    -> Re-seeking existing player for frag_id: {action.frag_id}")
                        start_frame = action.start_frame if action.start_frame is not None else self.internal_player.trk.begin
                        self.internal_player.seek(start_frame)
                        self.internal_player.play() # Ensures it is playing
                    else:
                        if self.internal_player:
                            self.internal_player.kill()
                        # The HeadlessPlayer handles creating its own Resource and Tracker
                        print(f"    -> Playing frag_id: {action.frag_id}")
                        self.internal_player = HeadlessPlayer(self.k, action.frag_id)
                        if self.internal_player.trk: # Check for successful initialization
                            if action.start_frame is not None:
                                self.internal_player.seek(action.start_frame)
                            self.internal_player.play()
                        else:
                            print(f"    -> FAILED to initialize HeadlessPlayer for frag_id: {action.frag_id}")
                            self.internal_player = None  # Failed to load
                elif self.internal_player and self.internal_player.trk:
                    if isinstance(action, PlayerPause):
                        print("    -> Pausing playback")
                        self.internal_player.pause()
                    elif isinstance(action, PlayerStop):
                        print("    -> Stopping playback")
                        self.internal_player.stop()
                    elif isinstance(action, PlayerSeek):
                        print(f"    -> Seeking to frame: {action.frame}")
                        self.internal_player.seek(action.frame)

                self.action_index += 1
            else:
                # Next action is in the future, so we can stop checking for now.
                break

    def kill(self):
        print(f"[LoopPlayer:{self.key_name}] Kill called.")
        if self.internal_player:
            self.internal_player.kill()