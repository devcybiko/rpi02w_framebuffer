from pmscreen import PMScreen, PMScreenConfig
from PIL import Image, ImageDraw


class Main:
    def __init__(self):
        print("Initializing Main class")
        self.args = self._args()
        print(f"Arguments: {self.args}")

    def _args(self):
        import argparse
        parser = argparse.ArgumentParser(description="PMScreen Test")
        parser.add_argument("--quiet", action="store_true", help="Disable debug output")
        parser.add_argument("--fast", action="store_true", dest="fast", help="Enable fast flush")
        return parser.parse_args()

    def run(self):
        print("Running Main class")
        screen = PMScreen(PMScreenConfig(), debug = not self.args.quiet)
        screen._hard_clear(b"\xff\xff")  # Clear the framebuffer to white
        screen = PMScreen(PMScreenConfig(), fast_flush=args.fast, debug=not args.quiet)
        screen.clear()  # Clear the screen
        screen.flush()  # Flush the changes to the framebuffer
        screen.rectangle((10, 10, 1910, 1070), color="red", width=5)  # Draw a white rectangle around the screen
        screen.flush()  # Flush the changes to the framebuffer
        screen.line((10, 10, 1910, 1070), color="green", width=3)  # Draw a green diagonal line
        screen.flush()  # Flush the changes to the framebuffer
        screen.line((10, 1070, 1910, 10), color="blue", width=3)  # Draw a blue diagonal line
        screen.flush()  # Flush the changes to the framebuffer

        screen.flush()  # Flush the cleared image to the framebuffer

if __name__ == "__main__":
    main = Main()
    main.run()
    while True:
        pass  # Keep the program running to maintain the framebuffer state