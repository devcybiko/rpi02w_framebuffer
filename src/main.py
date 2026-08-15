from pmscreen import PMScreen, PMScreenConfig


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
        screen._hard_clear(b"\x07\x0")  # Clear the framebuffer to black

if __name__ == "__main__":
    main = Main()
    main.run()
    while True:
        pass  # Keep the program running to maintain the framebuffer state