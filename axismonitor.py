import time

from PySide6.QtCore import QObject, Signal

from .axis import Axis, AxisStatus


class AxisMonitor(QObject):
    new_position = Signal(AxisStatus)
    status_message = Signal(str)
    finished = Signal()

    REFRESH_MOVING = 0.2
    REFRESH_IDLE = 1.
    RECONNECT_ERROR_COUNT = 2

    def __init__(self, axis: Axis, parent=None):
        super().__init__(parent)
        self.axis = axis
        self.status = None
        self.n_status_error = 0

        self.exit = False

        self.t_sleep = self.REFRESH_MOVING

    def run(self):
        while True:
            if self.exit:
                break

            self.get_status()
            time.sleep(self.t_sleep)

        self.finished.emit()

    def get_status(self):
        self.status = self.axis.get_status()
        if self.status.status is not None:
            self.n_status_error = 0
            self.t_sleep = self.REFRESH_MOVING if self.status.is_moving else self.REFRESH_IDLE
            self.new_position.emit(self.status)
        else:
            self.record_status_error()
            self.status_message.emit('Disconnected')

    def record_status_error(self):
        self.n_status_error += 1
        if self.n_status_error > self.RECONNECT_ERROR_COUNT - 1:
            self.n_status_error = 0
            self.axis.reopen_device()
            self.status_message.emit('Connecting')
