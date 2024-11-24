import pyaudio
import time
from tqdm import tqdm
from .audio_processing import AudioCapture, SignalProcessor

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
        self.is_running = False
        self.audio_capture = AudioCapture(record_seconds=record_seconds, chunk=chunk, rate=rate)
        self.signal_processor = SignalProcessor(rate=rate, volume_threshold=volume_threshold, magnitude_threshold=magnitude_threshold)
        

    def start(self, listen_time=float('inf'), callback=None, dif=True):
        """
        Starts the tuner and continuously listens for notes. It processes audio data and either updates
        the GUI through the callback or shows a progress bar.
        
        Parameters:
        - listen_time (float): How long to listen for (in seconds).
        - callback (function): A callback function to send the detected note to the GUI.
        - dif (bool): Whether to calculate the difference from the target note.
        """
        self.is_running = True
        self.audio = pyaudio.PyAudio()
        start_time = time.time()
        print("Tuner started: Recording...")
        
        if not callback:
            progress_bar = tqdm(total=100, desc="", bar_format='{desc} |{bar}|')

        try:
            while self.is_running and time.time() - start_time < listen_time:
                audio_data = self.audio_capture.start() # Record using pyaudio
                note_str, percentage = self.signal_processor.run(audio_data, dif) # Process signal to get name of the played note and the percentage of the progress bar
                    
                if note_str:
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
            
            self.audio_capture.close()
            
            
    def stop(self):
        """
        Stops the tuner from recording.
        """
        self.is_running = False
            
