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
        if event.get("type") == "button":
            self.action_bar.handle_button(event["index"])
            return
        if self.screen:
            self.screen.handle_event(event)

    def draw(self, draw):
        self.action_bar.draw(draw)

        if self.screen:
            region = (0, self.action_bar.height, draw.width, draw.height)
            self.screen.draw(draw, region)
