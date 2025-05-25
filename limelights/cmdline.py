#!/usr/bin/env python3

import sys, argparse, time, re, importlib, pathlib
import importlib.machinery
import importlib.util

from rpi_ws281x import PixelStrip, Color

from . engine import Engine
from . import model

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

def animate():
    parser = argparse.ArgumentParser(description="Run a limelights animation")
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
    parser.add_argument("-v", "--verbose", help="Be verbose",
                        action="store_true", default=False)
    parser.add_argument("modules", nargs="+",
                        help="Python modules to import or python files to "
                        "evaluate to load building models")

    args = parser.parse_args()

    if args.channel is None:
        channel = 0
        if args.gpio in { 13, 19, 41, 45, 53 }:
            channel = 1
    else:
        channel = args.channel

    buildings = []

    for modulename in args.modules:
        if modulename.endswith(".py"):
            module = load_module_from_file(modulename)
        else:
            module = importlib.import_module(modulename)

        for item in module.__dict__.values():
            if isinstance(item, model.Building):
                buildings.append(item)

    engine = Engine(buildings)

    strip = PixelStrip(engine.lightcount,
                       args.gpio, args.led_freq, args.dma,
                       args.invert, args.brightness, channel)
    strip.begin()

    # This will not return.
    engine.animate(strip)
