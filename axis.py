import libximc.highlevel as ximc
from libximc import status_calb_t

from axisparameters import AxisParameters
from configparser import ConfigParser
from synchronizer import Synchronizer

class AxisRange:
    def __init__(self, pm: AxisParameters, config_parser: ConfigParser):
        self.pm = pm
        self.config_parser = config_parser

    @property
    def min_pos(self):
        return self.pm.min_value - self.pm.zero_position

    @property
    def max_pos(self):
        return self.pm.max_value - self.pm.zero_position

    @property
    def range(self):
        return self.min_pos, self.max_pos

    @property
    def span(self):
        return abs(self.max_pos - self.min_pos)

    def set_zero(self, zero_position: float):
        zero = self.pm.zero_position + zero_position
        if self.pm.zero_position != zero:
            self.pm.zero_position = zero
            self.pm.save(self.config_parser)


class Axis:
    def __init__(self, pm: AxisParameters, config_parser: ConfigParser, verbose: bool = False):
        self.pm = pm
        self.verbose = verbose
        self.range = AxisRange(self.pm, config_parser)
        self.axis: ximc.Axis | None = None
        self.error = ''
        self.sync = Synchronizer()

    def has_error(self):
        return len(self.error) > 0

    def open_device(self):
        self.error = ''
        try:
            self.axis = ximc.Axis(self.pm.address)
        except TypeError as err:
            self.error = str(err)
            return

        try:
            self.axis.open_device()
        except ConnectionError as err:
            self.error = str(err)
            return

        self._set_calibration()
        if self.verbose:
            print(f'Device {self.axis.uri} open')

    def _set_calibration(self):
        self.axis.set_calb(self.pm.calibration, self.axis.get_engine_settings().MicrostepMode)

    def close_device(self):
        if self.axis is None:
            return

        self.error = ''
        try:
            self.axis.close_device()
        except Exception as err:
            self.error = str(err)

        if self.verbose:
            print(f'Device {repr(self.axis.uri)} closed')

    def reopen_device(self):
        self.close_device()
        self.open_device()

    def get_position(self) -> float | None:
        self.error = ''
        try:
            pos = self.axis.get_position_calb()
            return pos.Position
        except Exception as err:
            self.error = err
            return None

    def get_status(self):
        status = None
        self.error = ''
        try:
            status = self.axis.get_status_calb()
        except Exception as err:
            self.error = err

        return AxisStatus(self.pm, status, False)

    def move(self, position: float):
        if self.verbose:
            print(f'Moving to {position}')

        self.error = ''
        try:
            self.axis.command_move_calb(position)
        except Exception as err:
            self.error = str(err)
            print(self.error)

    def move_left(self):
        self.error = ''
        try:
            self.axis.command_left()
        except Exception as err:
            self.error = str(err)

        if self.verbose:
            print('Moving left')

    def move_right(self):
        self.error = ''
        try:
            self.axis.command_right()
        except Exception as err:
            self.error = str(err)

        if self.verbose:
            print('Moving right')

    def hard_stop(self):
        self.error = ''
        try:
            self.axis.command_stop()
        except Exception as err:
            self.error = str(err)

    def stop(self):
        self.error = ''
        try:
            self.axis.command_sstp()
        except Exception as err:
            self.error = str(err)

    def set_zero(self):
        current_pos = self.get_position()
        if current_pos is None:
            self.error = 'Command zero: Unable to get current position'
            return

        self.error = ''
        try:
            self.axis.command_zero()
            self.range.set_zero(current_pos)
        except Exception as err:
            self.error = str(err)

    def home(self):
        self.error = ''
        try:
            self.axis.command_home()
        except Exception as err:
            self.error = str(err)

