"""Bluetooth Screen - Manage Bluetooth connections"""
from claude.ui.base_screen import BaseScreen
from claude.ui.action_bar import ActionIcon
from PIL import ImageDraw
import logging

logger = logging.getLogger(__name__)


class BluetoothScreen(BaseScreen):
    """Screen for managing Bluetooth connections"""

    def __init__(self, app):
        super().__init__(app)

        # State
        self.devices = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 6
        self.scanning = False
        self.connected_device = None

    def on_enter(self):
        """Called when screen becomes active"""
        super().on_enter()

        # Configure action bar: Back, Scan, Connect, Power
        self.configure_action_bar(
            icons=[ActionIcon.BACK, ActionIcon.SHUFFLE, ActionIcon.BLUETOOTH, ActionIcon.STOP],
            colors=[self.COLOR_RED, self.COLOR_YELLOW, self.COLOR_GREEN, self.COLOR_BLUE]
        )

        # Load devices
        self.refresh_devices()

    def on_exit(self):
        """Called when screen is deactivated"""
        super().on_exit()

        # Stop scanning if active
        if self.scanning:
            self.bluetooth.stop_scan()
            self.scanning = False

    def refresh_devices(self):
        """Refresh device list"""
        self.devices = self.bluetooth.get_devices()
        self.connected_device = self.bluetooth.get_connected_device()
        logger.info(f"Found {len(self.devices)} Bluetooth devices")
        self.request_render()

    def render_content(self, draw: ImageDraw.ImageDraw):
        """Render bluetooth screen"""
        # Background
        draw.rectangle(
            [(0, self.CONTENT_Y_START), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
            fill=self.COLOR_BLACK
        )

        # Title with status
        title = "Bluetooth"
        if self.scanning:
            title += " (Scanning...)"
        elif not self.bluetooth.is_powered():
            title += " (Off)"

        self.draw_title_bar(draw, title)

        # Connected device indicator
        y_pos = self.CONTENT_Y_START + 30

        if self.connected_device:
            self.draw_text(
                draw,
                f"Connected: {self.connected_device.name}",
                (10, y_pos),
                fill=self.COLOR_GREEN,
                max_width=self.DISPLAY_WIDTH - 20
            )
            y_pos += 25
        else:
            self.draw_text(
                draw,
                "No device connected",
                (10, y_pos),
                fill=self.COLOR_GRAY
            )
            y_pos += 25

        if not self.devices:
            self.draw_text(
                draw,
                "No devices found" if self.bluetooth.is_powered() else "Bluetooth is off",
                (self.DISPLAY_WIDTH // 2, y_pos + 30),
                fill=self.COLOR_GRAY,
                align="center"
            )
            return

        # Calculate visible range
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.items_per_page:
            self.scroll_offset = self.selected_index - self.items_per_page + 1

        # Draw device list
        item_height = 25
        y_start = y_pos + 5

        for i in range(self.scroll_offset, min(self.scroll_offset + self.items_per_page, len(self.devices))):
            device = self.devices[i]
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

            # Device name
            display_name = device.name

            # Add status indicators
            if device.connected:
                display_name = "● " + display_name
            elif device.paired:
                display_name = "○ " + display_name

            # Draw device
            self.draw_text(
                draw,
                display_name,
                (10, y_pos),
                fill=text_color,
                max_width=290
            )

        # Draw scrollbar
        if len(self.devices) > self.items_per_page:
            self.draw_scrollbar(
                draw,
                total_items=len(self.devices),
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
            # Scan/Refresh button
            if not self.bluetooth.is_powered():
                self.bluetooth.power_on()

            if self.scanning:
                self.bluetooth.stop_scan()
                self.scanning = False
            else:
                self.bluetooth.start_scan()
                self.scanning = True

            # Refresh devices after short delay
            import time
            time.sleep(0.5)
            self.refresh_devices()

        elif button_index == 2:
            # Connect/Disconnect button
            if self.devices and 0 <= self.selected_index < len(self.devices):
                device = self.devices[self.selected_index]

                if device.connected:
                    # Disconnect
                    self.bluetooth.disconnect(device.mac_address)
                    logger.info(f"Disconnecting from {device.name}")
                else:
                    # Connect (pair first if needed)
                    if not device.paired:
                        logger.info(f"Pairing with {device.name}")
                        self.bluetooth.pair(device.mac_address)

                    logger.info(f"Connecting to {device.name}")
                    self.bluetooth.connect(device.mac_address)

                # Refresh devices
                import time
                time.sleep(1)
                self.refresh_devices()

        elif button_index == 3:
            # Power toggle button
            if self.bluetooth.is_powered():
                self.bluetooth.power_off()
            else:
                self.bluetooth.power_on()

            self.refresh_devices()

    def handle_encoder_rotate(self, delta: int):
        """Handle encoder rotation for list navigation"""
        if not self.devices:
            return

        # Update selection
        self.selected_index += delta

        # Wrap around
        if self.selected_index < 0:
            self.selected_index = len(self.devices) - 1
        elif self.selected_index >= len(self.devices):
            self.selected_index = 0

        self.request_render()

    def handle_encoder_press(self):
        """Handle encoder press to connect/disconnect"""
        if self.devices and 0 <= self.selected_index < len(self.devices):
            device = self.devices[self.selected_index]

            if device.connected:
                self.bluetooth.disconnect(device.mac_address)
            else:
                if not device.paired:
                    self.bluetooth.pair(device.mac_address)
                self.bluetooth.connect(device.mac_address)

            # Refresh devices
            import time
            time.sleep(1)
            self.refresh_devices()
