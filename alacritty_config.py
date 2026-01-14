#!/usr/bin/env python3

import tomllib
from pathlib import Path
from typing import Dict, Optional


class AlacrittyTheme:
    def __init__(self):
        self.background = "#2e3440"
        self.foreground = "#d8dee9"
        self.font_family = "Monospace"
        self.font_size = 10
        self.normal_black = "#2e3436"
        self.normal_red = "#cc0000"
        self.normal_green = "#73d216"
        self.normal_yellow = "#edd400"
        self.normal_blue = "#3465a4"
        self.normal_magenta = "#75507b"
        self.normal_cyan = "#06989a"
        self.normal_white = "#d3d7cf"
        self.bright_black = "#2e3436"
        self.bright_red = "#ef2929"
        self.bright_green = "#8ae234"
        self.bright_yellow = "#fce94f"
        self.bright_blue = "#729fcf"
        self.bright_magenta = "#ad7fa8"
        self.bright_cyan = "#34e2e2"
        self.bright_white = "#eeeeec"


def parse_alacritty_config(config_path: Optional[Path] = None) -> AlacrittyTheme:
    theme = AlacrittyTheme()

    if config_path is None:
        config_path = Path.home() / ".config" / "alacritty" / "alacritty.toml"

    if not config_path.exists():
        return theme

    try:
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)

        if 'colors' in config:
            colors = config['colors']

            if 'primary' in colors:
                primary = colors['primary']
                if 'background' in primary:
                    theme.background = primary['background']
                if 'foreground' in primary:
                    theme.foreground = primary['foreground']

            if 'normal' in colors:
                normal = colors['normal']
                theme.normal_black = normal.get('black', theme.normal_black)
                theme.normal_red = normal.get('red', theme.normal_red)
                theme.normal_green = normal.get('green', theme.normal_green)
                theme.normal_yellow = normal.get('yellow', theme.normal_yellow)
                theme.normal_blue = normal.get('blue', theme.normal_blue)
                theme.normal_magenta = normal.get('magenta', theme.normal_magenta)
                theme.normal_cyan = normal.get('cyan', theme.normal_cyan)
                theme.normal_white = normal.get('white', theme.normal_white)

            if 'bright' in colors:
                bright = colors['bright']
                theme.bright_black = bright.get('black', theme.bright_black)
                theme.bright_red = bright.get('red', theme.bright_red)
                theme.bright_green = bright.get('green', theme.bright_green)
                theme.bright_yellow = bright.get('yellow', theme.bright_yellow)
                theme.bright_blue = bright.get('blue', theme.bright_blue)
                theme.bright_magenta = bright.get('magenta', theme.bright_magenta)
                theme.bright_cyan = bright.get('cyan', theme.bright_cyan)
                theme.bright_white = bright.get('white', theme.bright_white)

        if 'font' in config:
            font = config['font']
            if 'size' in font:
                theme.font_size = int(font['size'])
            if 'normal' in font and 'family' in font['normal']:
                theme.font_family = font['normal']['family']

    except Exception as e:
        pass

    return theme


if __name__ == "__main__":
    theme = parse_alacritty_config()
    print(f"Background: {theme.background}")
    print(f"Foreground: {theme.foreground}")
    print(f"Font: {theme.font_family} {theme.font_size}pt")
    print(f"Green: {theme.normal_green}")
    print(f"Blue: {theme.normal_blue}")
