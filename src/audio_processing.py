import numpy as np
import pandas as pd
import pyaudio
import os

class AudioCapture:
    def __init__(self, record_seconds=1, chunk=1024, rate=44100):
        """
        Initializes the AudioCapture object.
        
        Parameters:
        - record_seconds (int): Duration to record for each sample.
        - chunk (int): Size of each audio chunk.
        - rate (int): Sampling rate of the audio.
        """
        self.record_seconds = record_seconds
        self.chunk = chunk
        self.rate = rate
        self.audio = pyaudio.PyAudio()


    def start(self):
        """
        Captures audio data from the microphone and returns it as a NumPy array.
        
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
    

    def close(self):
        """Close the audio stream."""
        self.audio.terminate()



class SignalProcessor:
    def __init__(self, rate=44100, volume_threshold=100, magnitude_threshold=1000):
        """
        Initializes the SignalProcessor object

        Parameters:
        - rate (int): Sampling rate of the audio.
        - volume_threshold (int): Threshold to determine if the sound is loud enough to process.
        - magnitude_threshold (int): Threshold for frequency magnitude to detect a valid note.
        """
        self.rate = rate
        self.volume_threshold = volume_threshold
        self.magnitude_threshold = magnitude_threshold
        self.all_notes, self.note_list = self._load_notes_frequencies_csv()


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


    def get_signal_spectrum(self, audio_data):
        """
        Computes the FFT of the audio data and returns the signal spectrum.

        Parameters:
        - audio_data (numpy.ndarray): The audio data to process.
        
        Returns:
        - x (numpy.ndarray): The magnitude of the FFT.
        - f (numpy.ndarray): The corresponding frequency bins.
        """
        n = len(audio_data)
        normalized_audio_data = audio_data / np.max(np.abs(audio_data)) # Normalize audio_data between -1 and 1
        audio_data_fft = np.abs(np.fft.fft(normalized_audio_data)) # Compute FFT
        frequencies = np.fft.fftfreq(n, 1/self.rate) # Get frequency bins
        audio_fft = audio_data_fft[0:n//2] # Only take positive frequencies
        freq = frequencies[0:n//2]
        
        # Trim the signal for frequencies below 5000 Hz
        aux = freq <= 5000
        x = audio_fft[aux]
        f = freq[aux]
        
        return x, f
    

    def get_note_frequency(self, x, f):
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
    

    def match_note(self, note, dif=True):
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
        
    
    def check_volume(self, audio_data):
        """
        Checks if signal volume is high enough for note detection

        Parameters: 
        - audio_data (numpy.ndarray): The audio data to process.

        Returns:
        - bool: Whether the volume is above the threshold or not
        """
        avg_volume = np.mean(np.abs(audio_data)) # Calculate average volume of audio_data
        return True if avg_volume > self.volume_threshold else False
    

    def run(self, audio_data, dif=True):
        """
        Runs all analyses at once

        Parameters: 
        - audio_data (numpy.ndarray): The audio data to process.
        - dif (bool): Whether to calculate the difference from the target note.
        """
        if self.check_volume(audio_data): # Check if volume is high enough
            x, f = self.get_signal_spectrum(audio_data) # Perform FFT and get frequency spectrum
            note = self.get_note_frequency(x, f) # Get the detected note
            if note: # Check if a note was detected
                note_str, percentage = self.match_note(note, dif) # Match to closest note
                return note_str, percentage
            else:
                return None, None
        else:
            return None, None
        





