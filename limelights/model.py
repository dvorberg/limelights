import random, dataclasses, types

from . import framerate
from .animations import on, off, tv

class Time(int):
    @property
    def frames(self):
        return self % framerate

    @property
    def seconds(self):
        return self // framerate

    @property
    def minutes(self):
        return self.seconds // 60

    @property
    def hours(self):
        return self.minutes // 60

    def time_in(self, seconds=0, minutes=0, hours=0):
        return Time(  seconds*framerate
                    + minutes*60*framerate
                    + hours*60*60*framerate)

    @classmethod
    def random(Time, a, b):
        return Time(random.randint(a, b))

    @classmethod
    def seconds(Time, f:float):
        return Time(f*framerate)

    @classmethod
    def minutes(Time, f:float):
        return Time(f*60*framerate)

    @classmethod
    def hours(Time, f:float):
        return Time(f*60*60*framerate)

@dataclasses.dataclass
class Minutes(object):
    a: int
    b: int

    def make_random_time(self):
        return Time.random(self.a, self.b)

def once(animation):
    for color in animation:
        yield color

    while True:
        yield None

def limit(animation, time):
    if isinstance(time, Minutes):
        time = time.make_random_time()

    for color in animation:
        yield color

        time -= 1
        if time == 0:
            break

class Change(dict):
    def __init__(self, idx, color):
        super().__init__( [(idx, color,)] )

    def __add__(self, other):
        self.update(other)

    def __iter__(self):
        return iter(self.items())

    def __repr__(self):
        return "Change" + super().__repr__()

class Changes(Change):
    def __init__(self, things):
        dict.__init__(self)

        for thing in things:
            if thing:
                if isinstance(thing, Change):
                    self.update(thing)
                elif type(thing) == types.GeneratorType:
                    self.update(Changes(thing))
                else:
                    raise TypeError(type(thing))

class Changeable(object):
    def engine_init(self, engine):
        raise NotImplementedError()

    def change_to(self, color) -> Change:
        raise NotImplementedError()

class Light(Changeable):
    def __init__(self):
        self._idx = None

    def engine_init(self, engine):
        self._idx = next(engine.indeces)

    def change_to(self, color) -> Change:
        return Change(self._idx, color)

class Container(list):
    def engine_init(self, engine):
        for item in self:
            item.engine_init(engine)

    def change_to(self, color) -> Change:
        return Changes([item.change_to(color) for item in self])

    def __repr__(self):
        cls = self.__class__.__name__
        if hasattr(self, "_name"):
            name = f" “{self._name}”"
        lst = super().__repr__()[1:-1]
        return f"[{cls}{name} {lst}]"

class Room(Container):
    def __init__(self, *lights, lightnum=None, color=0xffffff):
        """
        Specific `lights` may be passed as positional parameters. If a
        string is passed among the lights, it is assumed to be the room’s
        name. If no lights are specified, `lightnum` default lights will
        be created in their stead.
        """
        self._color = color
        self._name = "Room " + str(id(self))
        for light in lights:
            if type(light) is str:
                self._name = light
            else:
                self.append(light)

        if lightnum is not None:
            while len(self) < lightnum:
                self.append(self.make_default_light())

    def make_default_light(self):
        return Light()

    def animations(self):
        yield once(self.on())

    def animated_changes(self):
        while True:
            for animation in self.animations():
                for color in animation:
                    if color is not None:
                        yield self.change_to(color)
                    else:
                        yield None

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
    def __init__(self, *lights, lightnum=None, color=0x553311,
                 regular=Minutes(3,10),
                 beforetv=Minutes(2,8), tv=Minutes(6,12), aftertv=Minutes(2,3),
                 darkness=Minutes(10,20)):
        super().__init__(*lights, lightnum=lightnum, color=color)
        self.regular = regular
        self.beforetv = beforetv
        self.tv = tv
        self.aftertv = aftertv
        self.darkness = darkness

    def animations(self):
        def occupied():
            return random.random() > .65

        def watchingtv():
            return random.random() >= .5

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
            yield limit(self.on(), self.darkness)


class Fireplace(Room):
    """
    A room with a fireplace has a soft warm-white base lighting.

    The lights may be off for 6-20min
       or
    on for 3-8min
       followed by 15-22min of fire animation (the last of which animates
       dying amers till darkness).
    followed by 8-15min of darkness.
    """
    def __init__(self, *lights, lightnum=None, color=0x553311,
                 light=Minutes(6,20),
                 beforefire=Minutes(3,8), fire=Minutes(15,22),
                 darkness=Minutes(6,20)):
        super().__init__(*lights, lightnum=lightnum, color=color)
        self.light = light
        self.beforefire = beforefire
        self.fire = fire
        self.darkness = darkness

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
                 usage=Minutes(5,12), light=Time.minutes(1)):
        super().__init__(*lights, lightnum=lightnum, color=color)
        self.usage = usage
        self.light = light

    def animations(self):
        yield limit(self.off(), self.usage)
        yield limit(self.on(), self.light)

class Building(Container):
    def __init__(self, name, *rooms):
        self._name = name
        for room in rooms:
            self.append(room)

        self.running = [ room.animated_changes() for room in self ]

    def animated_changes(self):
        return Changes([ next(animation) for animation in self.running ])
