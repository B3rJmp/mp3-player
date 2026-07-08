import time
import RPi.GPIO as GPIO
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7789

GPIO.setwarnings(False)  # <-- suppress warnings

# SPI setup
serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=24, bus_speed_hz=40_000_000)
device = st7789(serial, width=320, height=240, rotate=2, bgr=True)

# BACKLIGHT_PIN = 12
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(BACKLIGHT_PIN, GPIO.OUT)
# GPIO.output(BACKLIGHT_PIN, GPIO.HIGH)  # turn on

try:
    while True:
        with canvas(device) as draw:
            action_bar_height = 30
            action_items = ["first","second","third","fourth"]
            for i in action_items:
                x0 = i * (device.width/len(action_items))
                y0 = 0
                x1 = x0 + (device.width/len(action_items)) - 1
                y1 = action_bar_height
                draw.rectangle((x0,y0,x1,y1), outline="white", fill="black")
            draw.text((30, 40), "Hello World", fill="red")
        time.sleep(0.5)
except KeyboardInterrupt:
    # GPIO.output(BACKLIGHT_PIN, GPIO.LOW)  # turn off
    device.clear()
    print("\nExiting")