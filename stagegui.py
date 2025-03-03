
import tkinter as tk
from tkinter import messagebox
from stage import Stage
import tkinter as tk
from tkinter import messagebox

class StageGUI:
    def __init__(self, master, stage):
        self.master = master
        self.stage = stage
        """        
        # Serial number input field and connection button
        self.serial_label = tk.Label(master, text="Serial Number:")
        self.serial_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.serial_entry = tk.Entry(master)
        self.serial_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.connect_button = tk.Button(master, text="Connect", command=self.connect_stage)
        self.connect_button.grid(row=0, column=2, padx=10, pady=10)
        """
        # Position display
        self.position_label = tk.Label(master, text=f"Position: {self.stage.position}")
        self.position_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        
        # Jog buttons (move stage)
        self.jog_label = tk.Label(master, text="Jog Position (mm):")
        self.jog_label.grid(row=2, column=0, padx=10, pady=10)
        
        self.jog_entry = tk.Entry(master)
        self.jog_entry.grid(row=2, column=1, padx=10, pady=10)
        
        self.jog_button = tk.Button(master, text="Jog", command=self.jog_stage)
        self.jog_button.grid(row=2, column=2, padx=10, pady=10)
        
        # Move to absolute position section
        self.move_to_label = tk.Label(master, text="Move to Position (mm):")
        self.move_to_label.grid(row=3, column=0, padx=10, pady=10)
        
        self.move_to_entry = tk.Entry(master)
        self.move_to_entry.grid(row=3, column=1, padx=10, pady=10)
        
        self.move_to_button = tk.Button(master, text="Move To", command=self.move_to_stage)
        self.move_to_button.grid(row=3, column=2, padx=10, pady=10)
        
        # Zero and Go to Zero buttons
        self.zero_button = tk.Button(master, text="Set Zero", command=self.set_zero_stage)
        self.zero_button.grid(row=4, column=0, padx=10, pady=10)
        
        self.goto_zero_button = tk.Button(master, text="Go to Zero", command=self.goto_zero_stage)
        self.goto_zero_button.grid(row=4, column=1, padx=10, pady=10)
        
    def connect_stage(self):
        """Attempt to connect the stage using the serial number provided."""
        serial_number = self.serial_entry.get()
        
        if not serial_number:
            messagebox.showerror("Error", "Please enter a serial number.")
            return
        
        # Connect to the stage
        self.stage.serial_number = serial_number
        self.stage._connect_stage()
        
        if self.stage.translator:
            self.position_label.config(text=f"Position: {self.stage.position}")
            messagebox.showinfo("Success", f"Connected to stage {self.stage.name}.")
        else:
            messagebox.showerror("Connection Failed", "Failed to connect to stage.")
    
    def jog_stage(self):
        """Jog the stage by a relative distance."""
        try:
            distance = float(self.jog_entry.get())
            new_position = self.stage.move_by(distance)
            self.position_label.config(text=f"Position: {new_position}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the jog distance.")
    
    def move_to_stage(self):
        """Move the stage to a specific absolute position."""
        try:
            target_position = float(self.move_to_entry.get())
            new_position = self.stage.move_to(target_position)
            self.position_label.config(text=f"Position: {new_position}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the target position.")
    
    def set_zero_stage(self):
        """Set the current position as zero."""
        self.stage.set_zero()
        messagebox.showinfo("Zeroed", "Stage position has been zeroed.")
    
    def goto_zero_stage(self):
        """Move the stage to the zeroed position."""
        new_position = self.stage.move_to(self.stage.zero_pos)
        self.position_label.config(text=f"Position: {new_position}")
        messagebox.showinfo("Moved to Zero", "Stage moved to zero position.")


if __name__ == "__main__":
    # Create the Stage instance
    stage = Stage(name="TestStage")

    # Create the Tkinter window
    root = tk.Tk()

    # Create the StageGUI
    gui = StageGUI(root, stage)

    # Start the Tkinter main loop
    root.mainloop()
    