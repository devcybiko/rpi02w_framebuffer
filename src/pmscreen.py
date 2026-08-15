from dataclasses import dataclass

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
