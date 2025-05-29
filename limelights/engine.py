import sys, time

from . import config
from .model import Changes, Time, Town
from .utils import clear, home

class Engine(object):
    def __init__(self, town:Town, first_light_index:Time=0):
        self._strip = None
        self.town = town

        def indeces():
            i = first_light_index
            while True:
                yield i
                i += 1
        self.indeces = indeces()

        self.town.engine_init(self)

        self.lightcount = next(self.indeces)
        self.indeces = None

        self._now = Time(0)

    def _output_debug_info(self, strip):
        home()
        self.town.print_items(strip)
        print()
        print(self._now)
        self._now += 1


    def animate(self, strip):
        if config.debug:
            clear()

        frametime = 1 / config.framerate
        start = time.time()
        changes = self.town.changes()
        for change in changes:
            change.apply_to(strip)

            if config.debug:
                self._output_debug_info(strip)

            strip.show()

            end = time.time()
            d = frametime - (end-start)
            if d > 0:
                time.sleep(d)
            start = end + d
