from core.input import read_event

class App:
    """
    Main app controller.
    Owns the screen stack / shell.
    Handles main loop and event dispatch.
    """
    def __init__(self, shell):
        self.shell = shell
        self.running = True

    def run(self):
        while self.running:
            event = read_event()
            if event:
                self.shell.handle_event(event)
            self.shell.draw()
