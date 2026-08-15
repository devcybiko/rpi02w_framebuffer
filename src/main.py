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
        screen.line((0, 0, 1919, 1079), color=0xFFFF, width=2)
        screen.flush()  # Flush the changes to the framebuffer

if __name__ == "__main__":
    main = Main()
