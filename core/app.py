# core/app.py

from time import sleep
from ui.shell import UIShell

class App:
    def __init__(self, action_bar):
        self.shell = UIShell(action_bar)
        self.display = None  # assign your luma display instance here

    def set_screen(self, screen):
        self.shell.set_screen(screen)

    def draw(self):
        if self.display:
            with self.display as draw:
                self.shell.draw(draw)
        else:
            # For testing without a physical display
            pass
        sleep(0.05)
