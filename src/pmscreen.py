from dataclasses import dataclass
from PIL import Image, ImageDraw

@dataclass
class PMScreenConfig:
    width: int = 1920
    height: int = 1080
    frame_buffer: str = "/dev/fb0"  # Path to framebuffer device

class PMScreen:
    def __init__(self, _screen: PMScreenConfig, fast_flush: bool = True, debug: bool = False):
        self._screen = _screen or PMScreenConfig()  # Use provided config or default
        self._debug = debug
        self._print(f"Initialized PMScreen with config: {self._screen}, fast_flush={fast_flush}, debug={debug}")
        self._img = Image.new("RGBA", (self._screen.width, self._screen.height), 0)
        self._draw = ImageDraw.Draw(self._img)

    def _print(self, *args, **kwargs) -> None:
        """Print debug messages to the console."""
        if self._debug:
            print("[DEBUG]", *args, **kwargs)

    def _hard_clear(self, color: bytes = b"\x00\x00") -> None:
        """Clear the framebuffer by writing zeros to it."""
        # Open the framebuffer device and write zeros to it
        with open(self._screen.frame_buffer, "wb") as f:
            f.write(color * (self._screen.width * self._screen.height))  # RGB565: 2 bytes per pixel

    def _slow_write_framebuffer(self, img: Image.Image = None) -> None:
        """Write the image to the framebuffer slowly (for debugging)."""
        ## convert the image to RGB565 format using python code assuming 1920x1080 resolution x2 RGB565 bytes per pixel
        import struct
        rgb565 = bytearray()
        self._print(f"converting RGB565 buffer")
        img = img or self._img
        for y in range(img.height):
            self._print(f"...converting row: {y}/{img.height}")
            for x in range(img.width):
                r, g, b, a = img.getpixel((x, y))
                # RGB565: RRRRRGGGGGGBBBBB (5 bits R, 6 bits G, 5 bits B)
                r5 = (r >> 3) & 0x1F
                g6 = (g >> 2) & 0x3F
                b5 = (b >> 3) & 0x1F
                rgb565_word = (r5 << 11) | (g6 << 5) | b5
                # Pack as little-endian 16-bit
                rgb565.extend(struct.pack('<H', rgb565_word))
        with open(self._screen.frame_buffer, "wb") as f:
            f.write(rgb565)

    