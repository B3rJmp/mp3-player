from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7789

# SPI setup
serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=24, gpio_LIGHT=12, bus_speed_hz=40_000_000)
device = st7789(serial, width=320, height=240, rotate=0, bgr=True)

with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 40), "Hello World", fill="red")

