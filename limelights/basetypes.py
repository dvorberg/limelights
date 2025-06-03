import types, random, colorsys
from typing import Generator, Callable
from termcolor import colored

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
    def from_rgb(Color, r:int, g:int, b:int):
        if r > 255: raise ValueError()
        if g > 255: raise ValueError()
        if b > 255: raise ValueError()
        return Color((r << 16) | (g << 8) | b)

    @classmethod
    def from_rgb_f(Color, r:float, g:float, b:float):
        # Keep these around in case we need them later.
        self = Color.from_rgb(round(r*255), round(g*255), round(b*255))
        self._rgb_f = r, g, b
        return self

    @classmethod
    def from_hsl(Color, h:float, s:float, l:float):
        if h > 1.0: raise ValueError()
        if s > 1.0: raise ValueError()
        if l > 1.0: raise ValueError()

        self = Color.from_rgb_f(*colorsys.hls_to_rgb(h, s, l))
        self._hsl = (h, s, l)
        return self

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
    def rgb(self) -> tuple[int]:
        return (self >> 16, (self & 0x00ff00) >> 8, self & 0x0000ff)

    @property
    def rgb_f(self) -> tuple[float]:
        if not hasattr(self, "_rgb_f"):
            self._rgb_f = tuple([channel / 255 for channel in self.rgb])
        return self._rgb_f

    @property
    def hsl(self) -> tuple[float]:
        if not hasattr(self, "_hsl"):
            self._hsl = colorsys.rgb_to_hls(*self.rgb_f)
        return self._hsl

    @property
    def h(self) -> float:
        """
        Most sources of visible light contain energy over a band
        of wavelengths. Hue is the wavelength within the visible light
        spectrum at which the energy output from a source is
        greatest. It is indicated by its position (in degrees) on the
        RGB color wheel: 0° <= h <= 360°
        """
        return self.hsl[0]

    @property
    def s(self) -> float:
        """
        Saturation is an expression for the relative bandwidth of
        the visible output from a light source. As saturation
        increases, colors appear more pure. As saturation decreases,
        colors appear more washed-out. It is measured on the following
        scale: 0 <= s <= 1
        """
        return self.hsl[1]

    @property
    def l(self) -> float:
        """
        Luminosity (also called brightness, lightness or
        luminance) stands for the intensity of the energy output of a
        visible light source. It basically tells how light a color is
        and is measured on the following scale: 0 <= l <= 1
        """
        return self.hsl[2]

    def __repr__(self):
        return f"{self:06x}"

    # Darker and brigter are the same thing. It depends on your factor
    # not my function.
    def brighter(self, factor:float):
        return self.darker(f)

    def darker(self, factor:float):
        h,s,l = self.hsl
        l = l*factor
        if l > 1.0:
            l = 1.0
        return self.from_hsl(h, s, l)




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

    @property
    def indeces(self):
        return set()

    def print_items(self, level=0):
        raise NotImplementedError()

class Lights(list):
    @property
    def indeces(self):
        ret = set()
        for a in self:
            ret.update(a.indeces)
        return ret

    @property
    def pixels(self):
        return sorted([item for item in self
                       if getattr(item, "idx", None) is not None])



    def print_items(self, strip=None, level=0):
        print(level*"  " + self._info() + (self._colorinfo(strip) or ""))

        for item in self:
            if hasattr(item, "print_items"):
                item.print_items(strip, level+1)

    def _info(self):
        ids = sorted(list(self.indeces))
        s = []
        while ids:
            n = ids[0]
            ids = ids[1:]
            m = n
            while (ids and ids[0] == m+1):
                m = ids[0]
                ids = ids[1:]

            if n == m:
                s.append(str(n))
            else:
                s.append(f"{n}–{m}")

        typename = self.__class__.__name__
        s = ",".join(s)
        return f"[{s}] {typename}"

    def _colorinfo(self, strip):
        if strip:
            ids = sorted(list(self.indeces))
            def color(i):
                c = Color(strip[i])
                return colored(c, color="red") # , on_color=c.rgb
            return " " + " ".join([f"{i}:{color(i)}" for i in ids])

    def __repr__(self):
        lst = super().__repr__()[1:-1]
        return f"[{self._info()} {lst}]"


class Lamp(Lights, Light):
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

class NameableLights(Lights):
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

    def _info(self):
        info = super()._info()
        if name := self.name:
             return f"{info} “{name}”"
        else:
            return info

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        else:
            return None
