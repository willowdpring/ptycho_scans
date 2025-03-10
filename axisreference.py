from PySide6.QtGui import QPalette, QGuiApplication

def is_dark_mode():
    p = QPalette()
    c_text = p.color(QPalette.ColorRole.WindowText)
    c_window = p.color(QPalette.ColorRole.Window)
    dark_mode = c_text.lightness() > c_window.lightness()
    return dark_mode


class PositionStyle:
    def __init__(
            self,
            moving: str,
            incorrect: str,
    ):
        self.moving = moving
        self.incorrect = incorrect

    @staticmethod
    def default(font_pt: int = 24):
        s = PositionStyle(
            moving=f'Font: bold {font_pt}pt;',
            incorrect=f'Font: bold {font_pt}pt; color: #C70039;'
        )
        return s

    @staticmethod
    def text_color():
        return QGuiApplication.palette().text().color().name()

    @staticmethod
    def text(font_pt: int = 24):
        return f'Font: {font_pt}pt;'

    @staticmethod
    def text_bold(font_pt: int = 24):
        return f'Font: bold {font_pt}pt;'

    @staticmethod
    def red(font_pt: int = 24):
      return f'Font: {font_pt}pt; color: #707b7c;'

    @staticmethod
    def red_bold(font_pt: int = 24):
      return f'Font: bold {font_pt}pt; color: #707b7c;'


class Reference:
    def __init__(
            self,
            enabled: bool,
            button_label: str,
            position: float,
            position_label: str,
            position_style: str
    ):
        self.enabled = enabled
        self.button_label = button_label
        self.position = position
        self.position_label = position_label
        self.position_style = position_style
