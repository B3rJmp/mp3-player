# MP3 Player Interface

A Python-based interface for controlling MPD (Music Player Daemon) on a Raspberry Pi with:
- ST7789 320x240 LCD display (via Luma)
- NeoKey 1x4 RGB button pad (4 context-aware buttons)
- Rotary encoder with push button

## Features

### Screens
- **Now Playing**: Shows current song, playback controls, progress bar, volume
- **Artists**: Browse all artists in your music library
- **Albums**: Browse albums (all or filtered by artist)
- **Songs**: Browse songs (all or filtered by artist/album)
- **Playlists**: Browse and load saved MPD playlists
- **Playlist Songs**: View songs in a specific playlist

### Navigation
The interface uses a **screen stack** system like mobile apps - screens preserve their state when navigating away.

### Hardware Controls

#### NeoKey Buttons (Context-Aware)
Buttons change function based on the current screen, with LED colors indicating their purpose:

**Now Playing Screen:**
- Button 1 (Cyan): Menu - Open artists browser
- Button 2 (Yellow): Previous track
- Button 3 (Green/Blue): Play/Pause toggle
- Button 4 (Yellow): Next track

**Browse Screens (Artists/Albums/Playlists):**
- Button 1 (Red): Back - Return to previous screen
- Button 2 (Yellow): View Albums/Songs (context-dependent)
- Button 3 (Green): View Songs/Play
- Button 4 (Cyan): Navigate to Playlists

**Songs Screen:**
- Button 1 (Red): Back
- Button 2 (Green): Play selected song
- Button 3 (Yellow): Add song to queue
- Button 4 (Blue): Play all songs

#### Rotary Encoder (Context-Aware)
**Now Playing Screen:**
- Rotate: Volume up/down
- Press: Toggle shuffle

**Browse Screens:**
- Rotate: Scroll through list
- Press: Select item (same as main action button)

## Architecture

```
claude/
├── app.py                    # Main application controller
├── main.py                   # Entry point
├── services/
│   └── mpd_service.py        # MPD wrapper
├── core/
│   ├── input_manager.py      # Hardware input handling
│   └── screen_stack.py       # Screen navigation management
└── ui/
    ├── base_screen.py        # Base class for all screens
    └── screens/
        ├── now_playing.py    # Now playing screen
        ├── artists.py        # Artists browser
        ├── albums.py         # Albums browser
        ├── songs.py          # Songs browser
        ├── playlists.py      # Playlists browser
        └── playlist_songs.py # Playlist songs viewer
```

## Running the Application

### Prerequisites
1. MPD installed and running
2. All required Python packages (see `requirements.txt`)
3. Hardware properly connected:
   - ST7789 display on SPI0 (DC=GPIO25, RST=GPIO24)
   - NeoKey on I2C address 0x30
   - Rotary encoder on I2C address 0x36

### Start the Application

```bash
# Basic usage (connects to localhost:6600)
python3 claude/main.py

# With custom MPD host
python3 claude/main.py --mpd-host 192.168.1.100

# With debug logging
python3 claude/main.py --log-level DEBUG
```

### Command Line Options

```
--mpd-host HOST    MPD server host (default: localhost)
--mpd-port PORT    MPD server port (default: 6600)
--log-level LEVEL  Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
```

## Development Notes

### Adding New Screens

1. Create a new file in `claude/ui/screens/`
2. Inherit from `BaseScreen`
3. Implement required methods:
   - `on_enter()`: Called when screen becomes active
   - `on_exit()`: Called when screen is deactivated
   - `render(draw)`: Draw screen content
   - `handle_button(button_index)`: Handle button presses
   - `handle_encoder_rotate(delta)`: Handle encoder rotation (optional)
   - `handle_encoder_press()`: Handle encoder press (optional)

4. Configure button labels and colors:
   ```python
   self.set_button_config(
       labels=["Back", "Action1", "Action2", "Action3"],
       colors=[self.COLOR_RED, self.COLOR_GREEN, ...]
   )
   ```

### Screen Navigation

```python
# Push new screen onto stack
self.app.screen_stack.push(NewScreen(self.app))

# Go back to previous screen
self.app.screen_stack.pop()

# Return to root (Now Playing)
self.app.screen_stack.pop_to_root()

# Replace entire stack
self.app.screen_stack.replace_all(NewScreen(self.app))
```

### Rendering

Screens automatically re-render when:
- `request_render()` is called
- Screen enters (via `on_enter()`)

The base screen provides helper methods:
- `draw_text()`: Draw text with alignment and truncation
- `draw_header()`: Standard header bar
- `draw_scrollbar()`: Scrollbar for lists
- `format_time()`: Format seconds as MM:SS
- `truncate_text()`: Truncate text to fit width

## Hardware Configuration

### Display (ST7789)
- Resolution: 320x240
- SPI Port: 0, Device: 0
- Bus Speed: 40 MHz
- DC Pin: GPIO 25
- RST Pin: GPIO 24

### NeoKey 1x4
- I2C Address: 0x30
- 4 mechanical switches with RGB LEDs

### Rotary Encoder
- I2C Address: 0x36 (via Seesaw)
- Incremental encoder with push button
- Button on Seesaw pin 24 (active low)

## Logs

Application logs are written to:
- Console (stdout)
- `/tmp/mp3player.log`

## Troubleshooting

### Display not working
- Check SPI is enabled: `sudo raspi-config` → Interface Options → SPI
- Verify pin connections (DC=25, RST=24)
- Check bus speed in app.py if display is garbled

### NeoKey not responding
- Verify I2C is enabled: `sudo raspi-config` → Interface Options → I2C
- Check I2C address: `i2cdetect -y 1` (should show 0x30)
- Test with `tests/i2c_test.py`

### Rotary encoder not responding
- Check I2C address: `i2cdetect -y 1` (should show 0x36)
- Test with `tests/rotary_test.py`

### MPD connection failed
- Check MPD is running: `systemctl status mpd`
- Verify MPD is listening: `netstat -ln | grep 6600`
- Test connection: `mpc status`

## License

See project root for license information.
