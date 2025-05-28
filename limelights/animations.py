from random import randint
from itertools import repeat
from typing import Generator

from . import config
from .basetypes import Animation, Change, Time, Color, RDuration

def limit(animation:Animation, duration:Time|RDuration) -> Animation:
    if isinstance(duration, RDuration):
        time = duration.randomize()
    else:
        time = duration

    if config.speed != 1:
        time = int(time/config.speed)

    for change in animation:
        yield change

        time -= 1
        if time == 0:
            break

def no_more_changes():
    while True:
        yield None

def perpetual(f):
    def wrapper(*args, **kw):
        yield from f(*args, **kw)
        yield from no_more_changes()

    return wrapper

def repeats(f):
    def wrapper(*args, **kw):
        while True:
            yield from f(*args, **kw)

    return wrapper

@perpetual
def on(color):
    yield color

@perpetual
def off():
    yield 0

def rduration(a:float, b:float):
    """
    “a” and “b” are floats denoting seconds.
    """
    return int(randint(int(a*config.framerate),
                       int(b*config.framerate)))


def rwait(a:float, b:float):
    """
    “a” and “b” are floats denoting seconds.
    """
    yield from repeat(None, rduration(a, b))


def tv():
    def limit(channel):
        if channel < 0:
            return 0
        elif channel > 255:
            return 255
        else:
            return channel

    bigdiff = 20
    smalldiff = 10

    while True:
        # A random color with a blue tint
        middle = randint(50, 90)
        r = limit(randint(middle-bigdiff, middle+bigdiff))
        g = limit(randint(middle-bigdiff, middle+bigdiff))
        b = limit(50 + randint(middle-bigdiff, middle+bigdiff))

        # A cut to a new sequence.
        yield Color.from_components(r, g, b)

        yield from rwait(.2, .8)

        for a in range(randint(10, 25)):
            # Make a number of small, quick changes emulating cuts
            # within a sequence.
            R = limit(r + randint(-smalldiff, smalldiff))
            G = limit(g + randint(-smalldiff, smalldiff))
            B = limit(b + randint(-smalldiff, smalldiff))

            yield Color.from_components(R, G, B)

            yield from rwait(.2, .8)

def candle():
    baselight = Color(0xff8800).darker(5)

    while True:
        yield baselight

        for a in range(randint(3, 6)):
            # Flicker a little
            for b in range(3):
                yield baselight.darker(randint(3,8))

            # Stick to a color for a while.
            yield baselight.darker(randint(2,4))
            yield from rwait(4, 12)


        # Flicker more!
        for a in range(randint(5, 9)):
            yield baselight.darker(randint(3,8))
