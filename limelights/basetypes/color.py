import colorsys

# Source: https://andi-siess.de/rgb-to-color-temperature/
# Thanks for that!

# Reference comments copied from Wikipedia
# https://en.wikipedia.org/wiki/Color_temperature
kelvin_table = {
    1000: (255, 56, 0, "Most commercial electric heating elements"),
    1100: (255, 71, 0),
    1200: (255, 83, 0),
    1300: (255, 93, 0),
    1400: (255, 101, 0),
    1500: (255, 109, 0),
    1600: (255, 115, 0),
    1700: (255, 121, 0, "Match flame, low pressure sodium lamps (LPS/SOX)"),
    1800: (255, 126, 0, "Candle flame, sunset/sunrise"),
    1900: (255, 131, 0),
    2000: (255, 138, 18),
    2100: (255, 142, 33),
    2200: (255, 147, 44),
    2300: (255, 152, 54),
    2400: (255, 157, 63, "Standard incandescent lamps"),
    2500: (255, 161, 72, "Soft white incandescent lamps"),
    2600: (255, 165, 79),
    2700: (255, 169, 87, "“Soft white” compact fluorescent and LED lamps"),
    2800: (255, 173, 94),
    2900: (255, 177, 101),
    3000: (255, 180, 107, "Warm white compact fluorescent and LED lamps"),
    3100: (255, 184, 114),
    3200: (255, 187, 120, "Studio lamps, photofloods, etc."),
    3300: (255, 190, 126),
    3400: (255, 193, 132),
    3500: (255, 196, 137),
    3600: (255, 199, 143),
    3700: (255, 201, 148),
    3800: (255, 204, 153),
    3900: (255, 206, 159),
    4000: (255, 209, 163),
    4100: (255, 211, 168),
    4200: (255, 213, 173),
    4300: (255, 215, 177),
    4400: (255, 217, 182),
    4500: (255, 219, 186),
    4600: (255, 221, 190),
    4700: (255, 223, 194),
    4800: (255, 225, 198),
    4900: (255, 227, 202),
    5000: (255, 228, 206, "Horizon daylight, Tubular fluorescent lamps or cool white/daylight compact fluorescent lamps (CFL)"),
    5100: (255, 230, 210),
    5200: (255, 232, 213),
    5300: (255, 233, 217),
    5400: (255, 235, 220),
    5500: (255, 236, 224, "Vertical daylight, electronic flash (lower limit)"),
    5600: (255, 238, 227),
    5700: (255, 239, 230),
    5800: (255, 240, 233),
    5900: (255, 242, 236),
    6000: (255, 243, 239, "Vertical daylight, electronic flash (upper limit)"),
    6100: (255, 244, 242),
    6200: (255, 245, 245, "Xenon short-arc lamp"),
    6300: (255, 246, 247),
    6400: (255, 248, 251),
    6500: (255, 249, 253, "Daylight, overcast"),
    6600: (254, 249, 255),
    6700: (252, 247, 255),
    6800: (249, 246, 255),
    6900: (247, 245, 255),
    7000: (245, 243, 255),
    7100: (243, 242, 255),
    7200: (240, 241, 255),
    7300: (239, 240, 255),
    7400: (237, 239, 255),
    7500: (235, 238, 255),
    7600: (233, 237, 255),
    7700: (231, 236, 255),
    7800: (230, 235, 255),
    7900: (228, 234, 255),
    8000: (227, 233, 255),
    8100: (225, 232, 255),
    8200: (224, 231, 255),
    8300: (222, 230, 255),
    8400: (221, 230, 255),
    8500: (220, 229, 255),
    8600: (218, 229, 255),
    8700: (217, 227, 255),
    8800: (216, 227, 255),
    8900: (215, 226, 255),
    9000: (214, 225, 255),
    9100: (212, 225, 255),
    9200: (211, 224, 255),
    9300: (210, 223, 255),
    9400: (209, 223, 255),
    9500: (208, 222, 255),
    9600: (207, 221, 255),
    9700: (207, 221, 255),
    9800: (206, 220, 255),
    9900: (205, 220, 255),
    10000: (207, 218, 255),
    10100: (207, 218, 255),
    10200: (206, 217, 255),
    10300: (205, 217, 255),
    10400: (204, 216, 255),
    10500: (204, 216, 255),
    10600: (203, 215, 255),
    10700: (202, 215, 255),
    10800: (202, 214, 255),
    10900: (201, 214, 255),
    11000: (200, 213, 255),
    11100: (200, 213, 255),
    11200: (199, 212, 255),
    11300: (198, 212, 255),
    11400: (198, 212, 255),
    11500: (197, 211, 255),
    11600: (197, 211, 255),
    11700: (197, 210, 255),
    11800: (196, 210, 255),
    11900: (195, 210, 255),
    12000: (195, 209, 255),
    15000: (255, 255, 255, "Clear blue poleward sky (maximum here)")}

