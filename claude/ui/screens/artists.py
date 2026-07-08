"""Artists Screen - Browse and select artists"""
from claude.ui.base_screen import BaseScreen
from claude.ui.action_bar import ActionIcon
from PIL import ImageDraw
import logging

logger = logging.getLogger(__name__)


class ArtistsScreen(BaseScreen):
    """Screen for browsing artists"""

    def __init__(self, app):
        super().__init__(app)

        # State
        self.artists = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 6  # Reduced for action bar space

    def on_enter(self):
        """Called when screen becomes active"""
        super().on_enter()

        # Configure action bar: Back, Albums (all), Songs (all), Playlists
        self.configure_action_bar(
            icons=[ActionIcon.BACK, ActionIcon.ALBUMS, ActionIcon.SONGS, ActionIcon.PLAYLISTS],
            colors=[self.COLOR_RED, self.COLOR_YELLOW, self.COLOR_GREEN, self.COLOR_CYAN]
        )

        self.load_artists()

    def on_exit(self):
        """Called when screen is deactivated"""
        super().on_exit()

    def load_artists(self):
        """Load artist list from MPD"""
        self.artists = self.mpd.get_artists()
        self.artists.sort()
        logger.info(f"Loaded {len(self.artists)} artists")
        self.request_render()

    def render_content(self, draw: ImageDraw.ImageDraw):
        """Render artists list"""
        # Background
        draw.rectangle(
            [(0, self.CONTENT_Y_START), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
            fill=self.COLOR_BLACK
        )

        # Title bar
        self.draw_title_bar(draw, f"Artists ({len(self.artists)})")

        if not self.artists:
            self.draw_text(
                draw,
                "No artists found",
                (self.DISPLAY_WIDTH // 2, 120),
                fill=self.COLOR_GRAY,
                align="center"
            )
            return

        # Calculate visible range
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.items_per_page:
            self.scroll_offset = self.selected_index - self.items_per_page + 1

        # Draw list items
        y_start = self.CONTENT_Y_START + 30
        item_height = 28

        for i in range(self.scroll_offset, min(self.scroll_offset + self.items_per_page, len(self.artists))):
            artist = self.artists[i]
            y_pos = y_start + (i - self.scroll_offset) * item_height

            # Highlight selected item
            if i == self.selected_index:
                draw.rectangle(
                    [(5, y_pos - 2), (305, y_pos + item_height - 5)],
                    fill=self.COLOR_BLUE
                )
                text_color = self.COLOR_BLACK
            else:
                text_color = self.COLOR_WHITE

            # Draw artist name
            self.draw_text(
                draw,
                artist,
                (10, y_pos),
                fill=text_color,
                max_width=290
            )

        # Draw scrollbar
        if len(self.artists) > self.items_per_page:
            self.draw_scrollbar(
                draw,
                total_items=len(self.artists),
                visible_items=self.items_per_page,
                scroll_offset=self.scroll_offset,
                y_start=y_start,
                y_end=y_start + self.items_per_page * item_height
            )

    def handle_button(self, button_index: int):
        """Handle button press"""
        if button_index == 0:
            # Back button - return to previous screen
            self.app.screen_stack.pop()

        elif button_index == 1:
            # Albums button - show ALL albums (no artist filter)
            from claude.ui.screens.albums import AlbumsScreen
            self.app.screen_stack.push(AlbumsScreen(self.app))

        elif button_index == 2:
            # Songs button - show ALL songs (no artist filter)
            from claude.ui.screens.songs import SongsScreen
            self.app.screen_stack.push(SongsScreen(self.app))

        elif button_index == 3:
            # Playlists button
            from claude.ui.screens.playlists import PlaylistsScreen
            self.app.screen_stack.push(PlaylistsScreen(self.app))

    def handle_encoder_rotate(self, delta: int):
        """Handle encoder rotation for list navigation"""
        if not self.artists:
            return

        # Update selection
        self.selected_index += delta

        # Wrap around
        if self.selected_index < 0:
            self.selected_index = len(self.artists) - 1
        elif self.selected_index >= len(self.artists):
            self.selected_index = 0

        self.request_render()

    def handle_encoder_press(self):
        """Handle encoder press to select artist (show albums filtered by this artist)"""
        if self.artists and 0 <= self.selected_index < len(self.artists):
            from claude.ui.screens.albums import AlbumsScreen
            selected_artist = self.artists[self.selected_index]
            # Pass artist filter to show only this artist's albums
            self.app.screen_stack.push(AlbumsScreen(self.app, artist=selected_artist))
