from src.tuner import Tuner
from src.gui import Tuner_GUI

tuner = Tuner()
gui = Tuner_GUI(tuner)
gui.run()