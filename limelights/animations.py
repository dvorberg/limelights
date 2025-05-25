def on(color):
    yield color

def off():
    yield 0

def tv():
    while True:
        for a in ( 0xff, 0xff00, 0xff0000 ):
            yield a

            for b in range(6):
                yield None
