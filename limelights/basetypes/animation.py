from typing import Generator, Callable

from .color import Color

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
