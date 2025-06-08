import random

from .. import config

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
