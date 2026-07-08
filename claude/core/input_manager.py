"""Input Manager - Handles NeoKey buttons and rotary encoder input"""
import board
import busio
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw.rotaryio import IncrementalEncoder
from adafruit_seesaw.digitalio import DigitalIO
from adafruit_neokey.neokey1x4 import NeoKey1x4
from digitalio import DigitalInOut
import time
from typing import Callable, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class InputType(Enum):
    """Types of input events"""
    BUTTON_PRESS = "button_press"
    BUTTON_RELEASE = "button_release"
    ENCODER_ROTATE = "encoder_rotate"
    ENCODER_PRESS = "encoder_press"
    ENCODER_RELEASE = "encoder_release"


@dataclass
class InputEvent:
    """Represents an input event from buttons or encoder"""
    input_type: InputType
    button_index: Optional[int] = None  # 0-3 for neokey buttons
    encoder_delta: Optional[int] = None  # -1 for CCW, +1 for CW


class InputManager:
    """Manages all input hardware: NeoKey buttons and rotary encoder"""

    # NeoKey I2C addresses
    NEOKEY_ADDR = 0x30
    ENCODER_ADDR = 0x36

    # Encoder button pin
    ENCODER_BUTTON_PIN = 24

    def __init__(self):
        # Initialize I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Initialize NeoKey (4 buttons with RGB LEDs)
        try:
            self.neokey = NeoKey1x4(self.i2c, addr=self.NEOKEY_ADDR)
            self.neokey_available = True
            logger.info("NeoKey initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NeoKey: {e}")
            self.neokey_available = False

        # Initialize rotary encoder
        try:
            self.encoder_seesaw = Seesaw(self.i2c, addr=self.ENCODER_ADDR)
            self.encoder = IncrementalEncoder(self.encoder_seesaw)
            self.encoder_button = DigitalIO(self.encoder_seesaw, self.ENCODER_BUTTON_PIN)
            self.encoder_button.switch_to_input(pull=True)
            self.encoder_available = True
            logger.info("Rotary encoder initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize rotary encoder: {e}")
            self.encoder_available = False

        # State tracking
        self.button_states = [False] * 4  # Track button press states
        self.encoder_button_state = False
        self.last_encoder_position = 0

        # Event callback
        self.event_callback: Optional[Callable[[InputEvent], None]] = None

    def set_event_callback(self, callback: Callable[[InputEvent], None]):
        """Set callback function for input events"""
        self.event_callback = callback

    def set_button_color(self, button_index: int, color: Tuple[int, int, int]):
        """
        Set LED color for a specific button

        Args:
            button_index: 0-3 for the four buttons
            color: RGB tuple (0-255, 0-255, 0-255)
        """
        if not self.neokey_available:
            return

        try:
            self.neokey.pixels[button_index] = color
        except Exception as e:
            logger.error(f"Error setting button {button_index} color: {e}")

    def set_all_button_colors(self, colors: list[Tuple[int, int, int]]):
        """
        Set LED colors for all buttons at once

        Args:
            colors: List of 4 RGB tuples
        """
        if not self.neokey_available or len(colors) != 4:
            return

        try:
            for i, color in enumerate(colors):
                self.neokey.pixels[i] = color
        except Exception as e:
            logger.error(f"Error setting button colors: {e}")

    def clear_button_leds(self):
        """Turn off all button LEDs"""
        self.set_all_button_colors([(0, 0, 0)] * 4)

    def poll(self):
        """Poll for input events and trigger callbacks"""
        # Poll NeoKey buttons
        if self.neokey_available:
            try:
                for i in range(4):
                    current_state = self.neokey[i]
                    previous_state = self.button_states[i]

                    if current_state and not previous_state:
                        # Button pressed
                        self.button_states[i] = True
                        if self.event_callback:
                            event = InputEvent(
                                input_type=InputType.BUTTON_PRESS,
                                button_index=i
                            )
                            self.event_callback(event)

                    elif not current_state and previous_state:
                        # Button released
                        self.button_states[i] = False
                        if self.event_callback:
                            event = InputEvent(
                                input_type=InputType.BUTTON_RELEASE,
                                button_index=i
                            )
                            self.event_callback(event)

            except Exception as e:
                logger.error(f"Error polling NeoKey: {e}")

        # Poll rotary encoder
        if self.encoder_available:
            try:
                # Check for rotation
                current_position = self.encoder.position
                if current_position != self.last_encoder_position:
                    delta = current_position - self.last_encoder_position
                    self.last_encoder_position = current_position

                    if self.event_callback:
                        event = InputEvent(
                            input_type=InputType.ENCODER_ROTATE,
                            encoder_delta=delta
                        )
                        self.event_callback(event)

                # Check encoder button (active low)
                current_button_state = not self.encoder_button.value
                previous_button_state = self.encoder_button_state

                if current_button_state and not previous_button_state:
                    # Encoder button pressed
                    self.encoder_button_state = True
                    if self.event_callback:
                        event = InputEvent(input_type=InputType.ENCODER_PRESS)
                        self.event_callback(event)

                elif not current_button_state and previous_button_state:
                    # Encoder button released
                    self.encoder_button_state = False
                    if self.event_callback:
                        event = InputEvent(input_type=InputType.ENCODER_RELEASE)
                        self.event_callback(event)

            except Exception as e:
                logger.error(f"Error polling encoder: {e}")

    def cleanup(self):
        """Clean up resources"""
        try:
            self.clear_button_leds()
            logger.info("Input manager cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
