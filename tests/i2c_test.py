# i2c_neokey_encoder_test_v2.py
import time
import board
import busio
from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw.rotaryio import IncrementalEncoder
from adafruit_seesaw.digitalio import DigitalIO

# --- I2C bus ---
i2c = busio.I2C(board.SCL, board.SDA)

# --- NeoKey 1x4 buttons ---
NEOKEY_ADDR = 0x30
neokey = NeoKey1x4(i2c, addr=NEOKEY_ADDR)

# --- Rotary encoder ---
ENCODER_ADDR = 0x36
seesaw = Seesaw(i2c, addr=ENCODER_ADDR)
encoder = IncrementalEncoder(seesaw)
last_position = encoder.position

# --- Rotary push button ---
# Pin depends on board revision; many Adafruit boards use pin 24
rotary_button = DigitalIO(seesaw, 24)
rotary_button.switch_to_input(pull="UP")  # active low
last_rotary_pressed = True  # assume released

# --- Track NeoKey button states ---
last_button_states = [False] * 4

print("NeoKey + Rotary Encoder Test v2")
print("Press buttons or rotate the encoder...")

try:
    while True:
        # --- NeoKey buttons ---
        for i in range(4):
            pressed = neokey[i]
            if pressed != last_button_states[i]:
                last_button_states[i] = pressed
                print(f"Button {i+1}: {'Pressed' if pressed else 'Released'}")

            # Update LED under the button (red when pressed)
            neokey.pixels[i] = (255, 0, 255) if pressed else (0, 0, 0)

        # --- Rotary encoder rotation ---
        position = encoder.position
        delta = position - last_position
        if delta != 0:
            print(f"Encoder rotated: {delta:+d}")
            last_position = position

        # --- Rotary push button ---
        pressed = not rotary_button.value  # active-low
        if pressed != (not last_rotary_pressed):
            last_rotary_pressed = not pressed
            print(f"Rotary button: {'Pressed' if pressed else 'Released'}")     

        time.sleep(0.05)

except KeyboardInterrupt:
    # Turn off LEDs on exit
    for i in range(4):
        neokey.pixels[i] = (0, 0, 0)
    print("\nExiting NeoKey + Encoder test v2")

