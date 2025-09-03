# main.py

from core.app import App
from ui.action_bar import ActionBar, Action
from ui.screens.now_playing import NowPlayingScreen

from luma.core.interface.serial import spi
from luma.lcd.device import st7789
from luma.core.render import canvas

from time import sleep
import board
import busio
import adafruit_seesaw.seesaw as seesaw

# ---------------------------
# SPI display setup
# ---------------------------
serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=24, bus_speed_hz=40_000_000)
device = st7789(serial, width=320, height=240, rotate=0)

# ---------------------------
# NeoKey 1x4 + rotary encoder setup
# ---------------------------
i2c_bus = busio.I2C(board.SCL, board.SDA)
ss = seesaw.Seesaw(i2c_bus, addr=0x30)

# Button state read
def read_buttons():
    return [ss.digital_read(i) == 0 for i in range(4)]  # active low

# ---------------------------
# Dummy icon
# ---------------------------
def draw_icon(draw, cx, cy, color):
    draw.ellipse((cx-6, cy-6, cx+6, cy+6), fill=color)

# ---------------------------
# Action bar
# ---------------------------
action_bar = ActionBar()
actions = [
    Action(draw_icon, lambda: print("BTN1 pressed")),
    Action(draw_icon, lambda: print("BTN2 pressed")),
    Action(draw_icon, lambda: print("BTN3 pressed")),
    Action(draw_icon, lambda: print("BTN4 pressed")),
]
action_bar.set_actions(actions)

# ---------------------------
# App
# ---------------------------
app = App(action_bar, device)
app.set_screen(NowPlayingScreen())

# ---------------------------
# Main loop
# ---------------------------
while True:
    # Read NeoKey buttons
    buttons = read_buttons()
    for idx, pressed in enumerate(buttons):
        if pressed:
            action_bar.handle_button(idx)
    
    # Draw to display
    app.draw()
    sleep(0.05)
