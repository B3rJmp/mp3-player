# core/app.py

from time import sleep
from ui.shell import UIShell
from luma.core.render import canvas

class App:
    def __init__(self, action_bar, display):
        self.shell = UIShell(action_bar)
        self.display = display

    def set_screen(self, screen):
        self.shell.set_screen(screen)

    def handle_event(self, event):
        self.shell.handle_event(event)

    def draw(self):
        with canvas(self.display) as draw_ctx:
            self.shell.draw(draw_ctx)
        sleep(0.05)
