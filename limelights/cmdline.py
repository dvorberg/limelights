#!/usr/bin/env python3

import sys, argparse, time, re, importlib, pathlib, os, pwd, grp
import importlib.machinery
import importlib.util

try:
    from rpi_ws281x import PixelStrip as RealPixelStrip
except ImportError:
    pass

from . import config
from . engine import Engine
from .basetypes import Time, Changes
from .model import Building, Town, Source, Light, EndMarker

class DebugPixelStrip(dict):
    def __init__(self, *args, **kw):
        # We ignore all the parameters.
        super().__init__()
        self.outfile = sys.stdout
        self.now = Time(0)

    def begin(self):
        pass

    def print(self, *args, **kw):
        kw["file"] = self.outfile
        print(*args, **kw)

    def __len__(self):
        return max(self.keys()) + 1

    @property
    def size(self):
        return len(self)

    def show(self):
        """
        This is going to print out our contents to stdout.
        """
        pass


def parse_int(s):
    if s.startswith("0x"):
        return int(s[2:], 16)
    else:
        return int(s)

range_re = re.compile(r"(\d+)[-–](\d+)|(\d+)")
def parse_number_range(r):
    match = range_re.match(r)
    if match is None:
        raise ValueError("Range syntax error in " + repr(r))
    else:
        first, last, no = match.groups()
        if first and last:
            return set(range(int(first), int(last)+1))
        else:
            return {int(no)}

def parse_number_ranges(r):
    ret = set()
    for R in r.split(","):
        ret |= parse_number_range(R)
    return ret

def load_module_from_file(filepath):
    path = pathlib.Path(filepath)
    name = path.stem

    loader = importlib.machinery.SourceFileLoader( name, filepath)
    spec = importlib.util.spec_from_loader( name, loader )
    module = importlib.util.module_from_spec( spec )
    loader.exec_module( module )

    return module

def populate_with_strip_arguments(parser):
    parser.add_argument("-g", "--gpio", help="GPIO pin connected to the pixels"
                        "18 uses PWM, 10 uses SPI /dev/spidev0.0, 21 uses PCM",
                        default=18, type=int)
    parser.add_argument("--led-freq", help="LED signal frequency in hertz "
                        "(usually 800khz)", default=800000, type=int)
    parser.add_argument("--dma", help="DMA channel to use for generating "
                        "signal (try 10)", default=10, type=int)
    parser.add_argument("--brightness", help="Set to 0 for darkest and 255 for "
                        "brightest.", default=255, type=int)
    parser.add_argument("--invert", help="True to invert the signal (when "
                        "using NPN transistor level shift)",
                        action="store_true", default=False)
    parser.add_argument("--channel", help="Set to 1 by default for GPIOs "
                        "13, 19, 41, 45, or 53, otherwise 0.",
                        default=None, type=int)
    parser.add_argument("--debug-strip", help="Use the virtual PixelStrip "
                        "for debuging.", action="store_true", default=False)

def construct_strip(args, size):
    if args.debug_strip or "RealPixelStrip" not in globals():
        PixelStrip = DebugPixelStrip
    else:
        PixelStrip = RealPixelStrip

    if args.channel is None:
        channel = 0
        if args.gpio in { 13, 19, 41, 45, 53 }:
            channel = 1
    else:
        channel = args.channel

    if args.gpio == 18: # We need root privileges for this.
        if os.getuid() != 0:
            raise OSError("We need root access to manipulate the lights on GPIO 18.")

    strip = PixelStrip(size,
                       args.gpio, args.led_freq, args.dma,
                       args.invert, args.brightness, channel)

    strip.begin()

    if args.gpio == 18: # We need root privileges for this.
        # Drop root privileges
        nobody = pwd.getpwnam("nobody").pw_uid
        nogroup = grp.getgrnam("nogroup").gr_gid
        os.setgid(nogroup)
        os.setuid(nobody)

    return strip

