"""Base Screen - Abstract base class for all screens"""
from abc import ABC, abstractmethod
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, TYPE_CHECKING
import logging

from claude.ui.action_bar import ActionBar, ActionIcon

if TYPE_CHECKING:
    from claude.core.input_manager import InputEvent

logger = logging.getLogger(__name__)


class BaseScreen(ABC):
    """
    Abstract base class for all screens.

    Screens have lifecycle methods (on_enter, on_exit) and handle input events.
    Each screen manages its own state and button configurations via action bar.
    """

    # Display dimensions (ST7789)
    DISPLAY_WIDTH = 320
    DISPLAY_HEIGHT = 240

    # Action bar height
    ACTION_BAR_HEIGHT = 36

    # Content area starts below action bar
    CONTENT_Y_START = ACTION_BAR_HEIGHT

    # Color palette
    COLOR_BLACK = (0, 0, 0)
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLUE = (0, 100, 255)
    COLOR_GREEN = (0, 255, 0)
    COLOR_RED = (255, 0, 0)
    COLOR_YELLOW = (255, 255, 0)
    COLOR_CYAN = (0, 255, 255)
    COLOR_MAGENTA = (255, 0, 255)
    COLOR_GRAY = (128, 128, 128)
    COLOR_DARK_GRAY = (64, 64, 64)

    def __init__(self, app):
        """
        Initialize base screen.

        Args:
            app: Reference to main application instance
        """
        self.app = app
        self.mpd = app.mpd_service
        self.bluetooth = app.bluetooth_service
        self.needs_render = True

        # Action bar (shows button icons at top)
        self.action_bar = ActionBar(width=self.DISPLAY_WIDTH)

        # Legacy button configuration (for LED control)
        self.button_colors = [self.COLOR_BLACK] * 4

    @abstractmethod
    def on_enter(self):
        """Called when screen becomes active"""
        logger.info(f"{self.__class__.__name__} entered")
        self.needs_render = True
        self.update_buttons()

    @abstractmethod
    def on_exit(self):
        """Called when screen is deactivated"""
        logger.info(f"{self.__class__.__name__} exited")

    def render_base(self, draw: ImageDraw.ImageDraw):
        """
        Render base elements (action bar), then call screen-specific render.
        Called by app, not by screens directly.

        Args:
            draw: PIL ImageDraw object to draw on
        """
        # Render action bar at top
        self.action_bar.render(draw)

        # Let screen render its content below action bar
        self.render_content(draw)

    @abstractmethod
    def render_content(self, draw: ImageDraw.ImageDraw):
        """
        Render screen-specific content below action bar.
        Screens should draw content starting from CONTENT_Y_START.

        Args:
            draw: PIL ImageDraw object to draw on
        """
        pass

    @abstractmethod
    def handle_button(self, button_index: int):
        """
        Handle button press.

        Args:
            button_index: 0-3 for the four buttons
        """
        pass

    def handle_encoder_rotate(self, delta: int):
        """
        Handle rotary encoder rotation.
        Default implementation does nothing - override in subclasses.

        Args:
            delta: Rotation delta (negative=CCW, positive=CW)
        """
        pass

    def handle_encoder_press(self):
        """
        Handle rotary encoder button press.
        Default implementation does nothing - override in subclasses.
        """
        pass

    def update_buttons(self):
        """Update button LED colors based on current configuration"""
        if self.app.input_manager:
            self.app.input_manager.set_all_button_colors(self.button_colors)

    def configure_action_bar(
        self,
        icons: list[ActionIcon],
        colors: list[Tuple[int, int, int]],
        enabled: Optional[list[bool]] = None
    ):
        """
        Configure action bar icons and button LEDs.

        Args:
            icons: List of 4 ActionIcon enums
            colors: List of 4 RGB color tuples
            enabled: List of 4 booleans for icon enabled state (optional)
        """
        self.action_bar.configure(icons, colors, enabled)
        self.button_colors = colors
        self.update_buttons()

    def request_render(self):
        """Mark screen as needing re-render"""
        self.needs_render = True

    # Helper drawing methods
    def draw_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        position: Tuple[int, int],
        font=None,
        fill=None,
        align: str = "left",
        max_width: Optional[int] = None
    ):
        """
        Draw text with optional truncation.

        Args:
            draw: ImageDraw object
            text: Text to draw
            position: (x, y) tuple
            font: PIL font object
            fill: Text color
            align: Text alignment ("left", "center", "right")
            max_width: Maximum width in pixels, will truncate with "..." if exceeded
        """
        if fill is None:
            fill = self.COLOR_WHITE

        # Handle text truncation
        if max_width:
            text = self.truncate_text(text, font, max_width)

        # Handle alignment
        if align == "center":
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            position = (position[0] - text_width // 2, position[1])
        elif align == "right":
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            position = (position[0] - text_width, position[1])

        draw.text(position, text, font=font, fill=fill)

    def truncate_text(self, text: str, font, max_width: int) -> str:
        """
        Truncate text to fit within max_width, adding "..." if needed.

        Args:
            text: Text to truncate
            font: PIL font object
            max_width: Maximum width in pixels

        Returns:
            Truncated text
        """
        # Create a temporary draw to measure text
        temp_image = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_image)

        # Check if text fits
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            return text

        # Truncate with ellipsis
        ellipsis = "..."
        for i in range(len(text), 0, -1):
            truncated = text[:i] + ellipsis
            bbox = temp_draw.textbbox((0, 0), truncated, font=font)
            if bbox[2] - bbox[0] <= max_width:
                return truncated

        return ellipsis

    def draw_title_bar(self, draw: ImageDraw.ImageDraw, title: str, font=None):
        """
        Draw an optional title bar below action bar.

        Args:
            draw: ImageDraw object
            title: Title text
            font: Font for title
        """
        y_start = self.CONTENT_Y_START
        y_end = y_start + 24

        # Title bar background
        draw.rectangle(
            [(0, y_start), (self.DISPLAY_WIDTH, y_end)],
            fill=self.COLOR_DARK_GRAY
        )

        # Title text
        self.draw_text(
            draw,
            title,
            (self.DISPLAY_WIDTH // 2, y_start + 6),
            font=font,
            fill=self.COLOR_WHITE,
            align="center"
        )

    def draw_scrollbar(
        self,
        draw: ImageDraw.ImageDraw,
        total_items: int,
        visible_items: int,
        scroll_offset: int,
        x: int = 315,
        y_start: int = None,
        y_end: int = None
    ):
        """
        Draw a scrollbar indicator.

        Args:
            draw: ImageDraw object
            total_items: Total number of items in list
            visible_items: Number of items visible at once
            scroll_offset: Current scroll position
            x: X position of scrollbar
            y_start: Top Y position (default: below action bar)
            y_end: Bottom Y position (default: bottom of screen)
        """
        if total_items <= visible_items:
            return

        # Default positions account for action bar
        if y_start is None:
            y_start = self.CONTENT_Y_START + 5
        if y_end is None:
            y_end = self.DISPLAY_HEIGHT - 5

        scrollbar_height = y_end - y_start
        thumb_height = max(20, int(scrollbar_height * visible_items / total_items))
        thumb_y = y_start + int((scrollbar_height - thumb_height) * scroll_offset / (total_items - visible_items))

        # Draw scrollbar track
        draw.rectangle(
            [(x, y_start), (x + 3, y_end)],
            fill=self.COLOR_DARK_GRAY
        )

        # Draw scrollbar thumb
        draw.rectangle(
            [(x, thumb_y), (x + 3, thumb_y + thumb_height)],
            fill=self.COLOR_BLUE
        )

    def format_time(self, seconds: Optional[float]) -> str:
        """
        Format seconds as MM:SS.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        if seconds is None:
            return "0:00"

        seconds = int(seconds)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
