from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import threading

class TrayIcon:
    """System tray icon for background operation."""
    
    def __init__(self, on_show=None, on_exit=None):
        self.on_show = on_show
        self.on_exit = on_exit
        self.icon = None

    def _create_image(self):
        """Creates a simple circle icon."""
        image = Image.new('RGB', (64, 64), (26, 26, 26))
        dc = ImageDraw.Draw(image)
        dc.ellipse((10, 10, 54, 54), fill=(0, 120, 215))
        return image

    def start(self):
        """Starts the tray icon in a separate thread."""
        menu = Menu(
            MenuItem('Show Window', self.on_show),
            MenuItem('Exit', self.on_exit)
        )
        self.icon = Icon("VoquillClone", self._create_image(), "Voquill Clone", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        if self.icon:
            self.icon.stop()
