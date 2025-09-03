import busio
from adafruit_seesaw.rotaryio import IncrementalEncoder
from adafruit_seesaw.seesaw import Seesaw

seesaw = Seesaw(busio.I2C(board.SCL, board.SDA), addr=0x36)
encoder = IncrementalEncoder(seesaw, 0)  # first encoder interface

last_position = encoder.position
while True:
    position = encoder.position
    delta = position - last_position
    if delta:
        print(f"Encoder moved: {delta:+d}")
        last_position = position

