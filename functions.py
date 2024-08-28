import numpy as np
import pandas as pd
import pyaudio
import matplotlib.pyplot as plt


def load_notes_frequencies_csv():
    df = pd.read_csv('notes_frequencies.csv')
    note_list = df.iloc[:, 0].to_list()
    all_notes = df.iloc[:, 1:].to_numpy()
    return all_notes, note_list


def listen_pyaudio(audio, RECORD_SECONDS):
    FORMAT = pyaudio.paInt16
    CHUNK = 1024
    RATE = 44100
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
    
    audio_data = np.concatenate(frames) # convert frames to single numpy array
    return audio_data


def plot_raw_signal(audio_data):
    plt.figure(figsize=(10, 4))
    plt.plot(audio_data)
    plt.title('Recorded Audio Signal')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.xlim((0, len(audio_data)))
    
   
def get_signal_spectrum(audio_data):
    # Perform FFT
    n = len(audio_data)
    audio_data_fft = np.abs(np.fft.fft(audio_data))
    RATE = 44100
    frequencies = np.fft.fftfreq(n, 1/RATE)
    audio_fft = audio_data_fft[0:n//2]
    freq = frequencies[0:n//2]
    
    # Trim signal
    aux = freq <= 5000
    f = freq[aux]
    x = audio_fft[aux]
    
    return x, f


def plot_spectrum(x, f, threshold, note):
    plt.figure(figsize=(10, 4))
    plt.plot(f, x)
    plt.title('Recorded Audio Signal Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.hlines(threshold, xmin=0, xmax=f[-1], colors='red')
    if note:
        plt.vlines(note, ymin=0, ymax=np.max(x)*1.1, colors='red')
    plt.xlim((0, f[-1]))
    plt.ylim((0, np.max(x) * 1.1))
    
    
def get_note_frequency(x, f, threshold):
    if max(x) > threshold:
        # Identify harmonics
        ft = f[x >= threshold]
        
        # Identify first harmonic
        note = np.mean(ft[ft < ft[0]*1.05])
    else:
        note = None
    
    return note


def match_note(note, all_notes, note_list):
    # Identify note closest to first harmonic
    ratios = note/all_notes
    closeness = np.abs(ratios - 1)
    indices = np.where(closeness == np.min(closeness))
    
    note_str = note_list[indices[0][0]]
    
    # Detect whether note is higher or lower then target
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
        
    return note_str + difference_str
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 