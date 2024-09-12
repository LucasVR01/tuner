import numpy as np
import pandas as pd
import pyaudio
import time
from tqdm import tqdm

class Tuner:
    def __init__(self, record_seconds=1, chunk=1024, rate=44100, volume_threshold=100, magnitude_threshold=1000):
        self.record_seconds = record_seconds
        self.chunk = chunk
        self.rate = rate
        self.volume_threshold = volume_threshold
        self.magnitude_threshold = magnitude_threshold
        self.audio = None
        self.all_notes, self.note_list = self._load_notes_frequencies_csv()
        self.running = False
        
    
    def _load_notes_frequencies_csv(self):
        df = pd.read_csv('notes_frequencies.csv') 
        note_list = df.iloc[:, 0].to_list()
        all_notes = df.iloc[:, 1:].to_numpy()
        return all_notes, note_list
        
    
    def _listen_pyaudio(self):
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
    
    
    def _get_signal_spectrum(self, audio_data):
        # Perform FFT
        n = len(audio_data)
        audio_data_fft = np.abs(np.fft.fft(audio_data))
        frequencies = np.fft.fftfreq(n, 1/self.rate)
        audio_fft = audio_data_fft[0:n//2]
        freq = frequencies[0:n//2]
        
        # Trim signal
        aux = freq <= 5000
        f = freq[aux]
        x = audio_fft[aux]
        
        return x, f
    
    
    def _get_note_frequency(self, x, f):
        if np.max(x) > self.magnitude_threshold:
            ft = f[x >= self.magnitude_threshold]        # frequencies higher than threshold
            ft_gp1 = ft[ft < ft[0]*1.05]                 # frequencies close to first harmonic (first group)
            idx_gp1 = np.where(np.isin(f, ft_gp1))[0]    # indices of frequencies in the first group
            x_max_gp1 = np.max(x[idx_gp1])               # maximum value of x within the first group
            note = f[x == x_max_gp1]                     # frequency of the maximum value of x in the first group
        else:
            note = None
        
        return note
    
    
    def _match_note(self, note, dif=True):
        # Identify note closest to first harmonic
        ratios = note/self.all_notes
        closeness = np.abs(ratios - 1)
        indices = np.where(closeness == np.min(closeness))
        
        note_str = self.note_list[indices[0][0]]
        
        if dif:
            # Detect whether note is higher or lower than target
            difference = (ratios[indices] - 1) * 100
            percentage = 50 + (difference / 2.973) * 50  # Normalize to a 0-100 scale
                
            return note_str, float(max(0, min(100, percentage)))
        else:
            return note_str, 50
        

    def start(self, listen_time=float('inf'), callback=None, dif=True):
        self.running = True
        self.audio = pyaudio.PyAudio()
        start_time = time.time()
        print("Tuner started: Recording...")
        
        if not callback:
            progress_bar = tqdm(total=100, desc="", bar_format='{desc} |{bar}|')

        try:
            while self.running and time.time() - start_time < listen_time:
                # Record using pyaudio
                audio_data = self._listen_pyaudio()
                
                # Compute average volume of audio_data
                avg_volume = np.mean(np.abs(audio_data))
                
                if avg_volume > self.volume_threshold:
                    # Normalize audio_data between -1 and 1
                    normalized_audio_data = audio_data / np.max(np.abs(audio_data))
                    
                    # Perform FFT and get signal spectrum
                    x, f = self._get_signal_spectrum(normalized_audio_data)
                    
                    # Identify note frequency
                    note = self._get_note_frequency(x, f)
                    
                    if note:
                        # Identify note closest to first harmonic
                        note_str, percentage = self._match_note(note, dif)
                        
                        if callback:
                            # Send the note to the GUI via the callback
                            callback((note_str, percentage))
                        else:
                            # Display progress bar with note
                            progress_bar.n = percentage
                            progress_bar.set_description(note_str if len(note_str) == 2 else note_str + " ")
                            progress_bar.refresh()
                            
            print("\nTuner stopped." if not callback else "Tuner stopped.")
                        
        except KeyboardInterrupt:
            print("\nTuner stopped by user.")
            
        finally:
            if not callback:
                progress_bar.close()
            
            self.audio.terminate()
            
            
    def stop(self):
        self.running = False
            
            
        
        
if __name__ == "__main__":      
    tuner = Tuner()
    tuner.start(100)
        
        
        
        
        
        
        
        
        
        
        
