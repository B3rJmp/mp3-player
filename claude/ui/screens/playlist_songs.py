"""Playlist Songs Screen - Browse songs in a specific playlist"""
from claude.ui.base_screen import BaseScreen
from claude.ui.action_bar import ActionIcon
from PIL import ImageDraw
import logging

logger = logging.getLogger(__name__)


class PlaylistSongsScreen(BaseScreen):
    """Screen for browsing songs in a specific playlist"""

    def __init__(self, app, playlist_name: str):
        super().__init__(app)

        self.playlist_name = playlist_name

        # State
        self.songs = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 6

    def on_enter(self):
        """Called when screen becomes active"""
        super().on_enter()

        # Configure action bar: Back, Play, --, PlayAll
        self.configure_action_bar(
            icons=[ActionIcon.BACK, ActionIcon.PLAY, ActionIcon.NONE, ActionIcon.SONGS],
            colors=[self.COLOR_RED, self.COLOR_GREEN, self.COLOR_BLACK, self.COLOR_BLUE]
        )

        self.load_songs()

    def on_exit(self):
        """Called when screen is deactivated"""
        super().on_exit()

    def load_songs(self):
        """Load songs from playlist"""
        self.songs = self.mpd.get_playlist_songs(self.playlist_name)
        logger.info(f"Loaded {len(self.songs)} songs from playlist '{self.playlist_name}'")
        self.request_render()

    def render_content(self, draw: ImageDraw.ImageDraw):
        """Render playlist songs list"""
        # Background
        draw.rectangle(
            [(0, self.CONTENT_Y_START), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
            fill=self.COLOR_BLACK
        )

        # Title bar
        self.draw_title_bar(draw, self.playlist_name)

        if not self.songs:
            self.draw_text(
                draw,
                "No songs in playlist",
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

        for i in range(self.scroll_offset, min(self.scroll_offset + self.items_per_page, len(self.songs))):
            song = self.songs[i]
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

            # Build song display text
            title = song.get('title', song.get('file', 'Unknown'))
            artist = song.get('artist', '')

            if artist:
                display_text = f"{title} - {artist}"
            else:
                display_text = title

            # Draw song
            self.draw_text(
                draw,
                display_text,
                (10, y_pos),
                fill=text_color,
                max_width=290
            )

        # Draw scrollbar
        if len(self.songs) > self.items_per_page:
            self.draw_scrollbar(
                draw,
                total_items=len(self.songs),
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
            # Play button - clear queue, add song, and play
            if self.songs and 0 <= self.selected_index < len(self.songs):
                song = self.songs[self.selected_index]
                if 'file' in song:
                    self.mpd.clear_queue()
                    self.mpd.add_to_queue(song['file'])
                    self.mpd.play(0)

                    logger.info(f"Playing song: {song.get('title', song['file'])}")

                    # Push now playing on top
                    from claude.ui.screens.now_playing import NowPlayingScreen
                    self.app.screen_stack.push(NowPlayingScreen(self.app))

        elif button_index == 3:
            # Play All button - load entire playlist and play
            self.mpd.clear_queue()
            self.mpd.load_playlist(self.playlist_name)
            self.mpd.play(0)

            logger.info(f"Playing entire playlist: {self.playlist_name}")

            # Push now playing on top
            from claude.ui.screens.now_playing import NowPlayingScreen
            self.app.screen_stack.push(NowPlayingScreen(self.app))

    def handle_encoder_rotate(self, delta: int):
        """Handle encoder rotation for list navigation"""
        if not self.songs:
            return

        # Update selection
        self.selected_index += delta

        # Wrap around
        if self.selected_index < 0:
            self.selected_index = len(self.songs) - 1
        elif self.selected_index >= len(self.songs):
            self.selected_index = 0

        self.request_render()

    def handle_encoder_press(self):
        """Handle encoder press to play selected song"""
        if self.songs and 0 <= self.selected_index < len(self.songs):
            song = self.songs[self.selected_index]
            if 'file' in song:
                self.mpd.clear_queue()
                self.mpd.add_to_queue(song['file'])
                self.mpd.play(0)

                logger.info(f"Playing song: {song.get('title', song['file'])}")

                # Push now playing on top
                from claude.ui.screens.now_playing import NowPlayingScreen
                self.app.screen_stack.push(NowPlayingScreen(self.app))
