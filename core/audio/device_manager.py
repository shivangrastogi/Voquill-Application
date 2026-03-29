import sounddevice as sd

class DeviceManager:
    """Handles discovery and selection of audio input devices."""
    
    @staticmethod
    def list_input_devices():
        """Returns a list of available input devices."""
        devices = sd.query_devices()
        input_devices = []
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': dev['name'],
                    'channels': dev['max_input_channels'],
                    'default_samplerate': dev['default_samplerate']
                })
        return input_devices

    @staticmethod
    def get_default_input_device():
        """Returns the default input device."""
        return sd.query_devices(kind='input')

    @staticmethod
    def set_default_device(device_index):
        """Sets the default input device (for the session)."""
        sd.default.device[0] = device_index
