"""Bluetooth Service - Manages Bluetooth connections for Moode Audio"""
import subprocess
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BluetoothDevice:
    """Represents a Bluetooth device"""
    mac_address: str
    name: str
    paired: bool = False
    connected: bool = False
    trusted: bool = False


class BluetoothService:
    """Service for managing Bluetooth connections via BlueZ/bluetoothctl"""

    def __init__(self):
        self.adapter_available = self._check_adapter()

    def _check_adapter(self) -> bool:
        """Check if Bluetooth adapter is available"""
        try:
            result = subprocess.run(
                ["bluetoothctl", "show"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Bluetooth adapter check failed: {e}")
            return False

    def _run_bluetoothctl_command(self, command: str, timeout: int = 5) -> Optional[str]:
        """
        Run a bluetoothctl command and return output.

        Args:
            command: Command to run (without 'bluetoothctl' prefix)
            timeout: Command timeout in seconds

        Returns:
            Command output or None on error
        """
        try:
            result = subprocess.run(
                ["bluetoothctl", command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error(f"Bluetooth command timed out: {command}")
            return None
        except Exception as e:
            logger.error(f"Bluetooth command failed: {e}")
            return None

    def power_on(self) -> bool:
        """Turn Bluetooth adapter on"""
        output = self._run_bluetoothctl_command("power on")
        if output and "succeeded" in output.lower():
            logger.info("Bluetooth powered on")
            return True
        return False

    def power_off(self) -> bool:
        """Turn Bluetooth adapter off"""
        output = self._run_bluetoothctl_command("power off")
        if output and "succeeded" in output.lower():
            logger.info("Bluetooth powered off")
            return True
        return False

    def is_powered(self) -> bool:
        """Check if Bluetooth is powered on"""
        output = self._run_bluetoothctl_command("show")
        if output:
            return "Powered: yes" in output
        return False

    def is_discoverable(self) -> bool:
        """Check if adapter is discoverable"""
        output = self._run_bluetoothctl_command("show")
        if output:
            return "Discoverable: yes" in output
        return False

    def set_discoverable(self, enabled: bool) -> bool:
        """Set discoverable mode"""
        command = "discoverable on" if enabled else "discoverable off"
        output = self._run_bluetoothctl_command(command)
        if output and "succeeded" in output.lower():
            logger.info(f"Discoverable set to {enabled}")
            return True
        return False

    def start_scan(self) -> bool:
        """Start scanning for devices"""
        # Note: scan runs continuously, so we just initiate it
        try:
            # Start scan in background
            subprocess.Popen(
                ["bluetoothctl", "scan", "on"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info("Bluetooth scan started")
            return True
        except Exception as e:
            logger.error(f"Failed to start scan: {e}")
            return False

    def stop_scan(self) -> bool:
        """Stop scanning for devices"""
        output = self._run_bluetoothctl_command("scan off")
        if output:
            logger.info("Bluetooth scan stopped")
            return True
        return False

    def get_devices(self) -> List[BluetoothDevice]:
        """Get list of known Bluetooth devices"""
        devices = []

        output = self._run_bluetoothctl_command("devices")
        if not output:
            return devices

        # Parse device list
        for line in output.split('\n'):
            if line.startswith('Device'):
                parts = line.split()
                if len(parts) >= 3:
                    mac = parts[1]
                    name = ' '.join(parts[2:])

                    # Get device info
                    device = self._get_device_info(mac, name)
                    if device:
                        devices.append(device)

        return devices

    def _get_device_info(self, mac: str, name: str) -> Optional[BluetoothDevice]:
        """Get detailed info about a device"""
        output = self._run_bluetoothctl_command(f"info {mac}")
        if not output:
            return BluetoothDevice(mac_address=mac, name=name)

        # Parse device info
        paired = "Paired: yes" in output
        connected = "Connected: yes" in output
        trusted = "Trusted: yes" in output

        return BluetoothDevice(
            mac_address=mac,
            name=name,
            paired=paired,
            connected=connected,
            trusted=trusted
        )

    def get_connected_device(self) -> Optional[BluetoothDevice]:
        """Get currently connected device (if any)"""
        devices = self.get_devices()
        for device in devices:
            if device.connected:
                return device
        return None

    def pair(self, mac_address: str) -> bool:
        """
        Pair with a device.

        Args:
            mac_address: Device MAC address

        Returns:
            True if successful
        """
        output = self._run_bluetoothctl_command(f"pair {mac_address}", timeout=30)
        if output and ("successful" in output.lower() or "already paired" in output.lower()):
            logger.info(f"Paired with device {mac_address}")
            return True
        logger.warning(f"Failed to pair with {mac_address}")
        return False

    def connect(self, mac_address: str) -> bool:
        """
        Connect to a device.

        Args:
            mac_address: Device MAC address

        Returns:
            True if successful
        """
        output = self._run_bluetoothctl_command(f"connect {mac_address}", timeout=30)
        if output and ("successful" in output.lower() or "connection successful" in output.lower()):
            logger.info(f"Connected to device {mac_address}")
            return True
        logger.warning(f"Failed to connect to {mac_address}")
        return False

    def disconnect(self, mac_address: str) -> bool:
        """
        Disconnect from a device.

        Args:
            mac_address: Device MAC address

        Returns:
            True if successful
        """
        output = self._run_bluetoothctl_command(f"disconnect {mac_address}")
        if output and "successful" in output.lower():
            logger.info(f"Disconnected from device {mac_address}")
            return True
        return False

    def trust(self, mac_address: str) -> bool:
        """
        Trust a device (auto-connect).

        Args:
            mac_address: Device MAC address

        Returns:
            True if successful
        """
        output = self._run_bluetoothctl_command(f"trust {mac_address}")
        if output and "succeeded" in output.lower():
            logger.info(f"Trusted device {mac_address}")
            return True
        return False

    def untrust(self, mac_address: str) -> bool:
        """
        Untrust a device.

        Args:
            mac_address: Device MAC address

        Returns:
            True if successful
        """
        output = self._run_bluetoothctl_command(f"untrust {mac_address}")
        if output and "succeeded" in output.lower():
            logger.info(f"Untrusted device {mac_address}")
            return True
        return False

    def remove(self, mac_address: str) -> bool:
        """
        Remove/unpair a device.

        Args:
            mac_address: Device MAC address

        Returns:
            True if successful
        """
        output = self._run_bluetoothctl_command(f"remove {mac_address}")
        if output and "removed" in output.lower():
            logger.info(f"Removed device {mac_address}")
            return True
        return False
