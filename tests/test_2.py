# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
ST7789 Test Script for Raspberry Pi Zero 2 W
Shows full screen background and some text to verify orientation.
"""

import time
import board
import displayio
from adafruit_st7789 import ST7789
from fourwire import FourWire
from adafruit_display_text import label
import terminalio

# Release any previously used displays
displayio.release_displays()

# SPI bus and pins
spi = board.SPI()
tft_cs = board.CE0       # GPIO8
tft_dc = board.D25       # D/C
tft_rst = board.D24      # Reset

# Create the display bus
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)

# Create the display object
display = ST7789(
    display_bus,
    width=320,
    height=240,
    colstart=0,      # Corrected offset for your display
    rotation=90     # Adjust to match your physical orientation
)

# Create a display group
splash = displayio.Group()
display.root_group = splash

# Draw a full red background
color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFF0000  # Red
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Add some text labels to test orientation
texts = ["Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"]
positions = [
    (20, 20),
    (display.width - 20, 20),
    (20, display.height - 20),
    (display.width - 20, display.height - 20),
    (display.width // 2, display.height // 2)
]

for text, pos in zip(texts, positions):
    text_area = label.Label(
        terminalio.FONT,
        text=text,
        color=0xFFFF00,       # Yellow
        scale=2,
        anchor_point=(0.5, 0.5),
        anchored_position=pos
    )
    splash.append(text_area)

# Keep displaying
while True:
    time.sleep(1)

