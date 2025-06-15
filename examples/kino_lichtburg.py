from random import random, randint

from limelights import config
from limelights.basetypes import Color
from limelights.model import (Building, Space, Room, HotelRoom, Fireplace,
                              Stairwell, Attic)
from limelights.animations import on, off, tv, limit, candle, darker

def rflicker(color:Color, a:float, b:float):
    """
    “a” and “b” are floats denoting seconds.
    """
    d = randint(int(a*config.framerate), int(b*config.framerate)) // 2

    for a in range(d):
        yield color
        yield 0

def projector():
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
        b = limit(randint(middle-bigdiff, middle+bigdiff))

        # A cut to a new sequence.
        yield from rflicker(Color.from_rgb(r, g, b).darker(random()), .2, .8)

        for a in range(randint(10, 25)):
            # Make a number of small, quick changes emulating cuts
            # within a sequence.
            R = limit(r + randint(-smalldiff, smalldiff))
            G = limit(g + randint(-smalldiff, smalldiff))
            B = limit(b + randint(-smalldiff, smalldiff))

            yield from rflicker(Color.from_rgb(R, G, B), .2, .8)



class Projector(Room):
    def animations(self):
        yield projector()

class Booth(Room):
    def __init__(self):
        # The default constructor will do for Victor’s room.
        # The color is a white even bluer thant the default of that
        # Pixel I glued there.
        super().__init__(color=0x111011)

#vorführraum = Building(
#    "Vorführraum",
#    Booth(),
#    Projector()
#
# )



warmwhite = Color(0x553311)

Appliance = Room
CeilingLamp = Room

warmwhite = Color.from_temperature(3000).darker(.85)

lichtburg = Building(
    # Wer weiß, was "LSTB" heißt? ;-)
    "Lichtburg LSTB",

    Space("Lobby", # Let's all go there!
          # Theke (die Theke sollte eigentlich am R-Kanel von dem Controller hängen, laut Beschriftung)
          Appliance("Popcorn Box", color=0x88ff00),

          # My Pixel strip's "white" is quite bluish and can be used as fridge light.
          Appliance("Bottle Fridges", lightnum=2, color=0xffffff),

          # The Lobby's main source of light. This must not be too bright as not to blot out the
          # other lights.
          CeilingLamp(lightnum=6, color=Color.from_temperature(2400).darker(.6))),

    # The Box Office.
    Room("Box Office", color=Color(0x884488).darker(.1)),

    Room("Entrance", lightnum=4, color=0xf06518),

    Room("First Floor Right", color=warmwhite),
    Room("First Floor Middle", color=warmwhite),
    Room("First Floor Left", color=warmwhite),

    Room("Second Floor Left", color=warmwhite),
    Room("Second Floor Middle", color=warmwhite),
    Room("Second Floor Right", color=warmwhite),

    Room("Third Floor Right", color=warmwhite),
    Room("Third Floor Middle", color=warmwhite),
    Room("Third Floor Left", color=warmwhite),

    # Backside
    Room("Third Floor Left (from the back)", color=warmwhite),
    Room("Third Floor Middle (from the back)", color=warmwhite),
    Room("Third Floor Bathroom (from the back)", color=warmwhite),

    Stairwell("Stairwell", lightnum=3),

    Room("Fourth Floor Right (from the back)", color=warmwhite),
    Room("Fourth Floor Middle (from the back)", color=warmwhite),
    Room("Fourth Floor Bathroom (from the back)", color=warmwhite),


    Room("Second Floor Left (from the back)", color=warmwhite),

    # The second floor back windows (which have very pretty curtains in them!) are hidden
    # by the movie theater's lower seats (and emergancy exists) and the projectionist's booth.
    Room("Hidden", color=0),
    Room("Hidden", color=0),
    #Room("Hidden", color=0),

    Booth(),
    Projector(),

    Attic(lightnum=7)
)
