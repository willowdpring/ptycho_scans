from stage import Stage
from camera import Camera
import time
import os
import datetime
import cv2

class Scan:
    def __init__(self, cam, x, y):
        self.camera = cam
        self.x_stage = x
        self.y_stage = y
        
        # Scan parameters
        self.num_x = 5  # Number of X positions
        self.num_y = 5  # Number of Y positions
        self.res_x = 1.0  # X resolution (step size)
        self.res_y = 1.0  # Y resolution (step size)
        self.snake_pattern = True  # True for snake, False for ladder
        
        # Image saving parameters
        self.save_folder = os.path.expanduser("~/scan_images")  # Default folder
        self.image_prefix = "scan_"  # Default prefix
        self.auto_save = True  # Auto-save by default
        self.overwrite = False  # Don't overwrite by default
        
        # State variables
        self.is_running = False
        self.is_paused = False
        self.current_image = 0
        
    def setup_scan(self, num_x, num_y, res_x, res_y, snake_pattern=True):
        """Configure the scan parameters"""
        self.num_x = num_x
        self.num_y = num_y
        self.res_x = res_x
        self.res_y = res_y
        self.snake_pattern = snake_pattern
        print(f"Scan configured: {num_x}x{num_y} grid with {res_x}x{res_y} resolution")
        print(f"Pattern: {'Snake' if snake_pattern else 'Ladder'}")
    
    def setup_saving(self, folder, prefix, auto_save=True, overwrite=False):
        """Configure image saving parameters"""
        # Use the folder provided rather than defaulting to ~/scan_images
        self.save_folder = folder
        self.image_prefix = prefix
        self.auto_save = auto_save
        self.overwrite = overwrite
        
        # Ensure the save folder exists
        if not os.path.exists(self.save_folder) and self.auto_save:
            try:
                os.makedirs(self.save_folder)
                print(f"Created save folder: {self.save_folder}")
            except Exception as e:
                print(f"Error creating save folder: {e}")
                return False
                
        print(f"Save configuration: Folder='{folder}', Prefix='{prefix}'")
        print(f"Auto-save: {'Enabled' if auto_save else 'Disabled'}, Overwrite: {'Enabled' if overwrite else 'Disabled'}")
        return True
    def start_scan(self):
        """Start or resume a scan"""
        self.is_running = True
        self.is_paused = False
        print("Scan started")
        self.scan_zero = (self.x_stage.position,self.y_stage.position)
        print(f"begining a scan from {self.scan_zero}")
        
        try:
            # Check save directory exists if auto-save is enabled
            if self.auto_save and not os.path.exists(self.save_folder):
                try:
                    os.makedirs(self.save_folder)
                    print(f"Created save folder: {self.save_folder}")
                except Exception as e:
                    print(f"Error creating save folder: {e}. Auto-save disabled.")
                    self.auto_save = False
            
            for i in range(self.num_x * self.num_y):
                if not self.is_running:
                    break
                    
                self.current_image = i
                if self.is_paused:
                    time.sleep(0.1)  # Small sleep to prevent CPU hogging while paused
                    continue
                
                target_y = self.scan_zero[1] +  (i//self.num_y) * self.res_y

                if self.snake_pattern and (i//self.num_y) % 2 == 1:
                    target_x = self.scan_zero[0] + (self.num_x - (1 + (i % self.num_x))) * self.res_x
                else:
                    target_x = self.scan_zero[0] + (i % self.num_x) * self.res_x

                self.x_stage.move_to(target_x)
                self.y_stage.move_to(target_y)

                # Take image at current position
                print(f"Scanning position ({target_x}, {target_y})")
                image = self.camera.snap_image()

                # Save image with position information
                self._save_image(image, i, target_x, target_y)

                # Small delay to avoid overwhelming the hardware
                time.sleep(1)
                
            print("Scan completed")
            self.reset_scan()
            
        except Exception as e:
            print(f"Error during scan: {e}")
            self.is_running = False
            
    def pause_scan(self):
        """Pause the ongoing scan"""
        self.is_paused = True
        print("Scan paused")
        
    def resume_scan(self):
        """Resume a paused scan"""
        self.is_paused = False
        print("Scan resumed")
        
    def cancel_scan(self):
        """Cancel the current scan"""
        self.is_running = False
        self.reset_scan()
        print("Scan canceled")
        
    def reset_scan(self):
        """Reset scan position to beginning"""
        if self.x_stage:
            self.x_stage.move_to(self.scan_zero[0])
        if self.y_stage:
            self.y_stage.move_to(self.scan_zero[1])
        self.current_image = 0
        self.is_running = False
        self.is_paused = False
            
    def _save_image(self, image_data, index, x_pos, y_pos):
        """Save the image with position metadata
        
        Args:
            image_data: OpenCV (cv2) image data
            index: Image sequence number
            x_pos: X-axis position when image was taken
            y_pos: Y-axis position when image was taken
        
        Returns:
            filepath: Path to saved image or None if saving failed
        """
        if not self.auto_save:
            print(f"Image at position ({x_pos}, {y_pos}) not saved (auto-save disabled)")
            return None
            
        try:
            # Create filename with index
            filename = f"{self.image_prefix}{index:04d}.png"
            filepath = os.path.join(self.save_folder, filename)
            
            # Check if file exists and handle accordingly
            if os.path.exists(filepath) and not self.overwrite:
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{self.image_prefix}{index:04d}_{timestamp}.png"
                filepath = os.path.join(self.save_folder, filename)
                print(f"File already exists. Saving as {filename} instead")
            
            # Save the OpenCV image
            success = cv2.imwrite(filepath, image_data)
            
            if not success:
                print(f"Failed to save image to {filepath}")
                return None
                
            print(f"Saved image to {filepath}")
            
            # Add position metadata to a companion file
            metadata_path = filepath.replace('.png', '.txt')
            with open(metadata_path, 'w') as f:
                f.write(f"X Position: {x_pos}\n")
                f.write(f"Y Position: {y_pos}\n")
                f.write(f"Index: {index}\n")
                f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
                
            return filepath
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return None


class Scanner_Backend:
    def __init__(self, sn_x=None, sn_y=None, sn_cam=None):
        self.x_stage = None
        self.y_stage = None
        self.camera = Camera(sn_cam)
        self.scan = Scan(self.camera, self.x_stage, self.y_stage)

    def connect_cam(self, sn):
        self.camera = Camera(sn)
        self.scan.camera = self.camera
        
    def connect_stage(self, sn, ax):
        if ax == 'x':
            self.x_stage = Stage("X", sn)
            self.scan.x_stage = self.x_stage
        elif ax == 'y':        
            self.y_stage = Stage("Y", sn)
            self.scan.y_stage = self.y_stage

    def setup_scan_saving(self, folder, prefix, auto_save=True, overwrite=False):
        """Configure image saving parameters for the scan"""
        return self.scan.setup_saving(folder, prefix, auto_save, overwrite)

    def close(self):
        """Properly close the connection to the hardware"""
        for device in [self.x_stage, self.y_stage, self.camera]:
            if device: device.close()
    
    def __del__(self):
        self.close()

