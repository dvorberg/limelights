from .animation import Change, Changes
from .color import Color
from termcolor import colored

class Light(object):
    """
    Abstract baseclass for those things that control one or more
    pixels which all display the same color. A Changeble is running a
    single animation at all times.
    """
    def engine_init(self, engine):
        raise NotImplementedError()

    def change_to(self, color) -> Change:
        raise NotImplementedError()

    @property
    def indeces(self):
        return set()

    def print_items(self, level=0):
        raise NotImplementedError()

class Lights(list):
    @property
    def indeces(self):
        ret = set()
        for a in self:
            ret.update(a.indeces)
        return ret

    @property
    def pixels(self):
        return sorted([item for item in self
                       if getattr(item, "idx", None) is not None])



    def print_items(self, strip=None, level=0):
        print(level*"  " + self._info() + (self._colorinfo(strip) or ""))

        for item in self:
            if hasattr(item, "print_items"):
                item.print_items(strip, level+1)

    def _info(self):
        ids = sorted(list(self.indeces))
        s = []
        while ids:
            n = ids[0]
            ids = ids[1:]
            m = n
            while (ids and ids[0] == m+1):
                m = ids[0]
                ids = ids[1:]

            if n == m:
                s.append(str(n))
            else:
                s.append(f"{n}–{m}")

        typename = self.__class__.__name__
        s = ",".join(s)
        return f"[{s}] {typename}"

    def _colorinfo(self, strip):
        if strip:
            ids = sorted(list(self.indeces))
            def color(i):
                c = Color(strip[i])
                return colored(c, color="red") # , on_color=c.rgb
            return " " + " ".join([f"{i}:{color(i)}" for i in ids])

    def __repr__(self):
        lst = super().__repr__()[1:-1]
        return f"[{self._info()} {lst}]"


class Lamp(Lights, Light):
    """
    A Lamp is a collection of multiple Lights that show the same
    color. It implements the Light interface and can be used anywhere
    a Light can be used.
    """
    def __init__(self, *items):
        super().__init__(items)

    def engine_init(self, engine):
        for item in self:
            item.engine_init(engine)

    def change_to(self, color) -> Change:
        return Changes([item.change_to(color) for item in self])

class NameableLights(Lights):
    """
    A Nameable is a list of things that also accepts strings as
    parameters. The first string passed is considered the object’s
    name for identification in debug output.
    """
    def __init__(self, *items):
        """
        Specific `items` may be passed as positional parameters. If a
        string is passed among the items, it is assumed to be the space’s
        name.
        """
        super().__init__()

        self._name = f"{self.__class__.__name__} 0x{id(self):x}"

        for item in items:
            if type(item) is str:
                self._name = item
            else:
                self.append(item)

    def engine_init(self, engine):
        for item in self:
            item.engine_init(engine)

    def _info(self):
        info = super()._info()
        if name := self.name:
             return f"{info} “{name}”"
        else:
            return info

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        else:
            return None
