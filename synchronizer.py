from PySide6.QtCore import QMutex, QMutexLocker, QWaitCondition


class Synchronizer:
    def __init__(self):
        self.mutex = QMutex()
        self.cv = QWaitCondition()

    def notify(self):
        lock = QMutexLocker(self.mutex)
        self.cv.wakeAll()

    def wait(self):
        lock = QMutexLocker(self.mutex)
        self.cv.wait(self.mutex)
