"""Now Playing Screen - Shows current song and playback controls"""
from claude.ui.base_screen import BaseScreen
from claude.ui.action_bar import ActionIcon
from PIL import ImageDraw
import logging

logger = logging.getLogger(__name__)


class NowPlayingScreen(BaseScreen):
    """Screen displaying current song and playback controls"""

    def __init__(self, app):
        super().__init__(app)

        # State
        self.status = None
        self.current_song = None

    def on_enter(self):
        """Called when screen becomes active"""
        super().on_enter()
        self.update_playback_state()

    def on_exit(self):
        """Called when screen is deactivated"""
        super().on_exit()

    def update_playback_state(self):
        """Fetch current playback state from MPD and update action bar"""
        self.status = self.mpd.get_status()
        self.current_song = self.mpd.get_current_song()

        # Determine play/pause icon based on state
        play_pause_icon = ActionIcon.PLAY
        play_pause_color = self.COLOR_BLUE

        if self.status:
            state = self.status.get('state', 'stop')
            if state == 'play':
                play_pause_icon = ActionIcon.PAUSE
                play_pause_color = self.COLOR_GREEN
            elif state == 'pause':
                play_pause_icon = ActionIcon.PLAY
                play_pause_color = self.COLOR_BLUE

        # Configure action bar: Previous, Play/Pause, Stop, Next
        self.configure_action_bar(
            icons=[ActionIcon.PREVIOUS, play_pause_icon, ActionIcon.STOP, ActionIcon.NEXT],
            colors=[self.COLOR_YELLOW, play_pause_color, self.COLOR_RED, self.COLOR_YELLOW]
        )

        self.request_render()

    def render_content(self, draw: ImageDraw.ImageDraw):
        """Render now playing screen content"""
        # Background
        draw.rectangle(
            [(0, self.CONTENT_Y_START), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
            fill=self.COLOR_BLACK
        )

        if not self.current_song:
            # No song playing
            self.draw_text(
                draw,
                "No song playing",
                (self.DISPLAY_WIDTH // 2, 120),
                fill=self.COLOR_GRAY,
                align="center"
            )
            return

        # Song info
        y_offset = self.CONTENT_Y_START + 20

        # Artist
        artist = self.current_song.get('artist', 'Unknown Artist')
        self.draw_text(
            draw,
            artist,
            (10, y_offset),
            fill=self.COLOR_CYAN,
            max_width=self.DISPLAY_WIDTH - 20
        )
        y_offset += 30

        # Album
        album = self.current_song.get('album', 'Unknown Album')
        self.draw_text(
            draw,
            album,
            (10, y_offset),
            fill=self.COLOR_GRAY,
            max_width=self.DISPLAY_WIDTH - 20
        )
        y_offset += 25

        # Title (larger, brighter)
        title = self.current_song.get('title', 'Unknown Title')
        self.draw_text(
            draw,
            title,
            (10, y_offset),
            fill=self.COLOR_WHITE,
            max_width=self.DISPLAY_WIDTH - 20
        )
        y_offset += 40

        # Progress bar
        if self.status:
            elapsed = float(self.status.get('elapsed', 0))
            duration = float(self.status.get('duration', 0))

            if duration > 0:
                # Time labels
                elapsed_str = self.format_time(elapsed)
                duration_str = self.format_time(duration)

                self.draw_text(draw, elapsed_str, (10, y_offset), fill=self.COLOR_WHITE)
                self.draw_text(
                    draw,
                    duration_str,
                    (self.DISPLAY_WIDTH - 10, y_offset),
                    fill=self.COLOR_WHITE,
                    align="right"
                )

                # Progress bar
                bar_y = y_offset + 25
                bar_width = self.DISPLAY_WIDTH - 20
                progress = elapsed / duration

                # Background bar
                draw.rectangle(
                    [(10, bar_y), (10 + bar_width, bar_y + 10)],
                    fill=self.COLOR_DARK_GRAY
                )

                # Progress fill
                fill_width = int(bar_width * progress)
                draw.rectangle(
                    [(10, bar_y), (10 + fill_width, bar_y + 10)],
                    fill=self.COLOR_BLUE
                )

                y_offset += 45

        # Playback state indicators
        if self.status:
            indicators = []

            # Repeat
            repeat_mode = self.status.get('repeat', '0')
            single_mode = self.status.get('single', '0')
            if single_mode == '1':
                indicators.append("Single")
            elif repeat_mode == '1':
                indicators.append("Repeat")

            # Random/Shuffle
            if self.status.get('random', '0') == '1':
                indicators.append("Shuffle")

            # Volume
            volume = self.status.get('volume', '50')
            indicators.append(f"Vol: {volume}%")

            if indicators:
                indicator_text = " | ".join(indicators)
                self.draw_text(
                    draw,
                    indicator_text,
                    (self.DISPLAY_WIDTH // 2, self.DISPLAY_HEIGHT - 15),
                    fill=self.COLOR_GRAY,
                    align="center"
                )

    def handle_button(self, button_index: int):
        """Handle button press"""
        if button_index == 0:
            # Previous track
            self.mpd.previous()
            self.update_playback_state()

        elif button_index == 1:
            # Play/Pause toggle
            if self.status:
                state = self.status.get('state', 'stop')
                if state == 'play':
                    self.mpd.pause()
                else:
                    self.mpd.play()
            else:
                self.mpd.play()
            self.update_playback_state()

        elif button_index == 2:
            # Stop
            self.mpd.stop()
            self.update_playback_state()

        elif button_index == 3:
            # Next track
            self.mpd.next()
            self.update_playback_state()

    def handle_encoder_rotate(self, delta: int):
        """Handle encoder rotation for volume control"""
        if delta > 0:
            self.mpd.volume_up(amount=2)
        else:
            self.mpd.volume_down(amount=2)
        self.update_playback_state()

    def handle_encoder_press(self):
        """Handle encoder press to open menu"""
        from claude.ui.screens.menu import MenuScreen
        self.app.screen_stack.push(MenuScreen(self.app))
