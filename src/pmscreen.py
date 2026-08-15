import os
from dataclasses import dataclass
from PIL import Image

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
    def __init__(self, _screen: PMScreenConfig):
        self._screen = _screen or PMScreenConfig()  # Use provided config or default
        self._img = Image.new("RGBA", (self._screen.width, self._screen.height), 0)
        self._hard_clear(b"\xff\xff")  # Clear the framebuffer with white color

    def _hard_clear(self, color: bytes = b"\x00\x00") -> None:
        """Clear the framebuffer by writing zeros to it."""
        # Open the framebuffer device and write zeros to it
        with open(self._screen.frame_buffer, "wb") as f:
            f.write(color * (self._screen.width * self._screen.height))  # RGB565: 2 bytes per pixel

    def _write_framebuffer(self, img: Image.Image) -> None:
        """Write the image to the framebuffer."""
        # self._screen.frame_buffer = "./fb0.jpg"
        if self._screen.frame_buffer:
            _debug(f"Writing to framebuffer: {self._screen.frame_buffer}")
            from clib import rgba_to_rgb16

            _debug(f"Image size: {img.size}, mode: {img.mode}")
            if self._screen.rotate:
                img = img.rotate(self._screen.rotate, expand=True)
            raw = img.tobytes("raw")
            _debug(f"Raw image size: {len(raw)} bytes")
            # Convert the image to RGB565 format
            rgb565 = rgba_to_rgb16(raw, img.width, img.height)
            _debug(f"Converted to RGB565 size: {len(rgb565)} bytes")
            with open(self._screen.frame_buffer, "wb") as f:
                _debug(f"Saving RGB565 image to {self._screen.frame_buffer}")
                f.write(rgb565)
            _debug("Framebuffer write complete")
            rgb565 = rgba_to_rgb16(raw, img.width, img.height)
            _debug(f"Converted to RGB565 size: {len(rgb565)} bytes")
            with open(self._screen.frame_buffer, "wb") as f:
                _debug(f"Saving RGB565 image to {self._screen.frame_buffer}")
                f.write(rgb565)
            _debug("Framebuffer write complete")

    def flush(self) -> None:
        img = self.bitmap._img
        self._write_framebuffer(img)
        self._atomic_write(img)
