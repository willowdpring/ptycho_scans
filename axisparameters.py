from customconfigparser import ConfigParser
from axisreference import Reference, PositionStyle


class AxisParameters:

    ZERO_POSITION = 'zero_position'

    SAVED = (
        'zero_position',
    )

    def __init__(
            self,
            pm_id: str,
            address: str,
            calibration: float,
            label: str,
            units: str,
            min_value: float,
            max_value: float,
            zero_position: float,
            step: float,
            range_limited: bool,
            can_home: bool,
            controls_enabled: bool,
            references: list[Reference],
            references_enabled: bool,
            ref_out_styles: PositionStyle | None,
    ):
        self.pm_id = pm_id
        self.address = address
        self.calibration = calibration
        self.label = label
        self.units = units
        self.min_value = min_value
        self.max_value = max_value
        self.zero_position = zero_position
        self.step = step
        self.range_limited = range_limited
        self.can_home = can_home
        self.controls_enabled = controls_enabled
        self.references = references
        self.references_enabled = references_enabled
        self.ref_out_styles = ref_out_styles
        self.save_ids = [self.pm_id]

    @property
    def config_id(self):
        return f'{AxisParameters.__name__}_{self.pm_id}'

    def from_dict(self, pm_dict):
        for key, value in pm_dict.items():
            setattr(self, key, value)

    def to_dict(self):
        pm_dict = {p: getattr(self, p) for p in AxisParameters.SAVED}
        return {self.config_id: pm_dict}

    def update(self, config_parser: ConfigParser):
        pm_dict = config_parser.get_entry(self.config_id)
        if pm_dict is not None:
            self.from_dict(pm_dict)

    def save(self, config_parser: ConfigParser):
        config_parser.write_entry(self.to_dict())
