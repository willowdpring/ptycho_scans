# main.py
import tkinter as tk
from tkinter import ttk
import threading
from scan import Scan

class ImagingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XY Imaging Application")
        self.root.geometry("600x500")
        
        self.scan = Scan()
        self.scan_thread = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        stage_tab = ttk.Frame(notebook)
        camera_tab = ttk.Frame(notebook)
        scan_tab = ttk.Frame(notebook)
        
        notebook.add(stage_tab, text="Stage Control")
        notebook.add(camera_tab, text="Camera Control")
        notebook.add(scan_tab, text="Scan Setup")
        
        # Stage Control Tab
        self.setup_stage_tab(stage_tab)
        
        # Camera Control Tab
        self.setup_camera_tab(camera_tab)
        
        # Scan Setup Tab
        self.setup_scan_tab(scan_tab)
        
    def setup_stage_tab(self, parent):
        # X Stage Controls
        x_frame = ttk.LabelFrame(parent, text="X Stage")
        x_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(x_frame, text="Current Position:").grid(row=0, column=0, padx=5, pady=5)
        self.x_position_label = ttk.Label(x_frame, text="0.0")
        self.x_position_label.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(x_frame, text="Jog Distance:").grid(row=1, column=0, padx=5, pady=5)
        self.x_jog_distance = ttk.Entry(x_frame, width=10)
        self.x_jog_distance.insert(0, "1.0")
        self.x_jog_distance.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(x_frame, text="-", command=lambda: self.jog_stage('x', -1)).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(x_frame, text="+", command=lambda: self.jog_stage('x', 1)).grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(x_frame, text="Absolute Position:").grid(row=2, column=0, padx=5, pady=5)
        self.x_abs_position = ttk.Entry(x_frame, width=10)
        self.x_abs_position.insert(0, "0.0")
        self.x_abs_position.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(x_frame, text="Go To", command=lambda: self.move_absolute('x')).grid(row=2, column=2, padx=5, pady=5)
        
        # Y Stage Controls
        y_frame = ttk.LabelFrame(parent, text="Y Stage")
        y_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(y_frame, text="Current Position:").grid(row=0, column=0, padx=5, pady=5)
        self.y_position_label = ttk.Label(y_frame, text="0.0")
        self.y_position_label.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(y_frame, text="Jog Distance:").grid(row=1, column=0, padx=5, pady=5)
        self.y_jog_distance = ttk.Entry(y_frame, width=10)
        self.y_jog_distance.insert(0, "1.0")
        self.y_jog_distance.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(y_frame, text="-", command=lambda: self.jog_stage('y', -1)).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(y_frame, text="+", command=lambda: self.jog_stage('y', 1)).grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(y_frame, text="Absolute Position:").grid(row=2, column=0, padx=5, pady=5)
        self.y_abs_position = ttk.Entry(y_frame, width=10)
        self.y_abs_position.insert(0, "0.0")
        self.y_abs_position.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(y_frame, text="Go To", command=lambda: self.move_absolute('y')).grid(row=2, column=2, padx=5, pady=5)
        
    def setup_camera_tab(self, parent):
        camera_frame = ttk.LabelFrame(parent, text="Camera Settings")
        camera_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(camera_frame, text="Exposure (ms):").grid(row=0, column=0, padx=5, pady=5)
        self.exposure_entry = ttk.Entry(camera_frame, width=10)
        self.exposure_entry.insert(0, "100")
        self.exposure_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(camera_frame, text="Set", command=self.set_exposure).grid(row=0, column=2, padx=5, pady=5)
        
        # Status and manual capture
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x", padx=10, pady=20)
        
        ttk.Button(status_frame, text="Snap Image", command=self.snap_image).pack(padx=5, pady=5)
        self.image_status = ttk.Label(status_frame, text="No image captured")
        self.image_status.pack(padx=5, pady=5)
        
    def setup_scan_tab(self, parent):
        # Scan parameters frame
        param_frame = ttk.LabelFrame(parent, text="Scan Parameters")
        param_frame.pack(fill="x", padx=10, pady=5)
        
        # Number of steps
        ttk.Label(param_frame, text="Number of X steps:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_x_entry = ttk.Entry(param_frame, width=10)
        self.num_x_entry.insert(0, "5")
        self.num_x_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Number of Y steps:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.num_y_entry = ttk.Entry(param_frame, width=10)
        self.num_y_entry.insert(0, "5")
        self.num_y_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Resolution
        ttk.Label(param_frame, text="X Resolution:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.res_x_entry = ttk.Entry(param_frame, width=10)
        self.res_x_entry.insert(0, "1.0")
        self.res_x_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Y Resolution:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.res_y_entry = ttk.Entry(param_frame, width=10)
        self.res_y_entry.insert(0, "1.0")
        self.res_y_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Pattern selection
        self.pattern_var = tk.BooleanVar(value=True)
        pattern_frame = ttk.Frame(param_frame)
        pattern_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        ttk.Radiobutton(pattern_frame, text="Snake Pattern", variable=self.pattern_var, 
                        value=True).pack(side="left", padx=5)
        ttk.Radiobutton(pattern_frame, text="Ladder Pattern", variable=self.pattern_var, 
                        value=False).pack(side="left", padx=5)
        
        # Apply button
        ttk.Button(param_frame, text="Apply Settings", command=self.apply_scan_settings).grid(
            row=5, column=0, columnspan=2, padx=5, pady=10)
        
        # Control frame
        control_frame = ttk.LabelFrame(parent, text="Scan Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Start Scan", command=self.start_scan)
        self.start_button.grid(row=0, column=0, padx=5, pady=10)
        
        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_scan, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=5, pady=10)
        
        self.resume_button = ttk.Button(control_frame, text="Resume", command=self.resume_scan, state="disabled")
        self.resume_button.grid(row=0, column=2, padx=5, pady=10)
        
        self.cancel_button = ttk.Button(control_frame, text="Cancel", command=self.cancel_scan, state="disabled")
        self.cancel_button.grid(row=0, column=3, padx=5, pady=10)
        
        # Status frame
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.scan_status = ttk.Label(status_frame, text="Ready")
        self.scan_status.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(status_frame, text="Progress:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, length=200)
        self.progress_bar.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
    def jog_stage(self, stage, direction):
        try:
            if stage == 'x':
                distance = float(self.x_jog_distance.get()) * direction
                new_pos = self.scan.x_stage.jog(distance)
                self.x_position_label.config(text=f"{new_pos:.2f}")
            else:  # stage == 'y'
                distance = float(self.y_jog_distance.get()) * direction
                new_pos = self.scan.y_stage.jog(distance)
                self.y_position_label.config(text=f"{new_pos:.2f}")
        except ValueError:
            print("Please enter a valid number for jog distance")
    
    def move_absolute(self, stage):
        try:
            if stage == 'x':
                position = float(self.x_abs_position.get())
                new_pos = self.scan.x_stage.set_position(position)
                self.x_position_label.config(text=f"{new_pos:.2f}")
            else:  # stage == 'y'
                position = float(self.y_abs_position.get())
                new_pos = self.scan.y_stage.set_position(position)
                self.y_position_label.config(text=f"{new_pos:.2f}")
        except ValueError:
            print("Please enter a valid number for position")
    
    def set_exposure(self):
        try:
            exposure = int(self.exposure_entry.get())
            self.scan.camera.set_exposure(exposure)
        except ValueError:
            print("Please enter a valid integer for exposure")
    
    def snap_image(self):
        image_data = self.scan.camera.snap_image()
        self.image_status.config(text=f"Captured: {image_data}")
    
    def apply_scan_settings(self):
        try:
            num_x = int(self.num_x_entry.get())
            num_y = int(self.num_y_entry.get())
            res_x = float(self.res_x_entry.get())
            res_y = float(self.res_y_entry.get())
            pattern = self.pattern_var.get()
            
            self.scan.setup_scan(num_x, num_y, res_x, res_y, pattern)
            self.scan_status.config(text="Settings applied")
        except ValueError:
            self.scan_status.config(text="Invalid parameters")
    
    def start_scan(self):
        if self.scan_thread and self.scan_thread.is_alive():
            return
            
        self.scan.reset_scan()
        self.scan_thread = threading.Thread(target=self._run_scan)
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.cancel_button.config(state="normal")
        self.resume_button.config(state="disabled")
        self.scan_status.config(text="Scanning...")
    
    def _run_scan(self):
        total_points = self.scan.num_x * self.scan.num_y
        
        self.scan.start_scan()
        
        # Update UI when scan is complete
        if not self.scan.is_running:
            self.root.after(0, self._update_ui_after_scan)
    
    def _update_ui_after_scan(self):
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.resume_button.config(state="disabled")
        self.cancel_button.config(state="disabled")
        self.scan_status.config(text="Scan completed")
        self.progress_var.set(100)
    
    def pause_scan(self):
        self.scan.pause_scan()
        self.pause_button.config(state="disabled")
        self.resume_button.config(state="normal")
        self.scan_status.config(text="Paused")
    
    def resume_scan(self):
        self.scan.resume_scan()
        self.pause_button.config(state="normal")
        self.resume_button.config(state="disabled")
        self.scan_status.config(text="Scanning...")
    
    def cancel_scan(self):
        self.scan.cancel_scan()
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.resume_button.config(state="disabled")
        self.cancel_button.config(state="disabled")
        self.scan_status.config(text="Canceled")
        self.progress_var.set(0)
    
    def update_progress(self):
        if self.scan.is_running:
            current = self.scan.current_y * self.scan.num_x + self.scan.current_x
            total = self.scan.num_x * self.scan.num_y
            progress = (current / total) * 100
            self.progress_var.set(progress)
            
            # Schedule the next update
            self.root.after(100, self.update_progress)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImagingApp(root)
    root.after(100, app.update_progress)  # Start progress updates
    root.mainloop()