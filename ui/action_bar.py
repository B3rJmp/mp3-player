# ui/action_bar.py

from time import monotonic

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (30, 30, 30)

BLINK_DURATION = 0.15  # seconds

class Action:
    """
    Represents a single icon-only action in the action bar.
    icon: callable(draw, cx, cy, fg_color)
    on_press: callback when button is pressed
    is_enabled: callable -> bool (optional)
    get_state: callable -> int (optional, e.g., repeat mode)
    """
    def __init__(self, icon, on_press, *, is_enabled=None, get_state=None):
        self.icon = icon
        self.on_press = on_press
        self.is_enabled = is_enabled
        self.get_state = get_state
        self._blink_until = 0.0

    def press(self):
        if self.on_press:
            self.on_press()
        self._blink_until = monotonic() + BLINK_DURATION

    def is_blinking(self):
        return monotonic() < self._blink_until

    def enabled(self):
        if self.is_enabled:
            return bool(self.is_enabled())
        if self.get_state:
            return self.get_state() != 0
        return False


class ActionBar:
    def __init__(self, display, *, height=32, padding=4, bg=DARK):
        self.display = display
        self.height = height
        self.padding = padding
        self.bg = bg
        self.actions = []

    def set_actions(self, actions):
        self.actions = actions

    def handle_button(self, index):
        if 0 <= index < len(self.actions):
            self.actions[index].press()

    def draw(self, draw):
        width = getattr(draw, 'width', 240)
        count = len(self.actions)
        if count == 0:
            return

        slot_width = width // count

        # Draw background bar
        draw.rectangle((0, 0, width, self.height), fill=self.bg)

        for i, action in enumerate(self.actions):
            x0 = i * slot_width
            blinking = action.is_blinking()
            enabled = action.enabled()

            if blinking:
                bg = WHITE
                fg = BLACK
            elif enabled:
                bg = WHITE
                fg = BLACK
            else:
                bg = DARK
                fg = WHITE

            draw.rectangle((x0, 0, x0 + slot_width, self.height), fill=bg)

            # Draw icon centered
            if action.icon:
                cx = x0 + slot_width // 2
                cy = self.height // 2
                action.icon(draw, cx, cy, fg)
