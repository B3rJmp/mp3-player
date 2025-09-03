import time
import RPi.GPIO as GPIO
from luma.core.interface.serial import spi
from luma.lcd.device import st7789
from luma.core.render import canvas
from PIL import ImageFont

GPIO.setwarnings(False)  # <-- suppress warnings

# SPI setup
serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=24, bus_speed_hz=40_000_000)
device = st7789(serial, width=320, height=240, rotate=0, bgr=True)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
text = "Hello World"
colors = ["red", "green", "blue"]

def center_text(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (device.width - w) // 2
    y = (device.height - h) // 2
    return x, y

try:
    while True:
        for color in colors:
            with canvas(device) as draw:
                x, y = center_text(draw, text, font)
                draw.text((x, y), text, fill=color, font=font)
            time.sleep(0.5)
except KeyboardInterrupt:
    device.clear()
    print("\nExiting luma_test.py")

