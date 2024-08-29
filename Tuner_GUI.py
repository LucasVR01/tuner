import ctypes
import tkinter as tk
from threading import Thread
from Tuner_Class import Tuner



class Tuner_GUI:
    def __init__(self, tuner):
        self.tuner = tuner
        
        # Adjust the resolution
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        
        # Initialize tkinter
        self.root = tk.Tk()
        self.root.title("Tuner")
        self.root.geometry("300x200")
        
        # Create a frame to hold the buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Create start button
        self.start_button = tk.Button(button_frame, text="Start Tuner", bg="green", 
                                      fg="white", font=("Helvetica", 10, "bold"), 
                                      activebackground="green", activeforeground="white",
                                      command=self.start_tuner,)
        self.start_button.pack(side="left", padx=5)

        # Create stop button
        self.stop_button = tk.Button(button_frame, text="Stop Tuner", bg="red", 
                                     fg="white", font=("Helvetica", 10, "bold"), 
                                     activebackground="red", activeforeground="white",
                                     command=self.stop_tuner,)
        self.stop_button.pack(side="left", padx=5)
        self.stop_button.config(state="disabled")

        self.is_running = False
        
        
    def start_tuner(self):
        # Disable the start button and enable the stop button
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start the tuner in a new thread
        print("Tuner started")
        self.tuner_thread = Thread(target=self.tuner.start, args=(120,))
        self.tuner_thread.start()
        
        
    def stop_tuner(self):
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # Stop the tuner
        self.tuner.stop()
        self.tuner_thread.join()
        
        
    def run(self):
        self.root.mainloop()
        
if __name__ == "__main__":
    tuner = Tuner()
    gui = Tuner_GUI(tuner)
    gui.run()
        

