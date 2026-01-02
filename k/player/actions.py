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
])