def load_buildings(modules):
    for modulename in modules:
        if modulename.endswith(".py"):
            module = load_module_from_file(modulename)
        else:
            module = importlib.import_module(modulename)

        for identifyer, value in module.__dict__.items():
            if isinstance(value, Building):
                value.identifyer = identifyer
                yield value

def all_lights(item):
    if isinstance(item, Light):
        yield item
    elif isinstance(item, Source):
        yield item.light
    elif isinstance(item, list):
        for a in item:
            yield from all_lights(a)
    else:
        raise TypeError(item)


def identify():
    parser = argparse.ArgumentParser(description="Identify room lights "
                                     "by blinking each room’s light(s) twice "
                                     "and then the next room and so on.")

    populate_with_strip_arguments(parser)
    parser.add_argument("--building", "-b", help="Specify building name or "
                        "identifyer (within its module). If not set, the "
                        "first building loaded will be used.", default=None)
    parser.add_argument("--offset", "-o", help="First light’s ID to be used",
                        type=int, default=0)
    parser.add_argument("--skip", "-s", help="Number of rooms (not lights!) "
                        "to skip before blinking any lights", type=int,
                        default=0)
    parser.add_argument("--wait", "-w", help="Wait for key press before "
                        "blinking the next room", action="store_true",
                        default=False)
    parser.add_argument("modules", nargs="+",
                        help="Python modules to import or python files to "
                        "evaluate to load building models")

    args = parser.parse_args()

    town = Town(*load_buildings(args.modules))
    engine = Engine(town, args.offset)

    strip = construct_strip(args, engine.lightcount)
    strip.begin()

    building = None
    if args.building:
        building = town.building_by_name(args.building)

    if building is None:
        building = town[0]

    def set(item, color):
        change = Changes([light.change_to(color)
                          for light in all_lights(item)])
        change.apply_to(strip)
        strip.show()

    # Turn all the lights off.
    set(building, 0)

    # Ok, let’s do our work here:
    for idx, room in enumerate(building[args.skip:]):
        print(room._info(), end=" ")
        sys.stdout.flush()

        set(room, 0xffffff)
        time.sleep(.5)
        set(room, 0x000000)
        time.sleep(.5)
        set(room, 0xffffff)
        time.sleep(.5)
        set(room, 0x000000)

        if args.wait:
            set(room, 0xffffff)
            print("<ENTER>", end="")
            input()
            set(room, 0x000000)
        else:
            print()


def animate():
    parser = argparse.ArgumentParser(description="Run a limelights animation")

    populate_with_strip_arguments(parser)

    parser.add_argument("--speed", "-s", help="Animation speed factor",
                        type=float, default=1.0)
    parser.add_argument("--framerate", help="How many times a second"
                        "the strip’s state is rendered.",
                        type=int, default=24)
    parser.add_argument("--offset", "-o", help="First light’s ID to be used",
                        type=int, default=0)
    parser.add_argument("--debug",
                        help="Print Buildings, rooms, and lights to stdout"
                        "on each frame.",
                        action="store_true", default=False)
    parser.add_argument("--end-marker", "-E",
                        help="Append no EndMarker, an extra "
                        "pixel colorfully blinking to test electrical "
                        "connectivity.",
                        action="store_false", default=True)
    parser.add_argument("modules", nargs="+",
                        help="Python modules to import or python files to "
                        "evaluate to load building models")

    args = parser.parse_args()

    if args.debug or "RealPixelStrip" not in globals():
        args.debug = True

    config.framerate = args.framerate
    config.speed = args.speed
    config.debug = args.debug

    town = Town(*load_buildings(args.modules))
    if args.end_marker:
        town.append(EndMarker())
    engine = Engine(town, args.offset)

    strip = construct_strip(args, engine.lightcount)

    # This will not return.
    engine.animate(strip)

def list_items():
    parser = argparse.ArgumentParser(help="Load building modules and list "
                                     "their subitems.")

    parser.add_argument("modules", nargs="+",
                        help="Python modules to import or python files to "
                        "evaluate to load building models")

    town =  Town(*load_buildings(args.modules))
    town.list_items()
