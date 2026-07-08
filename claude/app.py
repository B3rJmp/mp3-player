"""Main Application - MP3 Player Interface Controller"""
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7789
from PIL import Image, ImageDraw
import time
import logging

from claude.services.mpd_service import MPDService
from claude.services.bluetooth_service import BluetoothService
from claude.core.input_manager import InputManager, InputEvent, InputType
from claude.core.screen_stack import ScreenStack
from claude.ui.screens.now_playing import NowPlayingScreen

logger = logging.getLogger(__name__)


class MP3PlayerApp:
    """Main application controller for MP3 player interface"""

    # Display configuration
    DISPLAY_WIDTH = 320
    DISPLAY_HEIGHT = 240
    SPI_PORT = 0
    SPI_DEVICE = 0
    SPI_BUS_SPEED = 40000000  # 40 MHz
    DC_PIN = 25
    RST_PIN = 24

    # Timing
    RENDER_FPS = 15
    INPUT_POLL_RATE = 60  # Hz

    def __init__(self, mpd_host: str = "localhost", mpd_port: int = 6600):
        """
        Initialize MP3 Player application.

        Args:
            mpd_host: MPD server host
            mpd_port: MPD server port
        """
        self.running = False

        # Initialize display
        logger.info("Initializing display...")
        serial = spi(
            port=self.SPI_PORT,
            device=self.SPI_DEVICE,
            bus_speed_hz=self.SPI_BUS_SPEED,
            dc_pin=self.DC_PIN,
            rst_pin=self.RST_PIN
        )
        self.device = st7789(
            serial,
            width=self.DISPLAY_WIDTH,
            height=self.DISPLAY_HEIGHT,
            rotate=0
        )
        logger.info("Display initialized")

        # Initialize MPD service
        logger.info("Initializing MPD service...")
        self.mpd_service = MPDService(host=mpd_host, port=mpd_port)
        if not self.mpd_service.connect():
            logger.error("Failed to connect to MPD - continuing anyway")

        # Initialize Bluetooth service
        logger.info("Initializing Bluetooth service...")
        self.bluetooth_service = BluetoothService()

        # Initialize input manager
        logger.info("Initializing input manager...")
        self.input_manager = InputManager()
        self.input_manager.set_event_callback(self.handle_input_event)

        # Initialize screen stack
        self.screen_stack = ScreenStack()

        # Timing
        self.last_render_time = 0
        self.render_interval = 1.0 / self.RENDER_FPS
        self.last_input_poll_time = 0
        self.input_poll_interval = 1.0 / self.INPUT_POLL_RATE

        # Auto-update timer for now playing screen
        self.last_auto_update_time = 0
        self.auto_update_interval = 1.0  # Update every second

    def start(self):
        """Start the application with the initial screen"""
        logger.info("Starting MP3 Player App")

        # Push initial screen (Now Playing)
        self.screen_stack.push(NowPlayingScreen(self))

        # Start main loop
        self.running = True
        self.run()

    def run(self):
        """Main application loop"""
        logger.info("Entering main loop")

        try:
            while self.running:
                current_time = time.time()

                # Poll input at high rate
                if current_time - self.last_input_poll_time >= self.input_poll_interval:
                    self.input_manager.poll()
                    self.last_input_poll_time = current_time

                # Auto-update current screen (for live data like now playing)
                if current_time - self.last_auto_update_time >= self.auto_update_interval:
                    if self.screen_stack.current_screen:
                        # Only auto-update now playing screen
                        if isinstance(self.screen_stack.current_screen, NowPlayingScreen):
                            self.screen_stack.current_screen.update_playback_state()
                    self.last_auto_update_time = current_time

                # Render at controlled frame rate
                if current_time - self.last_render_time >= self.render_interval:
                    self.render()
                    self.last_render_time = current_time

                # Small sleep to prevent CPU spinning
                time.sleep(0.001)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.shutdown()

    def render(self):
        """Render current screen to display"""
        if not self.screen_stack.current_screen:
            return

        screen = self.screen_stack.current_screen

        # Only render if screen needs it
        if not screen.needs_render:
            return

        # Create image buffer
        image = Image.new('RGB', (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Let screen render itself (action bar + content)
        try:
            screen.render_base(draw)
            screen.needs_render = False
        except Exception as e:
            logger.error(f"Error rendering screen: {e}", exc_info=True)

        # Display on device
        try:
            self.device.display(image)
        except Exception as e:
            logger.error(f"Error displaying image: {e}")

    def handle_input_event(self, event: InputEvent):
        """
        Handle input events from input manager.

        Args:
            event: InputEvent from input manager
        """
        if not self.screen_stack.current_screen:
            return

        screen = self.screen_stack.current_screen

        try:
            if event.input_type == InputType.BUTTON_PRESS:
                logger.debug(f"Button {event.button_index} pressed")
                screen.handle_button(event.button_index)

            elif event.input_type == InputType.ENCODER_ROTATE:
                logger.debug(f"Encoder rotated: {event.encoder_delta}")
                screen.handle_encoder_rotate(event.encoder_delta)

            elif event.input_type == InputType.ENCODER_PRESS:
                logger.debug("Encoder pressed")
                screen.handle_encoder_press()

        except Exception as e:
            logger.error(f"Error handling input event: {e}", exc_info=True)

    def shutdown(self):
        """Clean shutdown of application"""
        logger.info("Shutting down MP3 Player App")

        self.running = False

        # Clear screen stack
        if self.screen_stack:
            self.screen_stack.clear()

        # Clean up input manager
        if self.input_manager:
            self.input_manager.cleanup()

        # Disconnect from MPD
        if self.mpd_service:
            self.mpd_service.disconnect()

        # Clear display
        try:
            black_image = Image.new('RGB', (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), (0, 0, 0))
            self.device.display(black_image)
        except Exception as e:
            logger.error(f"Error clearing display: {e}")

        logger.info("Shutdown complete")
