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
        screen = PMScreen(PMScreenConfig(), fast_flush=args.fast, debug=args.debug)
        screen.clear()  # Clear the screen
        screen.rectangle((0, 0, 1919, 1079), color="white", width=1)  # Draw a white rectangle around the screen
        screen.line((0, 0, 1919, 1079))
        screen.flush()  # Flush the changes to the framebuffer

    def _args(self):
        import argparse
        parser = argparse.ArgumentParser(description="PMScreen Test")
        parser.add_argument("--debug", action="store_true", dest="debug", default=True, help="Enable debug output")
        parser.add_argument("--fast", action="store_true", dest="fast", default=False, help="Enable fast flush")
        return parser.parse_args()

if __name__ == "__main__":
    main = Main()
