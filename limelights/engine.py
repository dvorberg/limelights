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

    def _output_debug_info(self, strip, proctime):
        home()
        self.town.print_items(strip)
        print()
        print(self._now)
        self._now += 1
        print("%.4f" % proctime)


    def animate(self, strip):
        if config.debug:
            clear()

        frametime = 1 / config.framerate
        start = time.time()
        changes = self.town.changes()
        for change in changes:
            change.apply_to(strip)

            strip.show()

            end = time.time()
            proctime=end-start

            d = frametime - proctime
            if d > 0:
                time.sleep(d)
                start = end + d
            else:
                # On the occasional cold start this mechanism screws up
                # when the engine is started in the boot sequence. I
                # suppose the system clock gets set during the script’s
                # runtime.
                start = time.time()

            if config.debug:
                self._output_debug_info(strip, proctime)
                start = time.time()
