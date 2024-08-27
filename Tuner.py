import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from functions import load_notes_frequencies_csv, listen_pyaudio, plot_raw_signal, get_signal_spectrum, plot_spectrum, note_frequency, match_note

#%%
plotting = True

#%% Load the data from the CSV file
all_notes, note_list = load_notes_frequencies_csv()

#%% Listen with PyAudio

# Parameters
RECORD_SECONDS = 1

# Initialize pyaudio
audio = pyaudio.PyAudio()

# Retrieve audio data
audio_data = listen_pyaudio(audio, RECORD_SECONDS)
audio.terminate()

#%% Plot data
if plotting:
    plot_raw_signal(audio_data)

#%%
volume_threshold = 100

if np.mean(np.abs(audio_data)) > volume_threshold:
    normalized_audio_data = audio_data / np.max(np.abs(audio_data)) # normalize audio_data
    
    # Perform FFT and get signal spectrum
    x, f = get_signal_spectrum(normalized_audio_data)
    
    # Identify note frequency
    magnitude_threshold = 500 # threshold for selecting first harmonic
    note = note_frequency(x, f, magnitude_threshold)
    
    # Plot spectrum
    if plotting:
        plot_spectrum(x, f, magnitude_threshold, note)
        
    # Identify note closest to first harmonic
    output_str = match_note(note, all_notes, note_list)
    print(output_str)
    
        
    
    
    
    
    
if plotting: 
    plt.show()
