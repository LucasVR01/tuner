import numpy as np
import pandas as pd
import pyaudio
import time
from tqdm import tqdm
import os

class Tuner:
    def __init__(self, record_seconds=1, chunk=1024, rate=44100, volume_threshold=100, magnitude_threshold=1000):
        """
        Initializes the Tuner object with parameters for recording, processing audio, and detecting notes.
        
        Parameters:
        - record_seconds (int): Time in seconds to record audio.
        - chunk (int): Size of each audio chunk.
        - rate (int): Sampling rate of the audio.
        - volume_threshold (int): Threshold to determine if the sound is loud enough to process.
        - magnitude_threshold (int): Threshold for frequency magnitude to detect a valid note.
        """
        self.record_seconds = record_seconds
        self.chunk = chunk
        self.rate = rate
        self.volume_threshold = volume_threshold
        self.magnitude_threshold = magnitude_threshold
        self.audio = None
        self.all_notes, self.note_list = self._load_notes_frequencies_csv()
        self.running = False
        
    
    def _load_notes_frequencies_csv(self):
        """
        Loads a CSV file containing note frequencies and returns them as NumPy arrays.
        
        Returns:
        - all_notes (numpy.ndarray): Array of note frequencies.
        - note_list (list): List of note names.
        """
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(base_dir, 'data', 'notes_frequencies.csv')
        df = pd.read_csv(data_path)
        note_list = df.iloc[:, 0].to_list()
        all_notes = df.iloc[:, 1:].to_numpy()
        return all_notes, note_list
        
    
    def _listen_pyaudio(self):
        """
        Listens to audio input using PyAudio and returns the audio data as a NumPy array.
        
        Returns:
        - audio_data (numpy.ndarray): Raw audio data.
        """
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
    
        # Open PyAudio stream for recording
        stream = self.audio.open(format=FORMAT,
                                 channels=CHANNELS,
                                 rate=self.rate,
                                 input=True,
                                 frames_per_buffer=self.chunk)
    
        frames = []
        # Record audio for the specified time
        for _ in range(int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            frames.append(np.frombuffer(data, dtype=np.int16))
    
        # Close stream
        stream.stop_stream()
        stream.close()

        # Concatenate frames to form the full audio signal
        audio_data = np.concatenate(frames)
        return audio_data
    
    
    def _get_signal_spectrum(self, audio_data):
        """
        Computes the FFT of the audio data and returns the signal spectrum.
        
        Parameters:
        - audio_data (numpy.ndarray): The audio data to process.
        
        Returns:
        - x (numpy.ndarray): The magnitude of the FFT.
        - f (numpy.ndarray): The corresponding frequency bins.
        """
        n = len(audio_data)
        audio_data_fft = np.abs(np.fft.fft(audio_data)) # Compute FFT
        frequencies = np.fft.fftfreq(n, 1/self.rate) # Get frequency bins
        audio_fft = audio_data_fft[0:n//2] # Only take positive frequencies
        freq = frequencies[0:n//2]
        
        # Trim the signal for frequencies below 5000 Hz
        aux = freq <= 5000
        f = freq[aux]
        x = audio_fft[aux]
        
        return x, f
    
    
    def _get_note_frequency(self, x, f):
        """
        Detects the frequency of the note in the audio signal based on the FFT result.
        
        Parameters:
        - x (numpy.ndarray): The FFT magnitude.
        - f (numpy.ndarray): The frequency bins corresponding to the FFT result.
        
        Returns:
        - note (float or None): The frequency of the detected note, or None if no note is detected.
        """
        if np.max(x) > self.magnitude_threshold:
            ft = f[x >= self.magnitude_threshold] # Frequencies higher than threshold
            ft_gp1 = ft[ft < ft[0]*1.05] # Frequencies close to first harmonic (first group)
            idx_gp1 = np.where(np.isin(f, ft_gp1))[0] # Indices of frequencies in the first group
            x_max_gp1 = np.max(x[idx_gp1]) # Maximum value of x within the first group
            note = f[x == x_max_gp1] # Frequency of the maximum value of x in the first group
        else:
            note = None
        
        return note
    
    
    def _match_note(self, note, dif=True):
        """
        Matches the detected note frequency to the closest standard musical note.
        
        Parameters:
        - note (float): The frequency of the detected note.
        - dif (bool): Whether to return the percentage difference (True) or just the note (False).
        
        Returns:
        - note_str (str): The musical name of the closest note.
        - percentage (float): The tuning percentage (for dif=True).
        """
        ratios = note / self.all_notes # Calculate frequency ratios
        closeness = np.abs(ratios - 1) # Find the closest frequency
        indices = np.where(closeness == np.min(closeness)) # Index of the closest note
        
        note_str = self.note_list[indices[0][0]] # Musical note name
        
        if dif:
            # Calculate the percentage difference from the target note
            difference = (ratios[indices] - 1) * 100
            percentage = 50 + (difference / 2.973) * 50  # Normalize to a 0-100 scale
            return note_str, float(max(0, min(100, percentage))) # Return note and percentage
        else:
            return note_str, 50 # Return 50% if not calculating the difference
        

    def start(self, listen_time=float('inf'), callback=None, dif=True):
        """
        Starts the tuner and continuously listens for notes. It processes audio data and either updates
        the GUI through the callback or shows a progress bar.
        
        Parameters:
        - listen_time (float): How long to listen for (in seconds).
        - callback (function): A callback function to send the detected note to the GUI.
        - dif (bool): Whether to calculate the difference from the target note.
        """
        self.running = True
        self.audio = pyaudio.PyAudio()
        start_time = time.time()
        print("Tuner started: Recording...")
        
        if not callback:
            progress_bar = tqdm(total=100, desc="", bar_format='{desc} |{bar}|')

        try:
            while self.running and time.time() - start_time < listen_time:
                audio_data = self._listen_pyaudio() # Record using pyaudio
                
                avg_volume = np.mean(np.abs(audio_data)) # Calculate average volume of audio_data
                
                if avg_volume > self.volume_threshold:
                    normalized_audio_data = audio_data / np.max(np.abs(audio_data)) # Normalize audio_data between -1 and 1
                    
                    x, f = self._get_signal_spectrum(normalized_audio_data) # Perform FFT and get frequency spectrum
                    
                    note = self._get_note_frequency(x, f) # Get the detected note
                    
                    if note:
                        note_str, percentage = self._match_note(note, dif) # Match to closest note
                        
                        if callback:
                            callback((note_str, percentage)) # Send to GUI
                        else:
                            # Display progress and note
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
        """
        Stops the tuner from recording.
        """
        self.running = False
            
                
if __name__ == "__main__":      
    tuner = Tuner()
    tuner.start(10)