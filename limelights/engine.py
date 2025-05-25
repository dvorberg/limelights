import sys, time

from . import framerate
from .model import Changes

class Engine(object):
    def __init__(self, buildings, first_light_index=0):
        self._strip = None
        self.buildings = buildings

        def indeces():
            i = 0
            while True:
                yield i
                i += 1
        self.indeces = indeces()

        for building in self.buildings:
            building.engine_init(self)

        self.lightcount = next(self.indeces)
        self.indeces = None

    def animate(self, strip):
        frametime = 1 / framerate
        while True:
            start = time.time()

            changes = Changes([building.animated_changes()
                               for building in self.buildings])

            for idx, color in changes:
                strip[idx] = color

            strip.show()

            end = time.time()
            d = frametime - (end-start)
            if d > 0:
                time.sleep(d)
