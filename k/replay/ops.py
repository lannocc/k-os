from abc import ABC, abstractmethod
import time

# NOTE: This file is for UI/system-level replay actions.
# For player-specific actions used in music looping, see k/player/actions.py


PRECISION = 1000000 # microseconds


class ParseError(ValueError):
    def __init__(self, msg, data_str):
        super().__init__(f'{msg}: {data_str}')


class Action(ABC):
    def __init__(self, t=None):
        if t is None:
            t = time.perf_counter()

        self.t = t

    @staticmethod
    def parse_all(data_str):
        return [ Action.get(data) for data in data_str.split('|') ]

    @staticmethod
    def format_all(actions, started=None):
        return '|'.join([ action.format(started) for action in actions ])

    @staticmethod
    def get(data_str):
        data = data_str.split(':')
        if len(data) > 2:
            raise ParseError('unexpected major parts (foo:bar)', data_str)

        ident = data.pop(0).split('@')
        if len(ident) != 2:
            raise ParseError('bad identifier format (idx@t)', data_str)

        try: idx = int(ident[0])
        except ValueError:
            raise ParseError('identifier index not an integer', data_str)

        try: cls = ACTIONS[idx]
        except IndexError:
            raise ParseError('no known action type for given index', data_str)

        try: t = int(ident[1])
        except ValueError:
            raise ParseError('action time not an integer', data_str)

        data_str = data[0] if data else None
        return cls.parse(t, data_str)

    @classmethod
    @abstractmethod
    def parse(cls, t, data_str):
        raise NotImplementedError()

    @abstractmethod
    def format(self, started=None):
        idx = ACTIONS.index(type(self))
        t = self.t
        if started is not None:
            t -= started
            t = int(t * PRECISION)
        return f'{idx}@{t}:'



###
### MOUSE
###

class MouseAction(Action):
    pass


class MouseMove(MouseAction):
    def __init__(self, x, y, t=None):
        super().__init__(t)
        self.x = x
        self.y = y

    @classmethod
    def parse(cls, t, data_str):
        data = data_str.split(',')
        x = int(data[0])
        y = int(data[1])
        return cls(x, y, t)

    def format(self, started=None):
        data = super().format(started)
        return data + f'{self.x},{self.y}'


class MouseDown(MouseAction):
    def __init__(self, button, t=None):
        super().__init__(t)
        self.button = button

    @classmethod
    def parse(cls, t, data_str):
        button = int(data_str)
        return cls(button, t)

    def format(self, started=None):
        data = super().format(started)
        return data + f'{self.button}'


class MouseUp(MouseAction):
    def __init__(self, button, t=None):
        super().__init__(t)
        self.button = button

    @classmethod
    def parse(cls, t, data_str):
        button = int(data_str)
        return cls(button, t)

    def format(self, started=None):
        data = super().format(started)
        return data + f'{self.button}'



###
### KEYBOARD
###

class KeyAction(Action):
    pass


class KeyDown(KeyAction):
    def __init__(self, code, t=None):
        super().__init__(t)
        self.code = code

    @classmethod
    def parse(cls, t, data_str):
        code = int(data_str)
        return cls(code, t)

    def format(self, started=None):
        data = super().format(started)
        return data + f'{self.code}'


class KeyUp(KeyAction):
    def __init__(self, code, t=None):
        super().__init__(t)
        self.code = code

    @classmethod
    def parse(cls, t, data_str):
        code = int(data_str)
        return cls(code, t)

    def format(self, started=None):
        data = super().format(started)
        return data + f'{self.code}'



###
### CAPTURE
###

class StopCapture(Action):
    def __init__(self, t=None):
        super().__init__(t)

    @classmethod
    def parse(cls, t, data_str):
        return cls(t)

    def format(self, started=None):
        data = super().format(started)
        return data



###
### CAUTION: The indexes of these actions get stored in the database.
###          Changes to the ordering will likely require a replay patch.
###

ACTIONS = [
    MouseMove,
    MouseDown,
    MouseUp,
    KeyDown,
    KeyUp,
    StopCapture,
]

