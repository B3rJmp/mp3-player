from .layout import ACTION_BAR_REGION, CONTENT_REGION

class UIShell:
    def __init__(self, display, action_bar, screen):
        self.display = display
        self.action_bar = action_bar
        self.screen = screen

    def handle_event(self, event):
        # Forward button presses to action bar first
        if hasattr(event, "index") and event.type == "button":
            self.action_bar.handle_button(event.index)
        # Forward everything to screen
        self.screen.handle_event(event)

    def draw(self):
        draw = self.display.draw()  # Assume display has a context manager
        self.action_bar.draw()
        self.screen.draw(draw, CONTENT_REGION)
        self.display.show()
