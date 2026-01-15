from k.replay.ops import Action, ParseError, ACTIONS, PRECISION


class PlayerAction(Action):
    """Base class for player-specific actions used in music looping."""
    pass


class PlayerPlay(PlayerAction):
    def __init__(self, frag_id, start_frame=None, t=None):
        super().__init__(t)
        self.frag_id = frag_id
        self.start_frame = start_frame

    @classmethod
    def parse(cls, t, data_str):
        if data_str is None:
            raise ParseError("PlayerPlay action requires a fragment ID", f"{t}:")
        parts = data_str.split(',')
        frag_id = int(parts[0])
        start_frame = int(parts[1]) if len(parts) > 1 else None
        return cls(frag_id, start_frame, t)

    def format(self, started=None):
        data = super().format(started) + str(self.frag_id)
        if self.start_frame is not None:
            data += f',{self.start_frame}'
        return data


class PlayerPause(PlayerAction):
    def __init__(self, t=None):
        super().__init__(t)

    @classmethod
    def parse(cls, t, data_str):
        return cls(t)

    def format(self, started=None):
        return super().format(started)


class PlayerStop(PlayerAction):
    def __init__(self, t=None):
        super().__init__(t)

    @classmethod
    def parse(cls, t, data_str):
        return cls(t)

    def format(self, started=None):
        return super().format(started)


class PlayerSeek(PlayerAction):
    def __init__(self, frame, t=None):
        super().__init__(t)
        self.frame = frame

    @classmethod
    def parse(cls, t, data_str):
        if data_str is None:
            raise ParseError("PlayerSeek action requires a frame number", f"{t}:")
        return cls(int(data_str), t)

    def format(self, started=None):
        return super().format(started) + str(self.frame)


class PlayerNoteOn(PlayerAction):
    def __init__(self, key, volume=1.0, t=None):
        super().__init__(t)
        self.key = key
        self.volume = volume

    @classmethod
    def parse(cls, t, data_str):
        if data_str is None:
            raise ParseError("PlayerNoteOn action requires a key", f"{t}:")
        parts = data_str.split(',')
        key = int(parts[0])
        volume = float(parts[1]) if len(parts) > 1 else 1.0
        return cls(key, volume, t)

    def format(self, started=None):
        return super().format(started) + f"{self.key},{self.volume}"


class PlayerNoteOff(PlayerAction):
    def __init__(self, key, t=None):
        super().__init__(t)
        self.key = key

    @classmethod
    def parse(cls, t, data_str):
        if data_str is None:
            raise ParseError("PlayerNoteOff action requires a key", f"{t}:")
        return cls(int(data_str), t)

    def format(self, started=None):
        return super().format(started) + str(self.key)


class PlayerSetVolume(PlayerAction):
    def __init__(self, volume, t=None):
        super().__init__(t)
        self.volume = volume

    @classmethod
    def parse(cls, t, data_str):
        if data_str is None:
            raise ParseError("PlayerSetVolume action requires a volume level", f"{t}:")
        return cls(float(data_str), t)

    def format(self, started=None):
        return super().format(started) + str(self.volume)


class PlayerSetMusicVolume(PlayerAction):
    def __init__(self, volume, t=None):
        super().__init__(t)
        self.volume = volume

    @classmethod
    def parse(cls, t, data_str):
        if data_str is None:
            raise ParseError("PlayerSetMusicVolume action requires a volume level", f"{t}:")
        return cls(float(data_str), t)

    def format(self, started=None):
        return super().format(started) + str(self.volume)


class PlayerHoldStart(PlayerAction):
    def __init__(self, t=None):
        super().__init__(t)

    @classmethod
    def parse(cls, t, data_str):
        return cls(t)

    def format(self, started=None):
        return super().format(started)


class PlayerHoldEnd(PlayerAction):
    def __init__(self, t=None):
        super().__init__(t)

    @classmethod
    def parse(cls, t, data_str):
        return cls(t)

    def format(self, started=None):
        return super().format(started)


class PlayerJump(PlayerAction):
    def __init__(self, index, t=None):
        super().__init__(t)
        self.index = index

    @classmethod
    def parse(cls, t, data_str):
        if data_str is None:
            raise ParseError("PlayerJump action requires an index", f"{t}:")
        return cls(int(data_str), t)

    def format(self, started=None):
        return super().format(started) + str(self.index)


class PlayerSetLoopStart(PlayerAction):
    def __init__(self, t=None):
        super().__init__(t)

    @classmethod
    def parse(cls, t, data_str):
        return cls(t)

    def format(self, started=None):
        return super().format(started)


class PlayerSetLoopEnd(PlayerAction):
    def __init__(self, t=None):
        super().__init__(t)

    @classmethod
    def parse(cls, t, data_str):
        return cls(t)

    def format(self, started=None):
        return super().format(started)


class PlayerLoopToggle(PlayerAction):
    def __init__(self, state, t=None):
        super().__init__(t)
        self.state = state  # boolean

    @classmethod
    def parse(cls, t, data_str):
        if data_str is None:
            raise ParseError("PlayerLoopToggle action requires a state", f"{t}:")
        return cls(bool(int(data_str)), t)

    def format(self, started=None):
        return super().format(started) + str(int(self.state))


# This replaces the old PlayerSetSpeed action.
class PlayerPlaybackSpeed(PlayerAction):
    def __init__(self, speed, direction, t=None):
        super().__init__(t)
        self.speed = speed
        self.direction = direction

    @classmethod
    def parse(cls, t, data_str):
        if data_str is None:
            raise ParseError("PlayerPlaybackSpeed action requires speed and direction", f"{t}:")
        parts = data_str.split(',')
        speed = float(parts[0])
        direction = int(parts[1])
        return cls(speed, direction, t)

    def format(self, started=None):
        return super().format(started) + f"{self.speed},{self.direction}"


# IMPORTANT:
# We are extending the main ACTIONS list from replay.ops here.
# This is a bit of a hack, but it keeps the player-specific actions
# separate while still using the same parsing/formatting mechanism.
# This must be imported *after* k.replay.ops to work correctly.

ACTIONS.extend([
    PlayerPlay,
    PlayerPause,
    PlayerStop,
    PlayerSeek,
    PlayerNoteOn,
    PlayerNoteOff,
    PlayerPlaybackSpeed, # Formerly PlayerSetSpeed
    PlayerSetVolume,
    PlayerSetMusicVolume,
    PlayerHoldStart,
    PlayerHoldEnd,
    PlayerJump,
    PlayerSetLoopStart,
    PlayerSetLoopEnd,
    PlayerLoopToggle,
])
