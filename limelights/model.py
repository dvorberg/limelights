import random, dataclasses, types
from typing import Generator

from . import config
from .basetypes import (Time, Duration, randmins, Color,
                        Animation, Animations, AnimationsFunction,
                        Change, Changes, Light, Lamp, NameableLights)
from .animations import limit, repeats, on, off, tv, candle

class Pixel(Light):
    """
    A Pixel represents one of the lights on a PixelStrip
    identified by its index which is set through the engine_init()
    method.
    """
    def __init__(self):
        self.idx = None

    def engine_init(self, engine):
        self.idx = next(engine.indeces)

    def change_to(self, color) -> Change:
        return Change(self.idx, color)

    @property
    def indeces(self):
        return {self.idx}

    def __lt__(self, other):
        return self.idx < other.idx

class Source(object):
    """
    A source is a Light that has animations to it.
    A source has a generator of Changes.

    The animations generator may be changed on the fly. The next
    Change yielded by changes() will reflect the er… change.
    """
    def __init__(self, light:Light, animations:AnimationsFunction):
        self.light = light
        self._dirty = False
        self._animations = animations

    @property
    def indeces(self):
        return self.light.indeces

    def engine_init(self, engine):
        self.light.engine_init(engine)

    @property
    def animations(self) -> AnimationsFunction:
        return self._animations

    @animations.setter
    def animations(self, animations:AnimationsFunction):
        self._animations = animations
        self._dirty = True

    def changes(self) -> Generator[Change, None, None]:
        while True:
            self._dirty = False
            for animation in self.animations():
                for color in animation:
                    if color is None:
                        yield None
                    else:
                        yield self.light.change_to(color)

                    if self._dirty:
                        break
                if self._dirty:
                    break

class Space(NameableLights):
    """
    A space is a collection of Sources and a genrator of
    Changes. They can be nested.
    """
    def engine_init(self, engine):
        for source in self:
            source.engine_init(engine)

    def changes(self) -> Generator[Change, None, None]:
        running = [source.changes() for source in self]
        while True:
            yield Changes([next(r) for r in running])

class Room(Space):
    """
    This is a base class for specific decorative units that
    roughly correspond to rooms in a building. The default
    implementation accepts assembles a number of lights to a source
    and runs the on() animation on them, turning the light in the room
    to a specified default color.
    """
    def __init__(self, *lights, lightnum=1, color=0xffffff):
        """
        Specific “lights” may be passed as positional
        parameters. If a string is passed among the lights, it is
        assumed to be the room’s name. If ferer lights are specified than
        `lightnum`, default lights will be created in their stead.
        """
        self._color = color

        lamp = Lamp()

        for l in lights:
            if type(l) is str:
                self._name = l
            else:
                lamp.append(l)

        while len(lamp) < lightnum:
            lamp.append(self.make_default_pixel())

        self.append(Source(lamp, self.animations))

    @property
    def source(self):
        return self[0]

    def animations(self):
        yield self.on()

    def make_default_pixel(self):
        return Pixel()

    def on(self):
        return on(self._color)

    def off(self):
        return off()

class HotelRoom(Room):
    """
    A hotel room has a soft warm-white base lighting. The room is
    either
       unoccupied for 8-18 minutes
    or,
        if occupied,
           lit with that light for 3-10 (“regular=”) minutes,
        or
           lit for 2-8min (“beforetv=”)
           followed by the guest wathing TV for 6-12min (“tv=”)
           and then going to bed with regular light for
               2-3 minutes (“aftertv=”),
        followed by 10-20minutes of darkness (“darkness=”)

    There is a 1-in-3 change the room is occupied.

    These default times may vary and I’ll probably forget updating
    this comment, but you get the idea.
    """
    def __init__(self, *lights, lightnum=1, color=0x553311,
                 regular=randmins(3,10),
                 beforetv=randmins(2,8),
                 tv=randmins(6,12),
                 aftertv=randmins(2,3),
                 darkness=randmins(10,20)):

        super().__init__(*lights, lightnum=lightnum, color=color)
        self.regular = regular
        self.beforetv = beforetv
        self.tv = tv
        self.aftertv = aftertv
        self.darkness = darkness

        self.source.animations = self.animations

    def animations(self):
        def occupied():
            return random.random() > .5

        def watchingtv():
            return random.random() >= .4

        if occupied():
            if watchingtv():
                yield limit(self.on(), self.beforetv)
                yield limit(tv(), self.tv)
                yield limit(self.on(), self.aftertv)
            else:
                # Maybe reading?
                yield limit(self.on(), self.regular)

            yield limit(self.on(), self.darkness)
        else:
            yield limit(self.off(), self.darkness)

class TVRoom(Room):
    def animations(self):
        yield tv()

class CandleRoom(Room):
    def animations(self):
        yield candle()

class Stairwell(Room):
    """
    A stairwell has a minute light. You press a switch and the
    light comes on.  A timer starts running and turns if off after one
    minute by which time you hopefully ascended (or descended) the
    stairs to reach your destination.

    This will happen once every 5-12 (“usage=”) minutes for
    1-1 minute. (“light=”).
    """
    def __init__(self, *lights, lightnum=None, color=0x553311,
                 usage=randmins(5,12), light=Time.from_minutes(1)):
        super().__init__(*lights, lightnum=lightnum, color=color)
        self.usage = usage
        self.light = light

    def animations(self):
        yield limit(self.off(), self.usage)
        yield limit(self.on(), self.light)

class Attic(Stairwell):
    def __init__(self, *lights, lightnum=None, color=Color(0xf06518).darker(.6),
                 usage=randmins(12,45), light=Time.from_minutes(4)):
        super().__init__(*lights, lightnum=lightnum, color=color, usage=usage, light=light)


class Fireplace(Room):
    pass

class Building(Space):
    def _colorinfo(self, strip): pass

class Town(Space):
    def _colorinfo(self, strip): pass

    def building_by_name(self, name) -> Building|None:
        for b in self:
            if b.identifyer == name or b.name == name:
                return b

        return None

class EndMarker(Room):
    def animations(self):
        yield self.animation()

    def animation(self):
        yield 0xff0000
        for a in range(config.framerate//2):
            yield None

        yield 0
        for a in range(config.framerate//2):
            yield None
