"""Action Bar - Permanent top bar showing button functions with icons"""
from PIL import Image, ImageDraw
from typing import Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ActionIcon(Enum):
    """Available action icons"""
    NONE = "none"
    BACK = "back"
    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    STOP = "stop"
    NEXT = "next"
    PREVIOUS = "previous"
    ALBUMS = "albums"
    SONGS = "songs"
    PLAYLISTS = "playlists"
    ARTISTS = "artists"
    BLUETOOTH = "bluetooth"
    QUEUE = "queue"
    SHUFFLE = "shuffle"
    REPEAT = "repeat"


class ActionBar:
    """
    Permanent action bar showing button functions with icons.
    Always displayed at the top of the screen.
    """

    # Dimensions
    HEIGHT = 36
    SLOT_WIDTH = 80  # 320 / 4 = 80 pixels per button
    ICON_SIZE = 24
    PADDING = 4

    # Colors
    COLOR_BACKGROUND = (20, 20, 20)
    COLOR_DIVIDER = (60, 60, 60)
    COLOR_ICON = (255, 255, 255)

    def __init__(self, width: int = 320):
        self.width = width
        self.slot_width = width // 4

        # Current configuration
        self.icons = [ActionIcon.NONE] * 4
        self.colors = [(0, 0, 0)] * 4
        self.enabled = [True] * 4

    def configure(
        self,
        icons: list[ActionIcon],
        colors: list[Tuple[int, int, int]],
        enabled: Optional[list[bool]] = None
    ):
        """
        Configure action bar buttons.

        Args:
            icons: List of 4 ActionIcon enums
            colors: List of 4 RGB color tuples
            enabled: List of 4 booleans (optional, defaults to all True)
        """
        if len(icons) != 4 or len(colors) != 4:
            logger.error("Action bar requires exactly 4 icons and 4 colors")
            return

        self.icons = icons
        self.colors = colors
        self.enabled = enabled if enabled else [True] * 4

    def render(self, draw: ImageDraw.ImageDraw):
        """Render action bar to image"""
        # Background
        draw.rectangle(
            [(0, 0), (self.width, self.HEIGHT)],
            fill=self.COLOR_BACKGROUND
        )

        # Draw each button slot
        for i in range(4):
            x_start = i * self.slot_width
            x_center = x_start + self.slot_width // 2
            y_center = self.HEIGHT // 2

            # Color indicator bar at bottom of slot
            if self.colors[i] != (0, 0, 0):
                draw.rectangle(
                    [(x_start + 2, self.HEIGHT - 3), (x_start + self.slot_width - 2, self.HEIGHT - 1)],
                    fill=self.colors[i]
                )

            # Draw icon
            if self.icons[i] != ActionIcon.NONE:
                icon_color = self.COLOR_ICON if self.enabled[i] else (80, 80, 80)
                self._draw_icon(
                    draw,
                    self.icons[i],
                    x_center,
                    y_center,
                    icon_color
                )

            # Divider between slots (except after last)
            if i < 3:
                draw.line(
                    [(x_start + self.slot_width, 4), (x_start + self.slot_width, self.HEIGHT - 4)],
                    fill=self.COLOR_DIVIDER,
                    width=1
                )

    def _draw_icon(
        self,
        draw: ImageDraw.ImageDraw,
        icon: ActionIcon,
        x: int,
        y: int,
        color: Tuple[int, int, int]
    ):
        """Draw a specific icon centered at (x, y)"""
        size = self.ICON_SIZE

        if icon == ActionIcon.BACK:
            # Left arrow
            points = [
                (x + 6, y),
                (x - 6, y),
                (x - 2, y - 6),
                (x - 6, y),
                (x - 2, y + 6)
            ]
            draw.line(points[:2], fill=color, width=2)
            draw.line(points[2:4], fill=color, width=2)
            draw.line(points[4:] + [points[1]], fill=color, width=2)

        elif icon == ActionIcon.MENU:
            # Hamburger menu (3 lines)
            for i in range(3):
                y_pos = y - 6 + (i * 6)
                draw.line([(x - 8, y_pos), (x + 8, y_pos)], fill=color, width=2)

        elif icon == ActionIcon.PLAY:
            # Right-pointing triangle
            points = [
                (x - 5, y - 8),
                (x + 8, y),
                (x - 5, y + 8)
            ]
            draw.polygon(points, fill=color)

        elif icon == ActionIcon.PAUSE:
            # Two vertical bars
            draw.rectangle([(x - 6, y - 7), (x - 2, y + 7)], fill=color)
            draw.rectangle([(x + 2, y - 7), (x + 6, y + 7)], fill=color)

        elif icon == ActionIcon.STOP:
            # Square
            draw.rectangle([(x - 6, y - 6), (x + 6, y + 6)], fill=color)

        elif icon == ActionIcon.NEXT:
            # Skip forward (triangle + bar)
            points = [
                (x - 6, y - 7),
                (x + 4, y),
                (x - 6, y + 7)
            ]
            draw.polygon(points, fill=color)
            draw.rectangle([(x + 5, y - 7), (x + 7, y + 7)], fill=color)

        elif icon == ActionIcon.PREVIOUS:
            # Skip backward (bar + triangle)
            points = [
                (x + 6, y - 7),
                (x - 4, y),
                (x + 6, y + 7)
            ]
            draw.polygon(points, fill=color)
            draw.rectangle([(x - 7, y - 7), (x - 5, y + 7)], fill=color)

        elif icon == ActionIcon.ALBUMS:
            # Stacked rectangles (album stack)
            draw.rectangle([(x - 7, y - 5), (x + 7, y + 1)], outline=color, width=2)
            draw.rectangle([(x - 7, y + 2), (x + 7, y + 8)], outline=color, width=2)

        elif icon == ActionIcon.SONGS:
            # Musical note
            draw.ellipse([(x - 5, y + 2), (x - 1, y + 6)], fill=color)
            draw.rectangle([(x - 1, y - 6), (x + 1, y + 4)], fill=color)
            draw.rectangle([(x + 1, y - 6), (x + 6, y - 4)], fill=color)

        elif icon == ActionIcon.PLAYLISTS:
            # List with play icon
            for i in range(3):
                y_pos = y - 5 + (i * 5)
                draw.line([(x - 2, y_pos), (x + 7, y_pos)], fill=color, width=2)
            # Small play triangle
            points = [(x - 8, y - 4), (x - 4, y), (x - 8, y + 4)]
            draw.polygon(points, fill=color)

        elif icon == ActionIcon.ARTISTS:
            # Person icon
            draw.ellipse([(x - 3, y - 7), (x + 3, y - 1)], outline=color, width=2)
            draw.arc([(x - 6, y), (x + 6, y + 10)], 0, 180, fill=color, width=2)

        elif icon == ActionIcon.BLUETOOTH:
            # Bluetooth symbol
            points_top = [(x, y - 8), (x + 6, y - 2), (x, y + 4)]
            points_bottom = [(x, y - 4), (x + 6, y + 2), (x, y + 8)]
            draw.line([(x, y - 8), (x, y + 8)], fill=color, width=2)
            draw.line(points_top, fill=color, width=2)
            draw.line(points_bottom, fill=color, width=2)

        elif icon == ActionIcon.QUEUE:
            # List icon
            for i in range(4):
                y_pos = y - 6 + (i * 4)
                draw.line([(x - 7, y_pos), (x + 7, y_pos)], fill=color, width=2)

        elif icon == ActionIcon.SHUFFLE:
            # Crossed arrows
            draw.line([(x - 6, y - 4), (x + 6, y + 4)], fill=color, width=2)
            draw.line([(x - 6, y + 4), (x + 6, y - 4)], fill=color, width=2)
            # Arrow heads
            draw.line([(x + 6, y + 4), (x + 3, y + 2)], fill=color, width=2)
            draw.line([(x + 6, y + 4), (x + 4, y + 7)], fill=color, width=2)

        elif icon == ActionIcon.REPEAT:
            # Circular arrow
            draw.arc([(x - 6, y - 6), (x + 6, y + 6)], 45, 315, fill=color, width=2)
            # Arrow head
            draw.line([(x + 5, y - 4), (x + 7, y - 1)], fill=color, width=2)
            draw.line([(x + 5, y - 4), (x + 2, y - 2)], fill=color, width=2)
