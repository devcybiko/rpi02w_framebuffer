from dataclasses import dataclass
from PIL import Image, ImageDraw
from clib import rgba_to_rgb16

@dataclass
class PMScreenConfig:
    width: int = 1920
    height: int = 1080
    frame_buffer: str = "/dev/fb0"  # Path to framebuffer device

class PMScreen:
    def __init__(self, _screen: PMScreenConfig, fast_flush: bool = True, debug: bool = False):
        self._screen = _screen or PMScreenConfig()  # Use provided config or default

