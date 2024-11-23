from src.tuner import Tuner
from src.gui import Tuner_GUI

def main():
    # Create tuner and GUI objects
    tuner = Tuner()
    gui = Tuner_GUI(tuner)

    # Run GUI
    gui.run()


if __name__ == "__main__":
    main()