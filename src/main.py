from src.pmscreen import PMScreen, PMScreenConfig

DEBUG = True
def _debug(*args, **kwargs) -> None:
    """Print debug messages to the console."""
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

class Main:
    def __init__(self):
        print("Initializing Main class")
        args = self._args()
        print(f"Arguments: {args}")
        screen = PMScreen(PMScreenConfig(), fast_flush=args.fast, debug=not args.quiet)
        screen.clear()  # Clear the screen
        screen.flush()  # Flush the changes to the framebuffer
        screen.rectangle((10, 10, 1910, 1070), color="red", width=5)  # Draw a white rectangle around the screen
        screen.flush()  # Flush the changes to the framebuffer
        screen.line((10, 10, 1910, 1070), color="green", width=3)  # Draw a green diagonal line
        screen.flush()  # Flush the changes to the framebuffer
        screen.line((10, 1070, 1910, 10), color="blue", width=3)  # Draw a blue diagonal line
        screen.flush()  # Flush the changes to the framebuffer
        screen.text((1920//2, 1080//2), "Hello, PMScreen!", color="yellow")  # Draw text on the screen
        screen.flush()  # Flush the changes to the framebuffer

    def _args(self):
        import argparse
        parser = argparse.ArgumentParser(description="PMScreen Test")
        parser.add_argument("--quiet", action="store_true", help="Disable debug output")
        parser.add_argument("--fast", action="store_true", dest="fast", help="Enable fast flush")
        return parser.parse_args()

if __name__ == "__main__":
    main = Main()
