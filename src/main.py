from src.pmscreen import PMScreen, PMScreenConfig

DEBUG = True
def _debug(*args, **kwargs) -> None:
    """Print debug messages to the console."""
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

class Main:
    def __init__(self):
        print("Initializing Main class")
        screen = PMScreen(PMScreenConfig())
        screen.clear()  # Clear the screen
        screen.line()

if __name__ == "__main__":
    main = Main()
