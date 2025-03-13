
# this is a hardcode for the borrowed SCAPA XIstage and is NOT PRETTY
import libximc.highlevel as ximc
from axis import Axis
from axisparameters import * # AxisParameters
from customconfigparser import ConfigParser
import time

default_params = AxisParameters(
                    pm_id='STANDA axis',
                    #address=f'xi-emu:///{Path.home() / 'Temp' / 'br_stage1_test.bin'}',
                    address=f'xi-com:\\\\.\\COM4',
                    calibration=0.00125,
                    label='Axis 1',
                    units='mm',
                    min_value=.5,
                    max_value=24.5,
                    zero_position=5.0,
                    step=1.0,
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
    def __init__(self,xi_params,name = "STANDA_STAGE"):
        print("xinit")
        self.name = name
        self.config_parser = ConfigParser(name)
        print("makeax")
        self.axis = Axis(xi_params,self.config_parser)
        self.min_value = xi_params.min_value 
        self.max_value = xi_params.max_value 
        self._connect_stage()
        
        print("get_pos")
        self.position = self.axis.get_position()
        if self.position == None:
            print(self.axis.error)

        print("done")

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
        if (target_position < self.config_parser.get_entry('min_value') 
            or target_position > self.config_parser.get_entry('max_value')):
            print(f"ERROR target position is outside software limits!")
            return self.position

        self.axis.move(target_position)
        while self.axis.get_status.is_moving():
            time.sleep(0.5)

        self.position = self.axis.get_position()

            
        print(f"Stage {self.name} moved to absolute position {self.position}")
        return self.position
    
    def close(self):
        """Properly close the connection to the hardware"""
        try:
            print(f"Closing connection to {self.name} stage")
            self.axis.close_device()
        except Exception as e:
            print(f"Error closing {self.name} stage: {e}")
        finally:
            self.axis = None

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