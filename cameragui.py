import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import time
from camera import Camera

class CameraGUI:
    def __init__(self, master, camera, reconnects=False):
        self.master = master

        self.camera = camera
        if reconnects:
            # Serial number input field and connection button
            self.serial_label = tk.Label(master, text="Serial Number:")
            self.serial_label.grid(row=0, column=0, padx=10, pady=10)
            
            self.serial_entry = tk.Entry(master)
            self.serial_entry.grid(row=0, column=1, padx=10, pady=10)
            
            self.connect_button = tk.Button(master, text="Connect", command=self.connect_camera)
            self.connect_button.grid(row=0, column=2, padx=10, pady=10)

        # Exposure controls
        self.exposure_label = tk.Label(master, text="Exposure (ms):")
        self.exposure_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.exposure_entry = tk.Entry(master)
        self.exposure_entry.insert(0, str(self.camera.exposure))  # Default exposure value
        self.exposure_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.set_exposure_button = tk.Button(master, text="Set Exposure", command=self.set_exposure)
        self.set_exposure_button.grid(row=1, column=2, padx=10, pady=10)

        # Frame display label and the grab frame button in the same row
        self.frame_label = tk.Label(master, text="Grabbed Frame:")
        self.frame_label.grid(row=2, column=0, padx=10, pady=10)

        self.snap_button = tk.Button(master, text="Grab Frame", command=self.grab_frame)
        self.snap_button.grid(row=2, column=1, padx=10, pady=10)  # Move the button to the left of the label

        self.canvas = tk.Canvas(master, width=640, height=480)
        self.canvas.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def connect_camera(self):
        """Connect to the camera using the serial number."""
        serial_number = self.serial_entry.get()
        
        if not serial_number:
            messagebox.showerror("Error", "Please enter a serial number.")
            return
        
        self.camera.serial_number = serial_number
        self.camera._connect_camera()
        
        if self.camera.camera:
            messagebox.showinfo("Success", f"Connected to camera {self.camera.serial_number}.")
        else:
            messagebox.showerror("Connection Failed", "Failed to connect to camera.")
    
    def set_exposure(self):
        """Set the exposure time for the camera."""
        try:
            exposure_ms = int(self.exposure_entry.get())
            self.camera.set_exposure(exposure_ms)
            messagebox.showinfo("Exposure Set", f"Exposure set to {exposure_ms} ms.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for exposure.")


    def grab_frame(self):
        """Grab and display a frame from the camera."""
        frame = self.camera.snap_image()
        
        if isinstance(frame, str):  # In case of a simulated image
            messagebox.showinfo("Simulated Image", f"Simulated image: {frame}")
            return
        
        # Convert the frame to RGB (OpenCV uses BGR by default)
        if frame.shape[2] == 1:  # If the frame is grayscale
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        # Convert to ImageTk format for displaying in Tkinter
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img)

        # Update the canvas with the new image
        self.canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
        self.canvas.image = img_tk  # Keep a reference to avoid garbage collection


if __name__ == "__main__":
    # Create the Camera instance
    camera = Camera(serial_number=None)  # Start in simulation mode for testing

    # Create the Tkinter window
    root = tk.Tk()

    # Create the CameraGUI
    gui = CameraGUI(root, camera, reconnects=True)

    # Start the Tkinter main loop
    root.mainloop()