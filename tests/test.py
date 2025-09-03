import time
import board
import displayio
from fourwire import FourWire
from adafruit_st7789 import ST7789

# Release any displays already in use
displayio.release_displays()

# SPI bus
spi = board.SPI()
cs = board.CE0
dc = board.D25
rst = board.D24

# Create display bus
display_bus = FourWire(
    spi,
    command=dc,
    chip_select=cs,
    reset=rst,
    baudrate=24000000
)

# IMPORTANT: These values are SPECIFIC to Adafruit #4311
display = ST7789(
    display_bus,
    width=320,
    height=240,
    colstart=0,     # REQUIRED for round-rectangle panel
    rowstart=0,
    rotation=270    # Works with typical Pi orientation
)

# Create a display group
group = displayio.Group()
display.root_group = group

# Solid color fill
bitmap = displayio.Bitmap(display.width, display.height, 1)
palette = displayio.Palette(1)
palette[0] = 0xFF0000  # BRIGHT RED

tilegrid = displayio.TileGrid(bitmap, pixel_shader=palette)
group.append(tilegrid)

print("Display should now be solid RED")
time.sleep(30)

