import ctypes
import tkinter as tk
from threading import Thread




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

        self.is_running = False
        
        self.root.mainloop()
        
        
    def start_tuner(self):
        print("Tuner started")
        
    def stop_tuner(self):
        print("Tuner stopped")
        
        
gui = Tuner_GUI(1)
        

