from stage import Stage
from camera import Camera
import time

class Scan:
    def __init__(self,cam,x,y):
        self.x_stage = cam
        self.y_stage = x
        self.camera = y
        
        # Scan parameters
        self.num_x = 5  # Number of X positions
        self.num_y = 5  # Number of Y positions
        self.res_x = 1.0  # X resolution (step size)
        self.res_y = 1.0  # Y resolution (step size)
        self.snake_pattern = True  # True for snake, False for ladder
        
        # State variables
        self.is_running = False
        self.is_paused = False
        self.current_x = 0
        self.current_y = 0
        
    def setup_scan(self, num_x, num_y, res_x, res_y, snake_pattern=True):
        """Configure the scan parameters"""
        self.num_x = num_x
        self.num_y = num_y
        self.res_x = res_x
        self.res_y = res_y
        self.snake_pattern = snake_pattern
        print(f"Scan configured: {num_x}x{num_y} grid with {res_x}x{res_y} resolution")
        print(f"Pattern: {'Snake' if snake_pattern else 'Ladder'}")
        
    def start_scan(self):
        """Start or resume a scan"""
        self.is_running = True
        self.is_paused = False
        print("Scan started")
        
        try:
            while self.is_running and self.current_y < self.num_y:
                if self.is_paused:
                    time.sleep(0.1)  # Small sleep to prevent CPU hogging while paused
                    continue
                    
                # Determine X direction based on pattern and current row
                x_direction = 1
                x_start = 0
                if self.snake_pattern and self.current_y % 2 == 1:
                    x_direction = -1
                    x_start = self.num_x - 1
                
                # Set initial X position for this row if starting
                if self.current_x == 0:
                    self.current_x = x_start
                    x_pos = x_start * self.res_x
                    self.x_stage.move_to(x_pos)
                
                # Take image at current position
                print(f"Scanning position ({self.current_x}, {self.current_y})")
                image = self.camera.snap_image()
                
                # Save image with position information
                self._save_image(image, self.current_x, self.current_y)
                
                # Move to next position
                if x_direction == 1:
                    self.current_x += 1
                    if self.current_x >= self.num_x:
                        self.current_y += 1
                        self.current_x = 0
                        if self.current_y < self.num_y:
                            self.y_stage.set_position(self.current_y * self.res_y)
                    else:
                        self.x_stage.set_position(self.current_x * self.res_x)
                else:  # x_direction == -1
                    self.current_x -= 1
                    if self.current_x < 0:
                        self.current_y += 1
                        self.current_x = 0
                        if self.current_y < self.num_y:
                            self.y_stage.set_position(self.current_y * self.res_y)
                    else:
                        self.x_stage.set_position(self.current_x * self.res_x)
                
                # Small delay to avoid overwhelming the hardware
                time.sleep(0.1)
                
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
        self.x_stage.zero()
        self.y_stage.zero()
        """Reset scan position to beginning"""
        self.current_x = 0
        self.current_y = 0
        self.is_running = False
        self.is_paused = False
        
    def _save_image(self, image_data, x_pos, y_pos):
        """Save the image with position metadata"""
        # In a real implementation, this would save to file with appropriate naming
        print(f"Saving image at position ({x_pos}, {y_pos})")


class Scanner_Backend:
    def __init__(self, sn_x = None, sn_y = None, sn_cam = None):
        self.x_stage = None
        self.y_stage = None
        self.camera = Camera(sn_cam)
        self.scan = Scan(self.camera,self.x_stage,self.y_stage)

    def connect_stage(self,sn,ax):
        if ax == 'x':
            self.x_stage = Stage("X",sn)
        elif ax == 'y':        
            self.x_stage = Stage("Y",sn)

    def close(self):
        """Properly close the connection to the hardware"""
        for device in [self.x_stage,self.y_stage,self.camera]:
            if device: device.close()
    
    def __del__(self):
        self.close()

