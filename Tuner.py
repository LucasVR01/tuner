import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from functions import load_notes_frequencies_csv, listen_pyaudio, plot_raw_signal, get_signal_spectrum, plot_spectrum, get_note_frequency, match_note

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
    magnitude_threshold = 1000 # threshold for selecting first harmonic
    note = get_note_frequency(x, f, magnitude_threshold)
    
    # Plot spectrum
    if plotting:
        plot_spectrum(x, f, magnitude_threshold, note)
        
    # Identify note closest to first harmonic
    '''output_str = match_note(note, all_notes, note_list)'''
    # Identify note closest to first harmonic
    ratios = note/all_notes
    closeness = np.abs(ratios - 1)
    indices = np.where(closeness == np.min(closeness))
    
    note_str = note_list[indices[0][0]]
    
    # Detect whether note is higher or lower than target
    difference = (ratios[indices] - 1) * 100
    if difference > 2:
        difference_str = " ↓↓↓"
    elif difference > 1.3:
        difference_str = " ↓↓"
    elif difference > 0.5:
        difference_str = " ↓"
    elif difference < 0.5 and difference > -0.5:
        difference_str = ""
    elif difference < -2:
        difference_str = " ↑↑↑"
    elif difference < -1.3:
        difference_str = " ↑↑"
    else:
        difference_str = " ↑"
        
    output_str = note_str + difference_str
    print(output_str)
    
    
if plotting: 
    plt.show()
