import dataclasses
import icecream
icecream.install()

@dataclasses.dataclass
class Config(object):
    framerate = 24
    speed = 1

config = Config()
