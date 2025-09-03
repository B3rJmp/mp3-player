# neokey_test.py
import time
import board
import busio
from adafruit_neokey.neokey1x4 import NeoKey1x4

i2c = busio.I2C(board.SCL, board.SDA)
neokey = NeoKey1x4(i2c, addr=0x30)

print("NeoKey 1x4 test - press buttons...")

last_states = [False] * 4

while True:
    for i in range(4):
        pressed = neokey[i]
        if pressed != last_states[i]:
            print(f"Button {i+1} {'Pressed' if pressed else 'Released'}")
            last_states[i] = pressed
    time.sleep(0.05)

