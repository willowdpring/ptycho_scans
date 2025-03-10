# stage.py
from pylablib.devices.Thorlabs import KinesisMotor  
import time

class Stage:
    def __init__(self, name="unnamed", serial_number=None):
        self.name = name
        self.position = 0.0
        self.serial_number = serial_number
        self.translator = None
        self.zero_pos = 0.0 
        if self.serial_number is None:
            print(f"WARNING: {self.name} stage initialized in simulation mode (no serial number provided)")
        else:
            self._connect_stage()
        
    def _connect_stage(self):
        """Connect to the physical stage if a serial number is provided"""
        try:
            self.translator = KinesisMotor(self.serial_number,scale='MTS25-Z8')
            self.units = self.translator.get_scale_units()
            # Set initial position from the actual hardware
            self.position = self.translator.get_position()
            print(f"Connected to {self.name} stage with serial {self.serial_number}")
        except Exception as e:
            print(f"Failed to connect to {self.name} stage: {e}")
            print(f"WARNING: {self.name} stage will operate in simulation mode")
            self.units = 'm'
            # If we can't connect, we'll operate in simulation mode
            self.translator = None
        
    def set_zero(self):
        if self.translator:
            self.zero_pos = self.translator.get_position()        
        else:
            self.zero_pos = self.position    

    def zero(self):
        if self.translator:
            self.translator.home()
        else: # dummy
            self.move_to(0)
        self.move_to(self.zero_pos)
        
    def move_by(self, relative_distance):
        """Move stage by a relative distance from current position"""
        target = self.position + relative_distance + self.zero_pos
        return self.move_to(target)
        
    def move_to(self, target_position):
        """Move stage to an absolute position"""
        if self.translator:
            try:
                self.translator.move_to(target_position-self.zero_pos)
                while self.translator.is_moving:
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error during absolute movement: {e}")
            self.position = self.translator.get_position()
        else:
            # Simulation mode
            time.sleep(0.5) # emulate hardware wait
            self.position = target_position
            

        print(f"Stage {self.name} moved to absolute position {self.position}")
        return self.position
    
    def close(self):
        """Properly close the connection to the hardware"""
        if self.translator:
            try:
                print(f"Closing connection to {self.name} stage")
                self.translator.close()
            except Exception as e:
                print(f"Error closing {self.name} stage: {e}")
            finally:
                del(self.translator)
        else:
            print(f"Closing virtual {self.name} stage")
            
    def __del__(self):
        """Destructor to ensure stage is closed when object is deleted"""
        self.close()

