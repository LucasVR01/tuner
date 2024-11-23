# Tuner Application

This project is a Python-based tuner application that detects musical notes in real-time. It includes a graphical user interface (GUI) built with Tkinter and a core tuning engine that processes audio input to determine the note being played and how closely it matches the correct frequency.

---

## Project Files

### `src/tuner.py`
This file contains the core logic for audio processing and note detection. Key features include:
- **Real-Time Audio Processing**: Captures audio input using `pyaudio`.
- **Frequency Analysis**: Uses Fast Fourier Transform (FFT) to determine the frequency components of the signal.
- **Note Matching**: Maps detected frequencies to musical notes based on the `notes_frequencies.csv` file.
- **Callback Support**: Allows integration with a GUI for real-time updates.

### `src/gui.py`
This file defines the graphical user interface for the tuner. Key features include:
- **Start/Stop Buttons**: Allows users to start or stop the tuner.
- **Note Display**: Shows the detected musical note.
- **Progress Bar**: Visualizes how close the detected note is to the correct frequency.
- **Tkinter Framework**: Provides an interactive and user-friendly experience.

### `data/notes_frequencies.csv`
This CSV file contains a mapping of musical notes to their corresponding frequencies. It is used by the `Tuner.py` file for accurate note detection.

---

## Features
- Detects musical notes from live audio input.
- Displays real-time feedback in a GUI.
- Progress bar indicates how close a note is to being perfectly in tune.
- Adjustable parameters for sensitivity and accuracy.

