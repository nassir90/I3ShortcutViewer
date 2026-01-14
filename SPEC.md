# Shortcut Viewer



## Introduction

I want to be able to view the shortcuts that I have enabled in i3 without actually looking at the shortcuts file that I have. In this case, my shortcuts file is stored in `~/.config/i3/shortcuts`. Can you make a nice UI that shows my shortcuts.


### Data Source

Categories should be marked by triple comments `(###)`. In the UI, the font used for category headings should be larger than the regular font.


### Search

You should be able to search through the shortcuts UI in the shortcuts viewer using the `/` key.


### Style

The UI should attempt to read and parse my alacritty.toml file for main colors and font. I.e. the background should be the same as my terminal background, the font should be my terminal font. This should be a dynamic process which reads the alacritty config file at startup and initialises the colors that should be used by the application. Only the colors should be inherited, not the font size.


### Configuration

There should be a configuration file that is either read from `i3-shortcut-viewer.toml` in the current directory or `~/.config/i3-shortcut-viewer/config.toml`. It should allow the user to configure the font size used for the application via a `[font] size = ...` parameter.


### Layout

By default text shouldn't overflow. If possible the window should expand to fit the length of the shortcut commands OR it should wrap over. There should be a "`wrap_command`" option in the config file to configure this. Wrapping behaviour should be such that the command text remains in the right hand column as opposed to wrapping at the very left where the key binding is. Where text has wrapped, there should be an indicator at the left that's an arrow emoji pointing down then right that should be stripped when copying. These likewise should not start at the very left and instead stay in the column of the command. The arrow should start in the right hand side column where the command text starts instead of starting in the left hand side column under where the keybinding is declared.


### Navigation

You should be able to scroll using the mouse, arrow keys, page up buttons and C-n and C-p keys (emacs). Scrolling should feel fluid and soft like in a web browser as opposed to being done in jumps.

Pressing the escape key should exit the application.


### Executing Commands

Hovering over the command of a keybinding highlights the entire row. Clicking on such a row should execute the command.


## Preparing your Shortcuts File

This script works better when you categorise your shortcuts.

Separate the user shortcuts that you care about into a smaller "shortcuts" file that you import from your main i3 config file as follows:

    include shortcuts

Ask your agent to look at the config file, reproduce it with everything categoriesd under `(###)` hheaders and make sure that it makes a python script that ensures that no shortcuts have been left behind by the categorisation. Copy the new file to your shortcuts file.


### Example of a Config File

    ### Apps
    $mod+a alacritty
    
    ### Commands
    $mod+BrightnessDown brightness_cli -10

