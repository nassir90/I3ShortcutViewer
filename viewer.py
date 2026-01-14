#!/usr/bin/env python3

import re
import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path
from parser import parse_shortcuts_file
from alacritty_config import parse_alacritty_config
from config_loader import load_config


class ShortcutsViewer:
    def __init__(self, root, script_dir=None):
        self.root = root
        self.root.title("i3 Shortcuts")
        self.root.geometry("900x600")

        self.theme = parse_alacritty_config()
        config = load_config(script_dir)
        self.font_size = config.font_size
        # Make header font larger than regular font (use config value if larger, otherwise add 4)
        self.header_font_size = max(config.header_font_size, config.font_size + 4)
        self.wrap_mode = tk.WORD if config.wrap_command else tk.NONE

        self.search_matches = []
        self.current_match_index = -1

        # Smooth scrolling state
        self.scroll_animation_id = None
        self.scroll_velocity = 0
        self.scroll_target = 0

        main_frame = tk.Frame(root, bg=self.theme.background)
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_bg = self.lighten_color(self.theme.background, 0.15)
        self.search_frame = tk.Frame(main_frame, bg=search_bg, height=40)
        self.search_frame.pack(fill=tk.X, side=tk.TOP)
        self.search_frame.pack_forget()

        search_label = tk.Label(
            self.search_frame,
            text="Search:",
            bg=search_bg,
            fg=self.theme.foreground,
            font=(self.theme.font_family, self.font_size),
            padx=10
        )
        search_label.pack(side=tk.LEFT, pady=8)

        self.search_entry = tk.Entry(
            self.search_frame,
            bg=self.theme.background,
            fg=self.theme.foreground,
            insertbackground=self.theme.bright_cyan,
            font=(self.theme.font_family, self.font_size),
            relief=tk.FLAT,
            borderwidth=2
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        self.search_entry.bind('<Escape>', self.close_search)
        self.search_entry.bind('<Return>', lambda e: self.next_match())

        self.search_info = tk.Label(
            self.search_frame,
            text="",
            bg=search_bg,
            fg=self.theme.bright_blue,
            font=(self.theme.font_family, 9),
            padx=10
        )
        self.search_info.pack(side=tk.RIGHT, pady=8)

        self.text_widget = scrolledtext.ScrolledText(
            main_frame,
            wrap=self.wrap_mode,
            font=(self.theme.font_family, self.font_size),
            bg=self.theme.background,
            fg=self.theme.foreground,
            insertbackground=self.theme.bright_cyan,
            selectbackground=self.lighten_color(self.theme.background, 0.2),
            selectforeground=self.theme.bright_white,
            padx=15,
            pady=15,
            borderwidth=0,
            highlightthickness=0
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        tab_position = 350
        self.text_widget.configure(tabs=(tab_position,))

        self.text_widget.tag_config('header', foreground=self.theme.bright_blue, font=(self.theme.font_family, self.header_font_size, 'bold'))
        self.text_widget.tag_config('separator', foreground=self.theme.bright_black)
        self.text_widget.tag_config('keybinding', foreground=self.theme.bright_green, font=(self.theme.font_family, self.font_size))
        self.text_widget.tag_config('command', foreground=self.theme.foreground, font=(self.theme.font_family, self.font_size), lmargin2=tab_position)
        self.text_widget.tag_config('wrap_indicator', foreground=self.theme.bright_black, font=(self.theme.font_family, self.font_size))
        self.text_widget.tag_config('search_highlight', background=self.theme.normal_yellow, foreground=self.theme.background)
        self.text_widget.tag_config('search_current', background=self.theme.bright_green, foreground=self.theme.background)

        self.text_widget.bind('<<Copy>>', self.handle_copy)

        self.root.bind('/', self.open_search)
        self.root.bind('n', lambda e: self.next_match())
        self.root.bind('N', lambda e: self.prev_match())
        self.root.bind('<Escape>', self.handle_escape)

        # Scrolling keybindings
        self.root.bind('<Up>', self.scroll_up)
        self.root.bind('<Down>', self.scroll_down)
        self.root.bind('<Prior>', self.scroll_page_up)  # Page Up
        self.root.bind('<Next>', self.scroll_page_down)  # Page Down
        self.root.bind('<Control-p>', self.scroll_up)  # Emacs-style up
        self.root.bind('<Control-n>', self.scroll_down)  # Emacs-style down

        # Mouse wheel scrolling
        self.text_widget.bind('<MouseWheel>', self.on_mousewheel)  # Windows/Mac
        self.text_widget.bind('<Button-4>', self.on_mousewheel_linux_up)  # Linux scroll up
        self.text_widget.bind('<Button-5>', self.on_mousewheel_linux_down)  # Linux scroll down

        self.load_shortcuts()

        self.text_widget.config(state=tk.DISABLED)

    def lighten_color(self, hex_color: str, factor: float) -> str:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))

        return f'#{r:02x}{g:02x}{b:02x}'

    def wrap_command_text(self, command: str, max_width: int = 60) -> list:
        if not self.wrap_mode or self.wrap_mode == tk.NONE:
            return [command]

        if len(command) <= max_width:
            return [command]

        lines = []
        current_line = ""
        words = command.split()

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if len(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines if lines else [command]

    def handle_copy(self, event=None):
        try:
            if self.text_widget.tag_ranges(tk.SEL):
                selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                cleaned_text = re.sub(r'\n\s*↳\t', ' ', selected_text)
                cleaned_text = cleaned_text.replace('  ↳\t', '')
                self.root.clipboard_clear()
                self.root.clipboard_append(cleaned_text)
                return "break"
        except tk.TclError:
            pass

    def load_shortcuts(self):
        try:
            groups = parse_shortcuts_file()

            if not groups:
                self.text_widget.insert(tk.END, "No shortcuts found.\n")
                return

            for i, group in enumerate(groups):
                if i > 0:
                    self.text_widget.insert(tk.END, "\n")

                self.text_widget.insert(tk.END, f"{group.name}\n", 'header')
                self.text_widget.insert(tk.END, "─" * 80 + "\n", 'separator')

                for keybinding, command in group.shortcuts:
                    command_lines = self.wrap_command_text(command)

                    self.text_widget.insert(tk.END, keybinding, 'keybinding')
                    self.text_widget.insert(tk.END, "\t")
                    self.text_widget.insert(tk.END, f"{command_lines[0]}\n", 'command')

                    for continuation_line in command_lines[1:]:
                        self.text_widget.insert(tk.END, "\t")
                        self.text_widget.insert(tk.END, "↳ ", 'wrap_indicator')
                        self.text_widget.insert(tk.END, f"{continuation_line}\n", 'command')

                self.text_widget.insert(tk.END, "\n")

        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load shortcuts: {e}")
            self.root.destroy()

    def open_search(self, event=None):
        self.search_frame.pack(fill=tk.X, side=tk.TOP, before=self.text_widget)
        self.search_entry.focus()
        return "break"

    def close_search(self, event=None):
        self.search_frame.pack_forget()
        self.search_entry.delete(0, tk.END)
        self.clear_search_highlights()
        self.text_widget.focus()
        return "break"

    def handle_escape(self, event=None):
        if self.search_frame.winfo_ismapped():
            self.close_search()
        else:
            self.root.destroy()
        return "break"

    def clear_search_highlights(self):
        self.text_widget.tag_remove('search_highlight', '1.0', tk.END)
        self.text_widget.tag_remove('search_current', '1.0', tk.END)
        self.search_matches = []
        self.current_match_index = -1
        self.search_info.config(text="")

    def on_search_change(self, event=None):
        self.clear_search_highlights()
        query = self.search_entry.get()

        if not query:
            return

        self.text_widget.config(state=tk.NORMAL)

        start = '1.0'
        while True:
            pos = self.text_widget.search(query, start, stopindex=tk.END, nocase=True)
            if not pos:
                break

            end = f"{pos}+{len(query)}c"
            self.text_widget.tag_add('search_highlight', pos, end)
            self.search_matches.append(pos)
            start = end

        self.text_widget.config(state=tk.DISABLED)

        if self.search_matches:
            self.current_match_index = 0
            self.highlight_current_match()
            self.update_search_info()
        else:
            self.search_info.config(text="No matches")

    def highlight_current_match(self):
        if not self.search_matches or self.current_match_index < 0:
            return

        self.text_widget.tag_remove('search_current', '1.0', tk.END)

        pos = self.search_matches[self.current_match_index]
        query = self.search_entry.get()
        end = f"{pos}+{len(query)}c"

        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.tag_add('search_current', pos, end)
        self.text_widget.config(state=tk.DISABLED)

        self.text_widget.see(pos)

    def update_search_info(self):
        if self.search_matches:
            total = len(self.search_matches)
            current = self.current_match_index + 1
            self.search_info.config(text=f"{current}/{total}")
        else:
            self.search_info.config(text="")

    def next_match(self):
        if not self.search_matches:
            return

        self.current_match_index = (self.current_match_index + 1) % len(self.search_matches)
        self.highlight_current_match()
        self.update_search_info()

    def prev_match(self):
        if not self.search_matches:
            return

        self.current_match_index = (self.current_match_index - 1) % len(self.search_matches)
        self.highlight_current_match()
        self.update_search_info()

    def scroll_up(self, event=None):
        self.add_scroll_velocity(-0.08)
        return "break"

    def scroll_down(self, event=None):
        self.add_scroll_velocity(0.08)
        return "break"

    def scroll_page_up(self, event=None):
        self.add_scroll_velocity(-0.8)
        return "break"

    def scroll_page_down(self, event=None):
        self.add_scroll_velocity(0.8)
        return "break"

    def on_mousewheel(self, event):
        # Windows and macOS
        delta = -0.03 * (event.delta / 120)
        self.add_scroll_velocity(delta)
        return "break"

    def on_mousewheel_linux_up(self, event):
        # Linux scroll up
        self.add_scroll_velocity(-0.08)
        return "break"

    def on_mousewheel_linux_down(self, event):
        # Linux scroll down
        self.add_scroll_velocity(0.08)
        return "break"

    def add_scroll_velocity(self, delta):
        self.scroll_velocity += delta
        # Clamp velocity to reasonable bounds
        self.scroll_velocity = max(-2.0, min(2.0, self.scroll_velocity))

        # Start animation if not already running
        if self.scroll_animation_id is None:
            self.animate_scroll()

    def animate_scroll(self):
        if abs(self.scroll_velocity) < 0.001:
            # Animation complete
            self.scroll_velocity = 0
            self.scroll_animation_id = None
            return

        # Get current scroll position
        current_pos = self.text_widget.yview()[0]

        # Calculate new position
        new_pos = current_pos + self.scroll_velocity * 0.02
        new_pos = max(0.0, min(1.0, new_pos))

        # Update view
        self.text_widget.yview_moveto(new_pos)

        # Apply friction/damping
        self.scroll_velocity *= 0.85

        # Continue animation
        self.scroll_animation_id = self.root.after(16, self.animate_scroll)  # ~60 FPS


def main():
    script_dir = Path(__file__).parent.resolve()
    root = tk.Tk()
    root.attributes('-type', 'dialog')
    viewer = ShortcutsViewer(root, script_dir)
    root.mainloop()


if __name__ == "__main__":
    main()
