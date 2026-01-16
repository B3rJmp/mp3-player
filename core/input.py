# Minimal stub for testing
class ButtonEvent:
    def __init__(self, button, pressed):
        self.type = "button"
        self.button = button
        self.pressed = pressed

class EncoderEvent:
    def __init__(self, delta=0, pressed=False):
        self.type = "encoder"
        self.delta = delta
        self.pressed = pressed

def read_event():
    # Replace with your NeoKey + rotary code later
    return None
