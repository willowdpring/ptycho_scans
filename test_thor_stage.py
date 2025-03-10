# test thor stage
from pylablib.devices.Thorlabs.kinesis import KinesisMotor, list_kinesis_devices

device_sn = list_kinesis_devices()[0][0]

stage = KinesisMotor(device_sn,scale = 'stage') # autodetect scale

print(f"{stage.get_device_info() = }\n\n")
print(f"{stage.get_scale() = }\n\n")
print(f"{stage.get_scale_units() = }\n\n")
print(f"{stage.get_gen_move_parameters() = }\n\n")
print(f"{stage.home() = }\n\n")
(f"{stage.get_position() = }\n\n")
(f"{stage.move_by(1e-3) = }\n\n") # 1mm
(f"{stage.get_position() = }\n\n")
