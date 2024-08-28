import numpy as np
import pandas as pd
import pyaudio
import time
import os

class Tuner:
    def __init__(self, record_seconds=2, chunk=1024, rate=44100, volume_threshold=100, magnitude_threshold=2000):
        self.record_seconds = record_seconds
        self.chunk = chunk
        self.rate = rate
        self.volume_threshold = volume_threshold
        self.magnitude_threshold = magnitude_threshold
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
        for _ in range(int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
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
    
    
    def get_note_frequency(self, x, f):
        if max(x) > self.magnitude_threshold:
            # Identify harmonics
            ft = f[x >= self.magnitude_threshold]
            
            # Identify first harmonic
            note = np.mean(ft[ft < ft[0]*1.05])
        else:
            note = None
        
        return note
    
    
    def match_note(self, note):
        # Identify note closest to first harmonic
        ratios = note/self.all_notes
        closeness = np.abs(ratios - 1)
        indices = np.where(closeness == np.min(closeness))
        
        note_str = self.note_list[indices[0][0]]
        
        # Detect whether note is higher or lower then target
        difference = (ratios[indices] - 1) * 100
        difference_str = ""
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
        

    def start(self, listen_time=120):
        start_time = time.time()
        print("Recording")
        try:
            while time.time() - start_time < listen_time:
                # Record using pyaudio
                audio_data = self.listen_pyaudio()
                
                # Compute average volume of audio_data
                avg_volume = np.mean(np.abs(audio_data))
                
                if avg_volume > self.volume_threshold:
                    # Normalize audio_data between -1 and 1
                    normalized_audio_data = audio_data / np.max(np.abs(audio_data))
                    
                    # Perform FFT and get signal spectrum
                    x, f = self.get_signal_spectrum(normalized_audio_data)
                    
                    # Identify note frequency
                    note = self.get_note_frequency(x, f)
                    
                    if note:
                        # Identify note closest to first harmonic
                        output_str = self.match_note(note)
                        
                        # Print note
                        # os.system("cls")
                        print(output_str)
                        
        except KeyboardInterrupt:
            print("\nTuner stopped by user.")
            
        finally:
            self.audio.terminate()
        
        
        
tuner = Tuner()
tuner.start(180)
        
        
        
        
        
        
        
        
        
        
        
