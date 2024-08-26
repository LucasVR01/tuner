import numpy as np
import pandas as pd
import pyaudio
import matplotlib.pyplot as plt

# Load the data from the CSV file
df = pd.read_csv('notes_frequencies.csv')
note_list = df.iloc[:, 0].to_list()
all_notes = df.iloc[:, 1:].to_numpy()


# Listen with PyAudio

# Parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 2

# Initialize pyaudio
audio = pyaudio.PyAudio()

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

# Plot data
audio_data = np.concatenate(frames) # convert frames to single numpy array
audio_data = audio_data / np.max(np.abs(audio_data)) # normalize audio_data
plt.figure(figsize=(10, 4))
plt.plot(audio_data)
plt.title('Recorded Audio Signal')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')

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
