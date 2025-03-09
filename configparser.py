from pathlib import Path

import json


class ConfigParser:
    CONFIG_PATH = 'config'

    def __init__(self, name: str):
        self.name = name

    def get_entry(self, key: str):
        cfg = self.read_config()
        if cfg is None:
            return None

        return cfg.get(key, None)

    def write_entry(self, cfg_dict):
        cfg = self.read_config()
        for key, value in cfg_dict.items():
            cfg[key] = value

        self.write_config(cfg)

    def read_config(self):
        try:
            filename = self.get_config_filename()
            path = self.get_path(filename)
            with open(path, 'r') as f:
                return json.load(f)
        except (IOError, json.decoder.JSONDecodeError):
            return {}

    def write_config(self, cfg):
        try:
            filename = self.get_config_filename()
            with open(self.get_path(filename), 'w') as f:
                return json.dump(cfg, f, ensure_ascii=False, indent=4)
        except IOError:
            filename = self.get_config_filename()
            p = self.get_path(filename)
            print(f"Error writing config to '{p}'")
            return None

    def get_config_filename(self):
        return f'cfg_{self.name}.json'

    @staticmethod
    def get_path(p):
        return Path(__file__).parent / ConfigParser.CONFIG_PATH / p
