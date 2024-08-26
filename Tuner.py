import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from functions import load_notes_frequencies_csv, listen_pyaudio

#%% Load the data from the CSV file
all_notes, note_list = load_notes_frequencies_csv()

#%% Listen with PyAudio

# Parameters
CHUNK = 1024
RATE = 44100
RECORD_SECONDS = 2

# Initialize pyaudio
audio = pyaudio.PyAudio()

# Retrieve audio data
audio_data = listen_pyaudio(audio, CHUNK, RATE, RECORD_SECONDS)

#%% Plot data
plt.figure(figsize=(10, 4))
plt.plot(audio_data)
plt.title('Recorded Audio Signal')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
volume_threshold = 100

#%%
if np.mean(np.abs(audio_data)) > volume_threshold:
    audio_data = audio_data / np.max(np.abs(audio_data)) # normalize audio_data
    
    # Perform FFT
    n = len(audio_data)
    audio_data_fft = np.abs(np.fft.fft(audio_data))
    frequencies = np.fft.fftfreq(n, 1/RATE)
    audio_fft = audio_data_fft[0:n//2]
    freq = frequencies[0:n//2]
    
    # Trim signal
    aux = freq <= 2500
    f = freq[aux]
    x = audio_fft[aux]
    
    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(f, x)
    plt.title('Recorded Audio Signal Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    
    # Identify harmonics
    threshold = 500
    ft = f[x >= threshold]
    print(ft)
    plt.hlines(threshold, xmin=0, xmax=f[-1], colors='red')
    
    # Identify first harmonic
    note = np.mean(ft[ft < ft[0]*1.05])
    plt.vlines(note, ymin=0, ymax=np.max(x), colors='red')
    
    
    
    
plt.show()
