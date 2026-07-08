"""Albums Screen - Browse and select albums"""
from claude.ui.base_screen import BaseScreen
from claude.ui.action_bar import ActionIcon
from PIL import ImageDraw
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AlbumsScreen(BaseScreen):
    """Screen for browsing albums, optionally filtered by artist"""

    def __init__(self, app, artist: Optional[str] = None):
        super().__init__(app)

        self.artist = artist

        # State
        self.albums = []
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

        self.load_albums()

    def on_exit(self):
        """Called when screen is deactivated"""
        super().on_exit()

    def load_albums(self):
        """Load album list from MPD"""
        self.albums = self.mpd.get_albums(artist=self.artist)
        self.albums.sort()
        logger.info(f"Loaded {len(self.albums)} albums" + (f" for artist '{self.artist}'" if self.artist else ""))
        self.request_render()

    def render_content(self, draw: ImageDraw.ImageDraw):
        """Render albums list"""
        # Background
        draw.rectangle(
            [(0, self.CONTENT_Y_START), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
            fill=self.COLOR_BLACK
        )

        # Title bar
        if self.artist:
            title = f"{self.artist} - Albums"
        else:
            title = f"All Albums ({len(self.albums)})"

        self.draw_title_bar(draw, title)

        if not self.albums:
            self.draw_text(
                draw,
                "No albums found",
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

        for i in range(self.scroll_offset, min(self.scroll_offset + self.items_per_page, len(self.albums))):
            album = self.albums[i]
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

            # Draw album name
            self.draw_text(
                draw,
                album,
                (10, y_pos),
                fill=text_color,
                max_width=290
            )

        # Draw scrollbar
        if len(self.albums) > self.items_per_page:
            self.draw_scrollbar(
                draw,
                total_items=len(self.albums),
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
            # Play button - clear queue, add album, and play
            if self.albums and 0 <= self.selected_index < len(self.albums):
                selected_album = self.albums[self.selected_index]
                songs = self.mpd.get_songs(artist=self.artist, album=selected_album)

                self.mpd.clear_queue()
                for song in songs:
                    if 'file' in song:
                        self.mpd.add_to_queue(song['file'])

                self.mpd.play(0)
                logger.info(f"Playing album: {selected_album}")

                # Push now playing on top (new behavior)
                from claude.ui.screens.now_playing import NowPlayingScreen
                self.app.screen_stack.push(NowPlayingScreen(self.app))

        elif button_index == 2:
            # Queue button - add album to queue
            if self.albums and 0 <= self.selected_index < len(self.albums):
                selected_album = self.albums[self.selected_index]
                songs = self.mpd.get_songs(artist=self.artist, album=selected_album)

                for song in songs:
                    if 'file' in song:
                        self.mpd.add_to_queue(song['file'])

                logger.info(f"Added album to queue: {selected_album}")

        elif button_index == 3:
            # Songs button - show songs filtered by this artist+album
            if self.albums and 0 <= self.selected_index < len(self.albums):
                from claude.ui.screens.songs import SongsScreen
                selected_album = self.albums[self.selected_index]
                self.app.screen_stack.push(
                    SongsScreen(self.app, artist=self.artist, album=selected_album)
                )

    def handle_encoder_rotate(self, delta: int):
        """Handle encoder rotation for list navigation"""
        if not self.albums:
            return

        # Update selection
        self.selected_index += delta

        # Wrap around
        if self.selected_index < 0:
            self.selected_index = len(self.albums) - 1
        elif self.selected_index >= len(self.albums):
            self.selected_index = 0

        self.request_render()

    def handle_encoder_press(self):
        """Handle encoder press to show songs in album"""
        if self.albums and 0 <= self.selected_index < len(self.albums):
            from claude.ui.screens.songs import SongsScreen
            selected_album = self.albums[self.selected_index]
            # Show songs filtered by this artist + album
            self.app.screen_stack.push(
                SongsScreen(self.app, artist=self.artist, album=selected_album)
            )