class AxisStatus:
    def __init__(self, axis_pm: AxisParameters, status: status_calb_t, verbose: bool = False):
        self.pm = axis_pm
        self.status = status
        self.verbose = verbose

    @property
    def position(self):
        return self.status.CurPosition

    @property
    def is_moving(self):
        if self.verbose > 0:
            print(self.get_info())

        return (self.status.MvCmdSts.value & ximc.MvcmdStatus.MVCMD_RUNNING.value) > 0

    @property
    def is_left(self):
        return (self.status.GPIOFlags.value & ximc.GPIOFlags.STATE_LEFT_EDGE.value) > 0

    @property
    def is_right(self):
        return (self.status.GPIOFlags.value & ximc.GPIOFlags.STATE_RIGHT_EDGE.value) > 0

    def get_info(self):
        s = (
            f'MoveSts: {self.status.MoveSts}\n'
            f'MoveCmdSts: {self.status.MvCmdSts}\n'
            f'PWRSts: {self.status.PWRSts}\n'
            f'EncSts: {self.status.EncSts}\n'
            f'WindSts: {self.status.WindSts}\n'
            f'CurPosition: {self.status.CurPosition}\n'
            f'EncPosition: {self.status.EncPosition}\n'
            f'CurSpeed: {self.status.CurSpeed}\n'
            f'Ipwr: {self.status.Ipwr} mA\n'
            f'Upwr: {0.1 * self.status.Upwr:g} mV\n'
            f'Iusb: {self.status.Iusb} mA\n'
            f'Uusb: {self.status.Uusb}\n'
            f'CurT: {0.1 * self.status.CurT:g} C\n\n'
        )
        ms = MvCmdStatus(self.status.MvCmdSts)
        s += ms.get_info()

        gs = GPIOStatus(self.status.GPIOFlags)
        s += gs.get_info()
        return s


class MvCmdStatus:
    def __init__(self, status: ximc.MvcmdStatus):
        self.status = status

    def get_info(self):
        s = (
            f'Command bit mask: {self.status.value & ximc.MvcmdStatus.MVCMD_NAME_BITS.value}\n'
            f'Command unknown: {self.status.value & ximc.MvcmdStatus.MVCMD_UKNWN.value}\n'
            f'Command move: {self.status.value & ximc.MvcmdStatus.MVCMD_MOVE.value}\n'
            f'Command movr: {self.status.value & ximc.MvcmdStatus.MVCMD_MOVR.value}\n'
            f'Command left: {self.status.value & ximc.MvcmdStatus.MVCMD_LEFT.value}\n'
            f'Command right: {self.status.value & ximc.MvcmdStatus.MVCMD_RIGHT.value}\n'
            f'Command stop: {self.status.value & ximc.MvcmdStatus.MVCMD_STOP.value}\n'
            f'Command home: {self.status.value & ximc.MvcmdStatus.MVCMD_HOME.value}\n'
            f'Command loft: {self.status.value & ximc.MvcmdStatus.MVCMD_LOFT.value}\n'
            f'Command soft stop: {self.status.value & ximc.MvcmdStatus.MVCMD_SSTP.value}\n'
            f'Command error: {self.status.value & ximc.MvcmdStatus.MVCMD_ERROR.value}\n'
            f'Running: {self.status.value & ximc.MvcmdStatus.MVCMD_RUNNING.value}\n'
        )
        return s


class GPIOStatus:
    def __init__(self, status: ximc.GPIOFlags):
        self.status = status

    def get_info(self):
        s = (
            f'Right edge: {self.status.value & ximc.GPIOFlags.STATE_RIGHT_EDGE.value}\n'
            f'Left edge: {self.status.value & ximc.GPIOFlags.STATE_LEFT_EDGE.value}\n'
            f'Button right: {self.status.value & ximc.GPIOFlags.STATE_BUTTON_RIGHT.value}\n'
            f'Button left: {self.status.value & ximc.GPIOFlags.STATE_BUTTON_LEFT.value}\n'
            f'Brake: {self.status.value & ximc.GPIOFlags.STATE_BRAKE.value}\n'
        )
        return s
