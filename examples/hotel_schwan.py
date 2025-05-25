# Hotel Schwan
# ------------

# This is the first model house I ever equipped with ws2811 pixel leds.
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

from limelights.model import Building, Room, HotelRoom, Fireplace, Stairwell

hotel_schwan = Building(
    "Hotel Schan",
    # Auhagen Stadthaus H0, Schmidtstraße 39 „Hotel Schwan“
    # https://www.auhagen-shop.de/Stadthaus-H0-Schmidtstrasse-39-Hotel-Schwan/11471

    # Front façade (except for top floor)
    HotelRoom("Second Floor left Single bed room"),
    HotelRoom("Third Floor left Single bed room"),
    HotelRoom("Fourth Floor left Single bed room"),
    HotelRoom("Second Floor Double bed room", lightnum=2),
    HotelRoom("Third Floor Double bed room", lightnum=2),
    HotelRoom("Fourth Floor Double bed room", lightnum=2),
    HotelRoom("Second Floor right Single bed room"),
    HotelRoom("Third Floor right Single bed room"),
    HotelRoom("Fourth Floor right Single bed room"),

    # Back view
    Stairwell(lightnum=3),

    # I assume the back windows to be flats rather than hotel rooms.
    # That’s an arbitrary decision, really, they might just as well be
    # hotel rooms except for the rooms the Schwan family occupies.
    Room("First floor flat"),
    Room("Second floor flat right window"),
    Room("Second floor float two left windows"),
    Room("Third floor flat right window"),
    Room("Third floor float two left windows"),
    Room("Fourth floor float two left windows"),
    Room("Fourth floor flat right window"),

    # I put curtain designs in the front rooms at the top,
    # because I grew up in a small hotel and my siter and I
    # had our rooms in the attic.
    Room("Children’s top floor room", lightnum=2))
