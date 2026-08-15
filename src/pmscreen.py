from dataclasses import dataclass
from PIL import Image, ImageDraw
from clib import rgba_to_rgb16

DEBUG = True

def _debug(*args, **kwargs) -> None:
    """Print debug messages to the console."""
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

@dataclass
class PMScreenConfig:
    width: int = 1920
    height: int = 1080
    frame_buffer: str = "/dev/fb0"  # Path to framebuffer device

class PMScreen:
    def __init__(self, _screen: PMScreenConfig, fast_flush: bool = True, debug: bool = False):
        self._screen = _screen or PMScreenConfig()  # Use provided config or default
        self._img = Image.new("RGBA", (self._screen.width, self._screen.height), 0)
        self._draw = ImageDraw.Draw(self._img)
        self._fast_flush = fast_flush
        self._debug = debug
        self._hard_clear(b"\x00\x00")  # Clear the framebuffer with white color

    def _hard_clear(self, color: bytes = b"\x00\x00") -> None:
        """Clear the framebuffer by writing zeros to it."""
        # Open the framebuffer device and write zeros to it
        with open(self._screen.frame_buffer, "wb") as f:
            f.write(color * (self._screen.width * self._screen.height))  # RGB565: 2 bytes per pixel

    def _fast_write_framebuffer(self, img: Image.Image) -> None:
        """Write the image to the framebuffer."""
        # self._screen.frame_buffer = "./fb0.jpg"
        if self._screen.frame_buffer:
            _debug(f"Writing to framebuffer: {self._screen.frame_buffer}")
            from clib import rgba_to_rgb16
            raw = img.tobytes("raw")
            _debug(f"Raw image size: {len(raw)} bytes")
            # Convert the image to RGB565 format
            rgb565 = rgba_to_rgb16(raw, img.width, img.height)
            _debug(f"Converted to RGB565 size: {len(rgb565)} bytes")
            with open(self._screen.frame_buffer, "wb") as f:
                _debug(f"Saving RGB565 image to {self._screen.frame_buffer}")
                f.write(rgb565)
            _debug("Framebuffer write complete")

    def _slow_write_framebuffer(self, img: Image.Image = None) -> None:
        """Write the image to the framebuffer slowly (for debugging)."""
        ## convert the image to RGB565 format using python code assuming 1920x1080 resolution x2 RGB565 bytes per pixel
        import struct
        rgb565 = bytearray()
        _debug(f"converting RGB565 buffer")
        img = img or self._img
        for y in range(img.height):
            _debug(f"...converting row: {y}/{img.height}")
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

    def flush(self) -> None:
        """Flush the current image to the framebuffer."""
        if self._fast_flush:
            self._fast_write_framebuffer(self._img)
        else:
            self._slow_write_framebuffer(self._img)

    def clear(self, color=None) -> None:
        _debug(f"Clearing screen with color: {color}")
        self._draw.rectangle(
            (0, 0, self._img.width-1, self._img.height-1), 0x00 if color is None else color
        )

    def line(self, rect: tuple, color="white", width=1) -> None:
        _debug(f"Drawing line with rect: {rect}, color: {color}, width: {width}")
        self._draw.line(rect, fill=color, width=width)
