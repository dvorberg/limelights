# Wiener Caféhaus
# ---------------

from random import random, randint

from limelights.basetypes import randmins, randsecs, Color
from limelights.model import (Building, Space, Room, HotelRoom, Fireplace,
                              Stairwell, CandleRoom, EndMarker)
from limelights.animations import on, off, tv, limit, candle, darker

warmwhite = Color(0x553311)

class Bakery(Room):
    def __init__(self, *lights, lightnum=1):
        super().__init__(*lights, lightnum=lightnum,
                         color=Color(0xdddddd).darker(1.8))

class Flat(Space):
    pass

class Restaurant(Room):
    # The walls of the model are very thin. Light shines gthrough the plastic.
    # That’s why I light those rooms rather darkly. But since the windows are
    # clear (rather than having paper “curtains”,) the effect is quite
    # pleasing, I think.
    # The lights in the restaurant are constantly on. There are constantly
    # model people in there so we won’t leave them in the dark.
    def __init__(self, *lights, lightnum=1, color=warmwhite):
        super().__init__(*lights, lightnum=lightnum, color=color.darker(.32))

class Office(Space):
    # At a later time there might be office hours. Right now the staff is
    # working all the time. Ouch!
    pass

class StudentAppartment(Room):
    """
    The students are home most of the time, mostly studying, as good students
    should. Occasionally they take a break to watch TV. Sometimes they light
    the room with a candle to smoke joint or make love or both.
    """
    def __init__(self, *lights, lightnum=1):
        super().__init__(*lights, lightnum=lightnum)

        if random() > .8:
            self._color=warmwhite.darker(.5)
        else:
            self._color=Color(0xffbbbb).darker(.25)

    def animations(self):
        r = random()
        if r < .35:
            # Sleeping
            yield limit(self.off(), randmins(30,90))
        elif r < .5:
            # Studying
            yield limit(self.on(), randmins(30,90))
            # One can’t really study more than 90mins at once effectively.
        elif r < .9:
            # Taking a break…
            yield limit(darker(tv(), .33), randmins(30,45))
        else:
            # …long break!
            yield limit(candle(), randmins(45,90))

class Flashlight(Room):
    """
    The flashlight is a ws2811 controller hooked up to three cold
    white LEDs. Every couple of minutes it will flash a couple of times.
    """
    def animations(self):
        for a in range(randint(9, 20)):
            yield self.flash()
            yield limit(off(), randsecs(.4, 1.5))
        yield limit(off(), randmins(0.5,2))

    def flash(self):
        yield 0xffffff

# The flat’s room are not interdependent.
class Bedroom(Room):
    def __init__(self, *lights, lightnum=1, color=warmwhite):
        super().__init__(*lights, lightnum=lightnum, color=color.darker(.33))

    def animations(self):
        # You spend about a third of the day in bed, right? Right??
        if random() > .6:
            if random() > .75:
                yield limit(candle(), randmins(15, 30))
            else:
                yield limit(self.on(), randmins(15, 25))
        else:
            yield self.off()

class Kitchen(Room):
    def __init__(self, *lights, lightnum=1):
        super().__init__(*lights, lightnum=lightnum,
                         color=Color(0xffeeee).darker(.25))

    def animations(self):
        # Takes about 45–90mins to cook a decent meal.
        if random() > .75:
            yield limit(self.on(), randmins(45, 90))
        else:
            yield self.off()

class Livingroom(Room):
    def __init__(self, *lights, lightnum=1, color=warmwhite):
        super().__init__(*lights, lightnum=lightnum, color=color.darker(1/1.6))

    def animations(self):
        r = random()
        if r < .3:
            yield limit(self.off(), randmins(45, 90))
        elif r < .6:
            yield limit(self.on(), randmins(45, 90))
        else:
            yield limit(tv(), randmins(45, 90))


wiener_cafehaus = Building(
    "Wiener Caféhaus",
    # Vissmann/Volmer 43618 H0 Wiener Kaffeehaus
    # https://viessmann-modell.com/spur-h0/gebaeude/stadt/1194h0-wiener-kaffeehaus/43618

    Flat( Bedroom("Fourth Floor Back right", color=warmwhite.darker(1/1.6)),
          Bedroom("Fourth Floor Front right"),
          Livingroom("Fourth Floor Front center"),
          Bedroom("Fourth Floor Front left"),
          Kitchen("Fourth Floor Back left")),

    Room("Fotostudio", lightnum=2, color=warmwhite.darker(1/1.5)),
    Room("Fotostudio Backroom", lightnum=3, color=warmwhite.darker(.5)),
    Flashlight("Flashlight!"),

    # The third floor has offices in the front rooms.
    # I have used to decorations provided by the manufacturer
    # but offset them several milimeters from the windws to be back-lit.
    # The middle window uses my 60g/m² paper curtains.
    # The two back rooms are rented out as single bedroom appartments
    # to students at the local university, see above.
    StudentAppartment("Third Floor Back left"),
    Office( Room("Third Floor Front right", color=0xffdddd),
            Room("Third Floor Front center", color=warmwhite.darker(1/2.5)),
            Room("Third Floor Front left", color=0xff9999)),
    StudentAppartment("Third Floor Back right"),

    StudentAppartment("Second Floor Back left"),
    Restaurant("Second Floor Restaurant", lightnum=3),
    StudentAppartment("Second Floor Back right"),

    Bakery(),

    Restaurant("Ground Floor", lightnum=3),

    Stairwell(lightnum=4),

    EndMarker()
)
