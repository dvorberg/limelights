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

        for b in self.town:
            print(f"{b.__class__.__name__} “{b.name}”")
            for room in b:
                print(" ", room.__class__.__name__, f"“{room.name}”")
                for source in room:
                    pixel = source.__fstpix()
                    print("  {:3}:{:06x}".format(pixel._idx, strip[pixel._idx]),
                          pixel.__class__.__name__)

        print()
        print(self._now)
        self._now += 1


    def animate(self, strip, debug=False):
        if debug:
            clear()

        frametime = 1 / config.framerate
        start = time.time()
        changes = self.town.changes()
        for change in changes:
            change.apply_to(strip)

            if debug:
                self._output_debug_info(strip)

            strip.show()

            end = time.time()
            d = frametime - (end-start)
            if d > 0:
                time.sleep(d)
            start = end + d
