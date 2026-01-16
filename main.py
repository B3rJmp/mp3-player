from core.app import App
from ui.action_bar import ActionBar, Action
from ui.screens.now_playing import NowPlayingScreen
from time import sleep

# Dummy icon draw function
def draw_icon(draw, cx, cy, color):
    draw.ellipse((cx-4, cy-4, cx+4, cy+4), fill=color)

# Create action bar
action_bar = ActionBar(None)
actions = [
    Action(draw_icon, lambda: print("BTN1 pressed")),
    Action(draw_icon, lambda: print("BTN2 pressed")),
    Action(draw_icon, lambda: print("BTN3 pressed")),
    Action(draw_icon, lambda: print("BTN4 pressed")),
]
action_bar.set_actions(actions)

# Create app and shell
app = App(action_bar)
app.set_screen(NowPlayingScreen())

# Main loop (dummy loop for testing)
while True:
    # Replace with actual input reads
    # Example: simulate BTN2 press every 2 seconds
    import random
    if random.random() < 0.01:
        action_bar.handle_button(1)
    app.draw()
    sleep(0.05)
