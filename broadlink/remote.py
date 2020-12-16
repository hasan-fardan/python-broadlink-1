"""Support for universal remotes."""
import struct

from .device import device
from .exceptions import check_error


class rm(device):
    """Controls a Broadlink RM."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the controller."""
        device.__init__(self, *args, **kwargs)
        self.type = "RM2"

    def _send_command(self, command: int, data: bytes = b'') -> bytes:
        """Send a command to the device."""
        packet = struct.pack("<I", command) + data
        response = self.send_packet(0x6A, packet)
        check_error(response[0x22:0x24])
        payload = self.decrypt(response[0x38:])
        return payload[0x4:]

    def check_data(self) -> bytes:
        """Return the last captured code."""
        return self._send_command(0x4)

    def send_data(self, data: bytes) -> None:
        """Send a code to the device."""
        self._send_command(0x2, data)

    def enter_learning(self) -> None:
        """Enter infrared learning mode."""
        self._send_command(0x3)

    def sweep_frequency(self) -> None:
        """Sweep frequency."""
        self._send_command(0x19)

    def cancel_sweep_frequency(self) -> None:
        """Cancel sweep frequency."""
        self._send_command(0x1E)

    def check_frequency(self) -> bool:
        """Return True if the frequency was identified successfully."""
        data = self._send_command(0x1A)
        return data[0] == 1

    def find_rf_packet(self) -> bool:
        """Enter radiofrequency learning mode."""
        data = self._send_command(0x1B)
        return data[0] == 1

    def check_temperature(self) -> float:
        """Return the temperature."""
        return self.check_sensors()["temperature"]

    def check_sensors(self) -> dict:
        """Return the state of the sensors."""
        data = self._send_command(0x1)
        return {"temperature": data[0x0] + data[0x1] / 10.0}


class rm4(rm):
    """Controls a Broadlink RM4."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the controller."""
        device.__init__(self, *args, **kwargs)
        self.type = "RM4"

    def _send_command(self, command: int, data: bytes = b'') -> bytes:
        """Send a command to the device."""
        packet = struct.pack("<HI", len(data) + 4, command) + data
        response = self.send_packet(0x6A, packet)
        check_error(response[0x22:0x24])
        payload = self.decrypt(response[0x38:])
        return payload[0x6:]

    def check_humidity(self) -> float:
        """Return the humidity."""
        return self.check_sensors()["humidity"]

    def check_sensors(self) -> dict:
        """Return the state of the sensors."""
        data = self._send_command(0x24)
        return {
            "temperature": data[0x0] + data[0x1] / 100.0,
            "humidity": data[0x2] + data[0x3] / 100.0,
        }
