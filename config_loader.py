#!/usr/bin/env python3

import tomllib
from pathlib import Path
from typing import Optional


class Config:
    def __init__(self):
        self.font_size = 10
        self.header_font_size = 12
        self.wrap_command = True


def load_config(script_dir: Optional[Path] = None) -> Config:
    config = Config()

    config_locations = []

    if script_dir:
        config_locations.append(script_dir / "config.toml")

    config_locations.append(Path.home() / ".config" / "i3-shortcut-viewer" / "config.toml")

    config_path = None
    for path in config_locations:
        if path.exists():
            config_path = path
            break

    if not config_path:
        return config

    try:
        with open(config_path, 'rb') as f:
            data = tomllib.load(f)

        if 'font' in data:
            font = data['font']
            if 'size' in font:
                config.font_size = int(font['size'])
            if 'header_size' in font:
                config.header_font_size = int(font['header_size'])

        if 'display' in data:
            display = data['display']
            if 'wrap_command' in display:
                config.wrap_command = bool(display['wrap_command'])

    except Exception:
        pass

    return config


if __name__ == "__main__":
    config = load_config()
    print(f"Font size: {config.font_size}")
    print(f"Header font size: {config.header_font_size}")
