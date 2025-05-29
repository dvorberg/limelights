# Hotel Schwan
# ------------

# This is the first model house I ever equipped with ws2811 pixel LEDs.
# The cabeling is not quite optimal, I guess.

# 0 Einzelzimmer 1. Stock links
# 1 Einzelzimmer 2. Stock links
# 2 Einzelzimmer 3. Stock links
# 3+4 Doppelzimmer 1. Stock
# 5+6 Doppelzimmer 2. Stock
# 7+8 Doppelzimmer 3. Stock
# 9 Treppenhaus
# 10 Treppenhaus
# 11 Flur (hinter der Haustür hinten, gehört zum Minutenlicht)
# 12 Wohnung Erdgeschoss (zwei Fenster)
# 13 Wohnung 1. Stock rechtes Fenster
# 14 Wohnung 1. Stock zwei linke Fenster
# 15 Wohnung 2. Stock rechtes Fenster
# 16 Wohnung 2. Stock zwei linke Fenster
# 17 Wohnung 3. Stock zwei linke Fenster
# 18 Wohnung 3. Stock rechtes Fenster
# 19 Einzelzimmer 1. Stock rechts
# 20 Einzelzimmer 2. Stock rechts
# 21 Einzelzimmer 3. Stock rechts
# 22+23 Kinderzimmer

import random

from limelights.basetypes import randmins, Color
from limelights.model import (Building, Space, Room, HotelRoom, Fireplace,
                              Stairwell, CandleRoom)
from limelights.animations import on, off, tv, limit, candle

class Flat(Space):
    """
    A Flat in Hotel Schwan’s backside has a two-window living room
    and a bedroom with a single window. This class will coordinate
    times of:
    - No-one being home (the flat is dark)
    - The occupants are spenging time in the living room
      - Reading or playing a game by a warm light
      - OR watching TV, which will have its own glow.
      After that there will be a brief time when they are going back and forth
      between the living room and the bedroom and leave the light on in both.
      Occasionly the occupants will light a candle in the bedroom after
      lights out and have some quality time together for, you know,
      “conversation.”
    """

    def __init__(self, athome=.3, **kw):
        """
        The constructor expexts a bedroom= and a livingroom= Light to be
        passed as named parameters. The generic **kw= is used so the order
        of the lights will be preserved for the engine_init() method.
        """
        self.athome=athome

        self.livingroom = kw["livingroom"]
        self.bedroom = kw["bedroom"]

        for room in kw.values():
            self.append(room)

        # The livingroom leads. It sets the animations property of
        # the bedroom source.
        self.livingroom.source.animations = self.livingroom_animations

    def livingroom_animations(self):
        # These are for the dependent (bedroom) source.
        def on_(room):
            yield room.on()

        def off_():
            yield off()

        def candle_():
            yield limit(candle(), randmins(12, 16))
            yield off()

        # There is a .3 change of someone being at home by default.
        # Turn the bedroom lights off. (Not needed, I think.)
        self.bedroom.source.animations = off_
        if random.random() >= self.athome:
            if random.random() > .5: # Watch TV?
                yield limit(tv(), randmins(15, 35))
            else:
                yield limit(self.livingroom.on(), randmins(25, 45))

            # It takes about 10min to go to bed, I guess.
            self.bedroom.source.animations = self.bedroom.animations
            yield limit(self.livingroom.on(), randmins(7, 12))

            if random.random() > .5: # This factor might vary with age.
                self.bedroom.source.animations = candle_

            # Turn the living room lights off.
            # The minumum here must be >= the maximum of the candle,
            # otherwise the animations will overlap. But well…
            yield limit(off(), randmins(16, 45)) # Good night!
        else:
            yield limit(off(), randmins(15, 45))

class VictorsRoom(Room):
    """
    In the back of the hotel, on the bottom floor, the hotel has a
    one room appartment that the Schwan family happily rent out to
    Victor. He is not a fancy man or anything, but he runs a tidy ship
    and his landlords surely appreciate that. He doesn’t have textile
    curtains like his neighbours, but simple role up blinds. His room
    is decorated with trophys and plaques that document his
    achivements as an amateur athelete and a big poster of a football
    team from his Slavic homeland. He framed signed photographs of
    some of his heroes and put up a picture of the old team at the
    warehouse right next to them. Now that he’s retired he likes to
    rest the old bones. More often than not you’ll find him watching
    the television. Otherwise he’s talking to his brother on the phone
    or reading the sports paper by the light of a simple neon tube
    that emits a cold bluish light.
    """
    def __init__(self, name):
        # The default constructor will do for Victor’s room.
        # The color is a white even bluer thant the default of that
        # Pixel I glued there.
        super().__init__(name, color=Color(0xeeffee).darker(1.2))

    def animations(self):
        if random.random() < .8:
            # Victor’s home…
            if random.random() > .7:
                # …reading or on the phone…n
                yield limit(self.on(), randmins(15, 30))
            else:
                # …or watching TV.
                yield limit(tv(), randmins(20, 56))
        else:
            # Vicor is out or sleeping.
            yield limit(self.off(), randmins(15, 35))


hotel_schwan = Building(
    "Hotel Schwan",
    # Auhagen Stadthaus H0, Schmidtstraße 39 „Hotel Schwan“
    # https://www.auhagen-shop.de/Stadthaus-H0-Schmidtstrasse-39-Hotel-Schwan/11471

    # Front façade (except for top floor)
    HotelRoom("Second Floor left Single bed room"),
    HotelRoom("Third Floor left Single bed room"),
    HotelRoom("Fourth Floor left Single bed room"),
    HotelRoom("Second Floor Double bed room", lightnum=2),
    HotelRoom("Third Floor Double bed room", lightnum=2),
    HotelRoom("Fourth Floor Double bed room", lightnum=2),

    # Back view
    Stairwell(lightnum=3),

    # I assume the back windows to be flats rather than hotel rooms.
    # That’s an arbitrary decision, really, they might just as well be
    # hotel rooms except for the rooms the Schwan family occupies.
    VictorsRoom("First floor flat"),

    Flat(bedroom=Room("Second floor flat right window",
                      color=0x553311),
         livingroom=Room("Second floor float two left windows",
                         color=0x553311)),

    Flat(bedroom=Room("Third floor flat right window",
                      color=0x553311),
         livingroom=Room("Third floor float two left windows",
                         color=0x993311)), # Pinkish light for plant growth.

    Flat(livingroom=Room("Fourth floor float two left windows",
                         color=0xaa8888),
         bedroom=Room("Fourth floor flat right window",
                      color=0x553311)),

    # Back to the front. The order of the lights was determined by the order
    # in which I built them into the model.
    HotelRoom("Second Floor right Single bed room"),
    HotelRoom("Third Floor right Single bed room"),
    HotelRoom("Fourth Floor right Single bed room"),

    # I put curtain designs in the front rooms at the top,
    # because I grew up in a small hotel and my siter and I
    # had our rooms in the attic.
    Room("Children’s top floor room", lightnum=2, color=0x553311))
