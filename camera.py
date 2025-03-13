from pylablib.devices.Thorlabs import ThorlabsTLCamera
import cv2

class Camera:
    def __init__(self, serial_number=None):
        self.serial_number = serial_number
        self.camera = None
        self.exposure = 100  # Default exposure in ms
        self.image_count = 0
        
        if self.serial_number is None:
            print("WARNING: Camera initialized in simulation mode (no serial number provided)")
            # Put the images in an array
            self.dummy_images = [cv2.imread('dummy_frame_1.png'),cv2.imread('dummy_frame_2.png')]
        else:
            self._connect_camera()
    
    def _connect_camera(self):
        """Connect to the physical camera if a serial number is provided"""
        try:
            self.camera = ThorlabsTLCamera.ThorlabsTLCamera(self.serial_number)
            self.camera.setup_acquisition()  # Prepare camera for acquisition
            # Set initial exposure
            self.camera.set_exposure(self.exposure / 1000.0)  # Convert ms to seconds
            print(f"Connected to camera with serial {self.serial_number}")
        except Exception as e:
            print(f"Failed to connect to camera: {e}")
            print("WARNING: Camera will operate in simulation mode")
            self.camera = None
    
    def set_exposure(self, exposure_ms):
        """Set the camera exposure in milliseconds"""
        self.exposure = exposure_ms
        if self.camera:
            try:
                # ThorlabsTLCamera expects exposure in seconds
                self.camera.set_exposure(exposure_ms / 1000.0)
                print(f"Hardware camera exposure set to {exposure_ms}ms")
            except Exception as e:
                print(f"Error setting camera exposure: {e}")
        else:
            # Simulation mode
            print(f"Camera exposure set to {exposure_ms}ms (simulation)")
    
    def snap_image(self):
        """Take an image with current settings and return image data"""
        self.image_count += 1
        
        if self.camera:
            try:
                # Start acquisition and wait for completion
                self.camera.start_acquisition()
                frame = self.camera.grab(frame_timeout=2 * self.exposure / 1000.0)  # Wait longer than exposure
                self.camera.stop_acquisition()
                
                # In a real app, you might want to save this image
                print(f"Image {self.image_count} captured with hardware camera")
            except Exception as e:
                print(f"Error capturing image: {e}")
                # Generate a dummy image in case of error
                print(f"Returning simulated image instead")
                return f"simulated_image_{self.image_count}"
        else:
            # Simulation mode
            print(f"Image {self.image_count} captured with {self.exposure}ms exposure (simulation)")
            # In simulation mode, we return a string instead of image data
            frame = self.dummy_images[self.image_count%2]
        return frame
        

    def close(self):
        """Properly close the connection to the hardware"""
        if self.camera:
            try:
                print("Closing connection to camera")
                self.camera.close()
            except Exception as e:
                print(f"Error closing camera: {e}")
            finally:
                self.camera = None
    
    def __del__(self):
        """Destructor to ensure camera is closed when object is deleted"""
        self.close()