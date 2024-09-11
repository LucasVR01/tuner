import ctypes
import tkinter as tk
from tkinter import ttk
from threading import Thread
from Tuner import Tuner

class Tuner_GUI:
    def __init__(self, tuner):
        self.tuner = tuner
        self.is_running = False
        
        # Adjust the resolution
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        
        # Initialize tkinter
        self.root = tk.Tk()
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
        
        # Label to display the detected note
        self.note_label = tk.Label(self.root, text="", font=("Helvetica", 20, "bold"),
                                   anchor="center", justify="center")
        self.note_label.pack(pady=20)
        
        # Progress bar to show tuning status
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10)
        self.progress["maximum"] = 100  # Progress bar range from 0 to 100
        
        
        # Bind the close window event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        
    def _start_tuner(self):
        # Disable the start button and enable the stop button
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        self.is_running = True
        
        # Start the tuner in a new thread
        self.tuner_thread = Thread(target=self.tuner.start, args=(float('inf'), self._update_note_label, True))
        self.tuner_thread.daemon = True
        self.tuner_thread.start()
        
        
    def _stop_tuner(self):
        # Disable the stop button and enable the start button
        self.stop_button.config(state="disabled")
        self.start_button.config(state="normal")
        
        self.is_running = False
        
        # Stop the tuner in a separate thread to avoid blocking the GUI
        self.stop_thread = Thread(target=self.__stop_tuner_thread)
        self.stop_thread.daemon = True
        self.stop_thread.start()
        
        
    def __stop_tuner_thread(self):
        # This method will run in a separate thread to avoid GUI lag
        self.tuner.stop()

        # Wait for the tuner thread to finish
        self.tuner_thread.join()

        # Update label and progress bar in the main thread after the tuner is stopped
        self.root.after(0, self._reset_gui)
        
        
    def _reset_gui(self):
        # Reset the GUI after the tuner stops
        self.note_label.config(text="")
        self.progress["value"] = 0

        
    def _on_closing(self):
        if self.is_running:
            self._stop_tuner()
            
        if self.tuner_thread and self.tuner_thread.is_alive():
            self.tuner_thread.join(timeout=1)  # Wait for the thread to terminate safely

        self.root.destroy()
        
        
    def _update_note_label(self, note_info):
        note, percentage = note_info
        self.note_label.config(text=f"{note}")
        self.progress["value"] = percentage
            
        
    def run(self):
        self.root.mainloop()
    
    
if __name__ == "__main__":
    tuner = Tuner()
    gui = Tuner_GUI(tuner)
    gui.run()
        

