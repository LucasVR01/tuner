import numpy as np
import pandas as pd
import pyaudio
import matplotlib.pyplot as plt


def load_notes_frequencies_csv():
    df = pd.read_csv('notes_frequencies.csv')
    note_list = df.iloc[:, 0].to_list()
    all_notes = df.iloc[:, 1:].to_numpy()
    return all_notes, note_list


def listen_pyaudio(audio, CHUNK, RATE, RECORD_SECONDS):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    # Open stream
    stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []
    for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(np.frombuffer(data, dtype=np.int16))

    print("Recording finished.")

    # Close stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    audio_data = np.concatenate(frames) # convert frames to single numpy array
    return audio_data
    