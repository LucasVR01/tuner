import tkinter as tk
from tkinter import ttk
from threading import Thread
from .tuner import Tuner

class Tuner_GUI:
    def __init__(self, tuner):
        """
        Initializes the GUI for the tuner application.
        
        Parameters:
        - tuner (Tuner): The Tuner object to use for note detection.
        """
        self.tuner = tuner
        self.is_running = False
        self.is_closing = False
        
        # Initialize tkinter
        self.root = tk.Tk()
        self.root.tk.call('tk', 'scaling', 2.0)
        self.root.title("Tuner")
        self.root.geometry("300x200")
        self.root.eval('tk::PlaceWindow . center')
        
        # Create a frame to hold the buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Create start button
        self.start_button = tk.Button(button_frame, text="Start Tuner", bg="green", 
                                      fg="white", font=("Helvetica", 10, "bold"), 
                                      activebackground="green", activeforeground="white",
                                      command=self._start_tuner,)
        self.start_button.pack(side="left", padx=5)

        # Create stop button
        self.stop_button = tk.Button(button_frame, text="Stop Tuner", bg="red", 
                                     fg="white", font=("Helvetica", 10, "bold"), 
                                     activebackground="red", activeforeground="white",
                                     command=self._stop_tuner,)
        self.stop_button.pack(side="left", padx=5)
        self.stop_button.config(state="disabled")
        
        # Label to display the detected musical note
        self.note_label = tk.Label(self.root, text="", font=("Helvetica", 20, "bold"),
                                   anchor="center", justify="center")
        self.note_label.pack(pady=20)
        
        # Progress bar to show how far the detected note is from being in tune
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10)
        self.progress["maximum"] = 100
        
        # Bind the close window event to handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        
    def _start_tuner(self):
        """
        Starts the tuner by enabling the stop button and disabling the start button.
        It also launches the tuner in a separate thread.
        """
        self.start_button.config(state="disabled") # Disable the start button
        self.stop_button.config(state="normal") # Enable the stop button
        
        self.is_running = True # Indicate that the tuner is running
        
        # Start the tuner in a new thread
        self.tuner_thread = Thread(target=self.tuner.start, args=(float('inf'), self._update_note_label, True))
        self.tuner_thread.daemon = True
        self.tuner_thread.start()
        
        
    def _stop_tuner(self):
        """
        Stops the tuner by disabling the stop button, enabling the start button, 
        and stopping the tuner in a separate thread.
        """
        self.stop_button.config(state="disabled") # Disable stop button
        self.start_button.config(state="normal") # Enable the start button
        
        self.is_running = False # Indicate that the tuner is not running
        
        # Stop the tuner in a separate thread to avoid blocking the GUI
        self.stop_thread = Thread(target=self._stop_tuner_thread)
        self.stop_thread.daemon = True
        self.stop_thread.start()
        
        # Reset GUI after 1000 ms
        self.root.after(1000, self._reset_gui)
        
        
    def _stop_tuner_thread(self):
        """
        Stops the tuner in a separate thread and ensures the tuner thread is joined.
        """
        self.tuner.stop()
        self.tuner_thread.join(timeout=1)
        
        
    def _reset_gui(self):
        """
        Resets the GUI elements (note label and progress bar) after the tuner is stopped.
        """
        if self.root:
            self.note_label.config(text="") # Clear the note label
            self.progress["value"] = 0 # Reset the progress bar
        
        
    def _update_note_label(self, note_info):
        """
        Updates the note label and progress bar with the detected note info.
        This method is run on a separate thread, so it schedules the update on the main thread.
        
        Parameters:
        - note_info (tuple): A tuple containing the note name and the percentage progress.
        """
        if not self.is_closing and self.root.winfo_exists():
            # Schedule the update on the main thread
            self.root.after(0, self._main_update_note_label, note_info)    
        
        
    def _main_update_note_label(self, note_info):
        """
        Main method to update the GUI components (note label and progress bar).
        
        Parameters:
        - note_info (tuple): A tuple containing the note name and the percentage progress.
        """
        # Update the note being played in the window
        note, percentage = note_info
        self.note_label.config(text=f"{note}") # Display the detected note
        self.progress["value"] = percentage # Update the progress bar
        
        
    def _on_closing(self):
        """
        Handles the close window event, stops the tuner if running, and ensures cleanup.
        """
        if not self.is_closing:
            self.is_closing = True # Prevent multiple close actions
            
            # Stop tuner if it's running
            if self.is_running:
                self._stop_tuner()
                self.stop_thread.join(timeout=1) # Wait for the stop thread to finish
            
            # Close window
            if self.root:
                self.root.destroy()
        
        
    def run(self):
        """
        Starts the main event loop for the tkinter GUI.
        Catches exceptions and handles cleanup on window close.
        """
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Tuner GUI interrupted by user.")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            # Ensure that resources are cleaned up
            self._on_closing()
    