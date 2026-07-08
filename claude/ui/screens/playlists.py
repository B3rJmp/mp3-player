"""Playlists Screen - Browse and select playlists"""
from claude.ui.base_screen import BaseScreen
from claude.ui.action_bar import ActionIcon
from PIL import ImageDraw
import logging

logger = logging.getLogger(__name__)


class PlaylistsScreen(BaseScreen):
    """Screen for browsing saved playlists"""

    def __init__(self, app):
        super().__init__(app)

        # State
        self.playlists = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 6

    def on_enter(self):
        """Called when screen becomes active"""
        super().on_enter()

        # Configure action bar: Back, Play, Queue, Songs
        self.configure_action_bar(
            icons=[ActionIcon.BACK, ActionIcon.PLAY, ActionIcon.QUEUE, ActionIcon.SONGS],
            colors=[self.COLOR_RED, self.COLOR_GREEN, self.COLOR_YELLOW, self.COLOR_CYAN]
        )

        self.load_playlists()

    def on_exit(self):
        """Called when screen is deactivated"""
        super().on_exit()

    def load_playlists(self):
        """Load playlists from MPD"""
        playlists_raw = self.mpd.get_playlists()
        # Extract playlist names
        self.playlists = [p.get('playlist', '') for p in playlists_raw if 'playlist' in p]
        self.playlists.sort()

        logger.info(f"Loaded {len(self.playlists)} playlists")
        self.request_render()

    def render_content(self, draw: ImageDraw.ImageDraw):
        """Render playlists list"""
        # Background
        draw.rectangle(
            [(0, self.CONTENT_Y_START), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
            fill=self.COLOR_BLACK
        )

        # Title bar
        self.draw_title_bar(draw, f"Playlists ({len(self.playlists)})")

        if not self.playlists:
            self.draw_text(
                draw,
                "No playlists found",
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

        for i in range(self.scroll_offset, min(self.scroll_offset + self.items_per_page, len(self.playlists))):
            playlist = self.playlists[i]
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

            # Draw playlist name
            self.draw_text(
                draw,
                playlist,
                (10, y_pos),
                fill=text_color,
                max_width=290
            )

        # Draw scrollbar
        if len(self.playlists) > self.items_per_page:
            self.draw_scrollbar(
                draw,
                total_items=len(self.playlists),
                visible_items=self.items_per_page,
                scroll_offset=self.scroll_offset,
                y_start=y_start,
                y_end=y_start + self.items_per_page * item_height
            )

    def handle_button(self, button_index: int):
        """Handle button press"""
        if button_index == 0:
            # Back button
            self.app.screen_stack.pop()

        elif button_index == 1:
            # Play button - clear queue, load playlist, and play
            if self.playlists and 0 <= self.selected_index < len(self.playlists):
                playlist_name = self.playlists[self.selected_index]

                self.mpd.clear_queue()
                self.mpd.load_playlist(playlist_name)
                self.mpd.play(0)

                logger.info(f"Playing playlist: {playlist_name}")

                # Push now playing on top
                from claude.ui.screens.now_playing import NowPlayingScreen
                self.app.screen_stack.push(NowPlayingScreen(self.app))

        elif button_index == 2:
            # Queue button - add playlist to queue
            if self.playlists and 0 <= self.selected_index < len(self.playlists):
                playlist_name = self.playlists[self.selected_index]
                self.mpd.load_playlist(playlist_name)

                logger.info(f"Added playlist to queue: {playlist_name}")

        elif button_index == 3:
            # Songs button - show songs in playlist
            if self.playlists and 0 <= self.selected_index < len(self.playlists):
                from claude.ui.screens.playlist_songs import PlaylistSongsScreen
                playlist_name = self.playlists[self.selected_index]
                self.app.screen_stack.push(PlaylistSongsScreen(self.app, playlist_name))

    def handle_encoder_rotate(self, delta: int):
        """Handle encoder rotation for list navigation"""
        if not self.playlists:
            return

        # Update selection
        self.selected_index += delta

        # Wrap around
        if self.selected_index < 0:
            self.selected_index = len(self.playlists) - 1
        elif self.selected_index >= len(self.playlists):
            self.selected_index = 0

        self.request_render()

    def handle_encoder_press(self):
        """Handle encoder press to view playlist songs"""
        if self.playlists and 0 <= self.selected_index < len(self.playlists):
            from claude.ui.screens.playlist_songs import PlaylistSongsScreen
            playlist_name = self.playlists[self.selected_index]
            self.app.screen_stack.push(PlaylistSongsScreen(self.app, playlist_name))
