from limelights.basetypes import Color
from limelights.model import (Building, Space, Room, HotelRoom, Fireplace,
                              Stairwell)
from limelights.animations import on, off, tv, limit, candle, darker

warmwhite = Color(0x553311)

Appliance = Room
CeilingLamp = Room

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

    Room("Entrance", lightnum=4, color=Color.from_temperature(2400).darker(.85)),


    Room("END MARKER", color=0xff0000))
