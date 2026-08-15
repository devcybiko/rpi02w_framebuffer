from pmscreen import PMScreen, PMScreenConfig


class Main:
    def __init__(self):
        print("Initializing Main class")
        args = self._args()
        print(f"Arguments: {args}")

    def _args(self):
        import argparse
        parser = argparse.ArgumentParser(description="PMScreen Test")
        parser.add_argument("--quiet", action="store_true", help="Disable debug output")
        parser.add_argument("--fast", action="store_true", dest="fast", help="Enable fast flush")
        return parser.parse_args()

    def run(self):
        print("Running Main class")
        screen = PMScreen(PMScreenConfig(), fast_flush=args.fast, debug=not args.quiet)

if __name__ == "__main__":
    main = Main()
    main.run()