class Color(int):
    @classmethod
    def from_rgb(Color, r:int, g:int, b:int):
        if r > 255: raise ValueError()
        if g > 255: raise ValueError()
        if b > 255: raise ValueError()
        return Color((r << 16) | (g << 8) | b)

    @classmethod
    def from_rgb_f(Color, r:float, g:float, b:float):
        # Keep these around in case we need them later.
        self = Color.from_rgb(round(r*255), round(g*255), round(b*255))
        self._rgb_f = r, g, b
        return self

    @classmethod
    def from_hls(Color, h:float, l:float, s:float):
        if h > 1.0: raise ValueError()
        if l > 1.0: raise ValueError()
        if s > 1.0: raise ValueError()

        self = Color.from_rgb_f(*colorsys.hls_to_rgb(h, l, s))
        self._hls = (h, l, s)
        return self

    @classmethod
    def from_temperature(Color, color_temperature:int):
        if color_temperature in kelvin_table:
            key = color_temperature
        else:
            keys = list(kelvin_table.keys())
            key = keys[min(range(len(keys)),
                           key = lambda i: abs(keys[i]-color_temperature))]

        return Color.from_rgb(*kelvin_table[key][:3])


    @property
    def r(self) -> int:
        return self >> 16

    @property
    def g(self) -> int:
        return (self & 0x00ff00) >> 8

    @property
    def b(self) -> int:
        return (self & 0x0000ff)

    @property
    def rgb(self) -> tuple[int]:
        return (self >> 16, (self & 0x00ff00) >> 8, self & 0x0000ff)

    @property
    def rgb_f(self) -> tuple[float]:
        if not hasattr(self, "_rgb_f"):
            self._rgb_f = tuple([channel / 255 for channel in self.rgb])
        return self._rgb_f

    @property
    def hls(self) -> tuple[float]:
        if not hasattr(self, "_hls"):
            h, l, s =  colorsys.rgb_to_hls(*self.rgb_f)
            self._hls = h, l, s
        return self._hls

    @property
    def h(self) -> float:
        """
        Most sources of visible light contain energy over a band
        of wavelengths. Hue is the wavelength within the visible light
        spectrum at which the energy output from a source is
        greatest. It is indicated by its position (in degrees) on the
        RGB color wheel: 0° <= h <= 360°
        """
        return self.hls[0]

    @property
    def l(self) -> float:
        """
        Luminosity (also called brightness, lightness or
        luminance) stands for the intensity of the energy output of a
        visible light source. It basically tells how light a color is
        and is measured on the following scale: 0 <= l <= 1
        """
        return self.hls[1]

    @property
    def s(self) -> float:
        """
        Saturation is an expression for the relative bandwidth of
        the visible output from a light source. As saturation
        increases, colors appear more pure. As saturation decreases,
        colors appear more washed-out. It is measured on the following
        scale: 0 <= s <= 1
        """
        return self.hls[2]

    def __repr__(self):
        return f"{self:06x}"

    # Darker and brigter are the same thing. It depends on your factor
    # not my function.
    def brighter(self, factor:float):
        return self.darker(f)

    def darker(self, factor:float):
        h,l,s = self.hls
        l = l*factor
        if l > 1.0:
            l = 1.0
        return self.__class__.from_hls(h, l, s)
