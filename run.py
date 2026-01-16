from core.app import App
from ui.action_bar import ActionBar, Action
from ui.screens.now_playing import NowPlayingScreen
from ui.shell import UIShell
from luma.core.interface.serial import spi
from luma.lcd.device import st7789
from PIL import ImageDraw

# --- 1. Setup SPI display ---
serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=24)
display = st7789(serial, width=320, height=240)

# --- 2. Setup action bar ---
def draw_icon(d, cx, cy, color):
    size = 10
    d.rectangle((cx-size, cy-size, cx+size, cy+size), fill=color)

actions = [
    Action(draw_icon, lambda: print("BTN1")),
    Action(draw_icon, lambda: print("BTN2")),
    Action(draw_icon, lambda: print("BTN3")),
    Action(draw_icon, lambda: print("BTN4")),
]

action_bar = ActionBar(display)
action_bar.set_actions(actions)

# --- 3. Create the initial screen ---
screen = NowPlayingScreen()

# --- 4. Create shell ---
shell = UIShell(display, action_bar, screen)

# --- 5. Create and run app ---
app = App(shell)
app.run()
