# ui/shell.py

class UIShell:
    def __init__(self, action_bar):
        self.action_bar = action_bar
        self.screen = None

    def set_screen(self, screen):
        if self.screen:
            self.screen.on_exit()
        self.screen = screen
        self.screen.on_enter()

    def handle_event(self, event):
        # Give action bar first shot at buttons
        if event.get("type") == "button":
            self.action_bar.handle_button(event["index"])
            return

        # Otherwise forward to screen
        if self.screen:
            self.screen.handle_event(event)

    def draw(self, draw):
        # Draw action bar at top
        self.action_bar.draw(draw)

        # Draw screen content below
        if self.screen:
            region = (0, self.action_bar.height, getattr(draw, 'width', 240), getattr(draw, 'height', 240))
            self.screen.draw(draw, region)
