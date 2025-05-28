import types, random
from typing import Generator, Callable

from . import config

class Time(int):
    """
    Time is measured in an integer number of
    frames. config.framerate is used to convert them to regular units
    of time.
    """
    @property
    def seconds(self) -> float:
        return float(self / config.framerate)

    @property
    def minutes(self) -> int:
        return self.seconds // 60

    @property
    def hours(self) -> int:
        return self.minutes // 60

    def time_in(self, seconds:float=0.0, minutes:float=0.0, hours:float=0.0):
        return Time(  seconds*config.framerate
                    + minutes*60*config.framerate
                    + hours*60*60*config.framerate)

    @classmethod
    def random(Time, a, b):
        """
        Return a random time a <= t <= b.
        """
        return Time(random.randint(a, b))

    @classmethod
    def from_seconds(Time, f:float):
        return Time(f*config.framerate)

    @classmethod
    def from_minutes(Time, f:float):
        return Time(f*60*config.framerate)

    @classmethod
    def from_hours(Time, f:float):
        return Time(f*60*60*config.framerate)

    def __iadd__(self, other):
        return Time(self+other)

    def __isub__(self, other):
        return Time(self-other)

    def __str__(self):
        frames = self % config.framerate
        seconds = self // config.framerate
        minutes = seconds // 60
        hours = minutes // 60
        return "{:02}:{:02}:{:02}:{:02}".format(
            hours, minutes, seconds % 60, frames)

class Duration(Time):
    pass

class RDuration(object):
    def __init__(self, a:Time, b:Time):
        self.a = a
        self.b = b

    @classmethod
    def from_minutes(RDuration, a:float, b:float):
        return RDuration(Time.from_minutes(a),
                         Time.from_minutes(b))

    @classmethod
    def from_seconds(RDuration, a:float, b:float):
        return RDuration(Time.from_seconds(a),
                         Time.from_seconds(b))

    def randomize(self):
        return Time.random(self.a, self.b)

def randmins(a, b) -> RDuration:
    return RDuration.from_minutes(a, b)

def randsecs(a, b) -> RDuration:
    return RDuration.from_seconds(a, b)

class Color(int):
    @classmethod
    def from_components(Color, r:int, g:int, b:int):
        return Color((r << 16) | (g << 8) | b)

    @property
    def r(self) -> int:
        return self >> 16

    @property
    def g(self) -> int:
        return (self & 0x00ff00) >> 8

    @property
    def b(self) -> int:
        return (self & 0x0000ff)

    @property
    def rgb(self):
        return (self >> 16, (self & 0x00ff00) >> 8, self & 0x0000ff)

    def brigter(self, factor:float):
        factor = float(factor)
        return self.from_components(*[int(c*factor) for c in self.rgb])

    def darker(self, factor:float):
        factor = float(factor)
        return self.from_components(*[int(c/factor) for c in self.rgb])

Animation = Generator[Color, None, None]
Animations = Generator[Animation, None, None]
AnimationsFunction = Callable[[None], Animations]

class Change(dict):
    def __init__(self, idx:int, color:Color):
        super().__init__()
        self[idx] = color

    def __add__(self, other):
        self.update(other)

    def __iter__(self):
        return iter(self.items())

    def __repr__(self):
        return "Change" + super().__repr__()

    def apply_to(self, strip):
        try:
            for idx, color in self.items():
                strip[idx] = color
        except TypeError:
            ic(idx, color)
            raise

class Changes(Change):
    def __init__(self, things):
        for thing in things:
            if thing:
                if isinstance(thing, Change):
                    self.update(thing)
                elif type(thing) == types.GeneratorType:
                    self.update(Changes(thing))
                else:
                    raise TypeError(type(thing))

class Light(object):
    """
    Abstract baseclass for those things that control one or more
    pixels which all display the same color. A Changeble is running a
    single animation at all times.
    """
    def engine_init(self, engine):
        raise NotImplementedError()

    def change_to(self, color) -> Change:
        raise NotImplementedError()

class Lamp(Light, list):
    """
    A Lamp is a collection of multiple Lights that show the same
    color. It implements the Light interface and can be used anywhere
    a Light can be used.
    """
    def __init__(self, *items):
        super().__init__(items)

    def engine_init(self, engine):
        for item in self:
            item.engine_init(engine)

    def change_to(self, color) -> Change:
        return Changes([item.change_to(color) for item in self])


class NameableList(list):
    """
    A Nameable is a list of things that also accepts strings as
    parameters. The first string passed is considered the object’s
    name for identification in debug output.
    """
    def __init__(self, *items):
        """
        Specific `items` may be passed as positional parameters. If a
        string is passed among the items, it is assumed to be the space’s
        name.
        """
        super().__init__()

        self._name = f"{self.__class__.__name__} 0x{id(self):x}"

        for item in items:
            if type(item) is str:
                self._name = item
            else:
                self.append(item)

    def engine_init(self, engine):
        for item in self:
            item.engine_init(engine)

    def __repr__(self):
        cls = self.__class__.__name__
        name = self.name
        if name:
            name = f" “{name}”"
        else:
            name = ""
        lst = super().__repr__()[1:-1]
        return f"[{cls}{name} {lst}]"

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        else:
            return None
