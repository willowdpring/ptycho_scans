
# this is a hardcode for the borrowed SCAPA XIstage and is NOT PRETTY
import libximc.highlevel as ximc
from axis import Axis
from axisparameters import * # AxisParameters


xi_params = AxisParameters(
                    pm_id='STANDA axis',
                    #address=f'xi-emu:///{Path.home() / 'Temp' / 'br_stage1_test.bin'}',
                    address=f'xi-com:\\\\.\\COM3',
                    calibration=0.00125,
                    label='Axis 1',
                    units=' mm',
                    min_value=.0,
                    max_value=50.0,
                    zero_position=0.0,
                    step=10.0,
                    range_limited=True,
                    can_home=True,
                    controls_enabled=True,
                    references=[
                        Reference(
                            True,
                            'Move in',
                            0.0,
                            'Target IN',
                            PositionStyle.text_bold()
                        ),
                        Reference(
                            True,
                            'Move out',
                            10.0,
                            'Target OUT',
                            PositionStyle.red_bold()
                        ),
                    ],
                    references_enabled=True,
                    ref_out_styles=PositionStyle.default()
                )


class XiStage:
    def __init__(self,name = "STANDA_STAGE"):
        self.config_parser = ConfigParser(name="default_conf")
        self.axis = Axis(xi_params,self.config_parser)
        self.name = name
        self._connect_stage()
        self.position = self.axis.get_position()


    def _connect_stage(self):
        """Connect to the physical stage if a serial number is provided"""
        self.axis.open_device()
        
    def set_zero(self):
        self.axis.set_zero()

    def zero(self):
        self.axis.home()   
             
    def move_by(self, relative_distance):
        """Move stage by a relative distance from current position"""
        target = self.position + relative_distance
        return self.move_to(target)
        
    def move_to(self, target_position):
        self.axis.move(target_position) # will this wait?
        self.position = self.axis.get_position()
            
        print(f"Stage {self.name} moved to absolute position {self.position}")
        return self.position
    
    def close(self):
        """Properly close the connection to the hardware"""
        if self.axis:
            try:
                print(f"Closing connection to {self.name} stage")
                self.axis.close_device()
            except Exception as e:
                print(f"Error closing {self.name} stage: {e}")
            finally:
                self.translator = None

    def __del__(self):
        """Destructor to ensure stage is closed when object is deleted"""
        self.close()


if __name__ == '__main__':
    # Enumerate devices with the ENUMERATE_PROBE flag to get full information
    devices = ximc.enumerate_devices(ximc.EnumerateFlags.ENUMERATE_PROBE)

    # Display information about each detected device
    for device in devices:
        print("-" * 40)
        print(f"Device Name: {device['PositionerName']}")
        print(f"Device URI: {device['uri']}")
        print(f"Serial Number: {device['device_serial']}")
        print(f"Manufacturer: {device['Manufacturer']}")
    print("-" * 40)