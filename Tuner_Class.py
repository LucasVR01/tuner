import numpy as np
import pandas as pd
import pyaudio
import time

class Tuner:
    def __init__(self, record_seconds=0.5, chunk=1024, rate=44100, ):
        self.record_seconds = record_seconds
        self.chunk = chunk
        self.rate = rate
        self.volume_threshold = 100
        self.magnitude_threshold = 120
        self.audio = pyaudio.PyAudio()
        self.all_notes, self.note_list = self.load_notes_frequencies_csv()
        
    
    def load_notes_frequencies_csv(self):
        df = pd.read_csv('notes_frequencies.csv')
        note_list = df.iloc[:, 0].to_list()
        all_notes = df.iloc[:, 1:].to_numpy()
        return all_notes, note_list
        
    
    def listen_pyaudio(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
    
        stream = self.audio.open(format=FORMAT,
                                 channels=CHANNELS,
                                 rate=self.rate,
                                 input=True,
                                 frames_per_buffer=self.chunk)
    
        frames = []
        for _ in range(int(self.RATE / self.CHUNK * self.record_seconds)):
            data = stream.read(self.CHUNK)
            frames.append(np.frombuffer(data, dtype=np.int16))
    
        stream.stop_stream()
        stream.close()
    
        audio_data = np.concatenate(frames)
        return audio_data
    
    
    def get_signal_spectrum(self, audio_data):
        # Perform FFT
        n = len(audio_data)
        audio_data_fft = np.abs(np.fft.fft(audio_data))
        frequencies = np.fft.fftfreq(n, 1/self.rate)
        audio_fft = audio_data_fft[0:n//2]
        freq = frequencies[0:n//2]
        
        # Trim signal
        aux = freq <= 2500
        f = freq[aux]
        x = audio_fft[aux]
        
        return x, f
    
    
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
            difference_str = "↑"
            
        return note_str + difference_str

