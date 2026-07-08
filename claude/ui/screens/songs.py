"""Songs Screen - Browse and select songs"""
from claude.ui.base_screen import BaseScreen
from claude.ui.action_bar import ActionIcon
from PIL import ImageDraw
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SongsScreen(BaseScreen):
    """Screen for browsing songs, optionally filtered by artist and/or album"""

    def __init__(self, app, artist: Optional[str] = None, album: Optional[str] = None):
        super().__init__(app)

        self.artist = artist
        self.album = album

        # State
        self.songs = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 6

    def on_enter(self):
        """Called when screen becomes active"""
        super().on_enter()

        # Configure action bar: Back, Play, Queue, PlayAll
        self.configure_action_bar(
            icons=[ActionIcon.BACK, ActionIcon.PLAY, ActionIcon.QUEUE, ActionIcon.SONGS],
            colors=[self.COLOR_RED, self.COLOR_GREEN, self.COLOR_YELLOW, self.COLOR_BLUE]
        )

        self.load_songs()

    def on_exit(self):
        """Called when screen is deactivated"""
        super().on_exit()

    def load_songs(self):
        """Load song list from MPD"""
        self.songs = self.mpd.get_songs(artist=self.artist, album=self.album)

        # Sort by track number if available, otherwise by title
        def sort_key(song):
            track = song.get('track', '999')
            # Extract numeric part from track (could be "1/12" format)
            try:
                track_num = int(track.split('/')[0])
            except (ValueError, AttributeError):
                track_num = 999
            return (track_num, song.get('title', ''))

        self.songs.sort(key=sort_key)

        logger.info(f"Loaded {len(self.songs)} songs")
        self.request_render()

    def render_content(self, draw: ImageDraw.ImageDraw):
        """Render songs list"""
        # Background
        draw.rectangle(
            [(0, self.CONTENT_Y_START), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
            fill=self.COLOR_BLACK
        )

        # Title bar
        header_parts = []
        if self.artist:
            header_parts.append(self.artist)
        if self.album:
            header_parts.append(self.album)

        if header_parts:
            title = " - ".join(header_parts)
        else:
            title = f"All Songs ({len(self.songs)})"

        self.draw_title_bar(draw, title)

        if not self.songs:
            self.draw_text(
                draw,
                "No songs found",
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
            track = song.get('track', '')
            title = song.get('title', song.get('file', 'Unknown'))

            # Format: "01. Song Title" or just "Song Title"
            if track:
                try:
                    track_num = int(track.split('/')[0])
                    display_text = f"{track_num:02d}. {title}"
                except (ValueError, AttributeError):
                    display_text = title
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

        elif button_index == 2:
            # Queue button - add song to queue
            if self.songs and 0 <= self.selected_index < len(self.songs):
                song = self.songs[self.selected_index]
                if 'file' in song:
                    self.mpd.add_to_queue(song['file'])
                    logger.info(f"Added to queue: {song.get('title', song['file'])}")

        elif button_index == 3:
            # Play All button - clear queue, add all songs, and play
            if self.songs:
                self.mpd.clear_queue()
                for song in self.songs:
                    if 'file' in song:
                        self.mpd.add_to_queue(song['file'])

                self.mpd.play(0)
                logger.info(f"Playing all {len(self.songs)} songs")

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
