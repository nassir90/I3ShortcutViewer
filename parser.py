#!/usr/bin/env python3

from pathlib import Path
from typing import List, Tuple


class ShortcutGroup:
    def __init__(self, name: str):
        self.name = name
        self.shortcuts = []

    def add_shortcut(self, keybinding: str, command: str):
        self.shortcuts.append((keybinding, command))


def parse_shortcuts_file(filepath: str = None) -> List[ShortcutGroup]:
    if filepath is None:
        filepath = Path.home() / ".config" / "i3" / "shortcuts"
    else:
        filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Shortcuts file not found: {filepath}")

    groups = []
    current_group = ShortcutGroup("General")

    with open(filepath, 'r') as f:
        for line in f:
            line = line.rstrip()

            if not line.strip():
                continue

            if line.startswith('#'):
                comment_text = line.lstrip('#').strip()
                if comment_text:
                    if current_group.shortcuts:
                        groups.append(current_group)
                    current_group = ShortcutGroup(comment_text)
                continue

            if line.strip().startswith('bindsym'):
                keybinding, command = parse_bindsym_line(line)
                if keybinding and command:
                    current_group.add_shortcut(keybinding, command)

    if current_group.shortcuts:
        groups.append(current_group)

    return groups


def parse_bindsym_line(line: str) -> Tuple[str, str]:
    line = line.strip()
    if not line.startswith('bindsym'):
        return None, None

    line = line[7:].strip()

    parts = line.split(None, 1)
    if len(parts) < 2:
        return None, None

    keybinding = parts[0]
    command = parts[1]

    if command.startswith('exec'):
        command = command[4:].strip()

    command = command.replace('--no-startup-id', '').strip()

    if command.startswith('"') and command.endswith('"'):
        command = command[1:-1]

    command = command.rstrip('&').strip()

    return keybinding, command


if __name__ == "__main__":
    try:
        groups = parse_shortcuts_file()
        for group in groups:
            print(f"\n{group.name}")
            print("=" * len(group.name))
            for keybinding, command in group.shortcuts:
                print(f"{keybinding:40} {command}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
