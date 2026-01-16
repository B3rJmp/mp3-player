# ui/screens/base.py

class Screen:
    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event):
        pass

    def draw(self, draw, region):
        pass
