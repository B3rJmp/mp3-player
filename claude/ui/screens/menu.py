"""Menu Screen - Main navigation menu"""
from claude.ui.base_screen import BaseScreen
from claude.ui.action_bar import ActionIcon
from PIL import ImageDraw
import logging

logger = logging.getLogger(__name__)


class MenuScreen(BaseScreen):
    """Main menu screen for navigating to different sections"""

    def __init__(self, app):
        super().__init__(app)

        # Menu options
        self.menu_items = [
            ("Artists", ActionIcon.ARTISTS, self._open_artists),
            ("Albums", ActionIcon.ALBUMS, self._open_albums),
            ("Songs", ActionIcon.SONGS, self._open_songs),
            ("Playlists", ActionIcon.PLAYLISTS, self._open_playlists),
            ("Bluetooth", ActionIcon.BLUETOOTH, self._open_bluetooth),
        ]

        # State
        self.selected_index = 0

    def on_enter(self):
        """Called when screen becomes active"""
        super().on_enter()

        # Configure action bar: Back, --, --, Select
        self.configure_action_bar(
            icons=[ActionIcon.BACK, ActionIcon.NONE, ActionIcon.NONE, ActionIcon.MENU],
            colors=[self.COLOR_RED, self.COLOR_BLACK, self.COLOR_BLACK, self.COLOR_GREEN]
        )

    def on_exit(self):
        """Called when screen is deactivated"""
        super().on_exit()

    def render_content(self, draw: ImageDraw.ImageDraw):
        """Render menu content"""
        # Background
        draw.rectangle(
            [(0, self.CONTENT_Y_START), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
            fill=self.COLOR_BLACK
        )

        # Title
        self.draw_title_bar(draw, "Menu")

        # Menu items
        y_start = self.CONTENT_Y_START + 35
        item_height = 35

        for i, (label, icon, _) in enumerate(self.menu_items):
            y_pos = y_start + (i * item_height)

            # Selection highlight
            if i == self.selected_index:
                draw.rectangle(
                    [(10, y_pos - 3), (self.DISPLAY_WIDTH - 10, y_pos + item_height - 8)],
                    fill=self.COLOR_BLUE
                )
                text_color = self.COLOR_BLACK
            else:
                text_color = self.COLOR_WHITE

            # Draw menu item
            self.draw_text(
                draw,
                label,
                (20, y_pos + 4),
                fill=text_color
            )

    def handle_button(self, button_index: int):
        """Handle button press"""
        if button_index == 0:
            # Back button - return to now playing
            self.app.screen_stack.pop()

        elif button_index == 3:
            # Select/Enter button
            self._select_current_item()

    def handle_encoder_rotate(self, delta: int):
        """Handle encoder rotation for menu navigation"""
        # Update selection
        self.selected_index += delta

        # Wrap around
        if self.selected_index < 0:
            self.selected_index = len(self.menu_items) - 1
        elif self.selected_index >= len(self.menu_items):
            self.selected_index = 0

        self.request_render()

    def handle_encoder_press(self):
        """Handle encoder press to select menu item"""
        self._select_current_item()

    def _select_current_item(self):
        """Execute selected menu item action"""
        if 0 <= self.selected_index < len(self.menu_items):
            _, _, action = self.menu_items[self.selected_index]
            action()

    def _open_artists(self):
        """Open artists screen"""
        from claude.ui.screens.artists import ArtistsScreen
        self.app.screen_stack.push(ArtistsScreen(self.app))

    def _open_albums(self):
        """Open albums screen"""
        from claude.ui.screens.albums import AlbumsScreen
        self.app.screen_stack.push(AlbumsScreen(self.app))

    def _open_songs(self):
        """Open songs screen"""
        from claude.ui.screens.songs import SongsScreen
        self.app.screen_stack.push(SongsScreen(self.app))

    def _open_playlists(self):
        """Open playlists screen"""
        from claude.ui.screens.playlists import PlaylistsScreen
        self.app.screen_stack.push(PlaylistsScreen(self.app))

    def _open_bluetooth(self):
        """Open bluetooth screen"""
        from claude.ui.screens.bluetooth import BluetoothScreen
        self.app.screen_stack.push(BluetoothScreen(self.app))
