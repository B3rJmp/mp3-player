# Screen Migration Guide

All browse screens need to be updated to use the new action bar system. Here are the required changes:

## Changes Required for Each Screen

### 1. Add ActionIcon Import
```python
# OLD:
from claude.ui.base_screen import BaseScreen

# NEW:
from claude.ui.base_screen import BaseScreen
from claude.ui.action_bar import ActionIcon
```

### 2. Replace set_button_config with configure_action_bar
```python
# OLD:
self.set_button_config(
    labels=["Back", "Play", "Queue", "Songs"],
    colors=[self.COLOR_RED, self.COLOR_GREEN, self.COLOR_YELLOW, self.COLOR_CYAN]
)

# NEW:
self.configure_action_bar(
    icons=[ActionIcon.BACK, ActionIcon.PLAY, ActionIcon.QUEUE, ActionIcon.SONGS],
    colors=[self.COLOR_RED, self.COLOR_GREEN, self.COLOR_YELLOW, self.COLOR_CYAN]
)
```

### 3. Rename render() to render_content()
```python
# OLD:
def render(self, draw: ImageDraw.ImageDraw):
    """Render screen"""

# NEW:
def render_content(self, draw: ImageDraw.ImageDraw):
    """Render screen content"""
```

### 4. Update Background Rectangle Y-Coordinate
```python
# OLD:
draw.rectangle(
    [(0, 0), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
    fill=self.COLOR_BLACK
)

# NEW:
draw.rectangle(
    [(0, self.CONTENT_Y_START), (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)],
    fill=self.COLOR_BLACK
)
```

### 5. Replace draw_header() with draw_title_bar()
```python
# OLD:
self.draw_header(draw, "Artists")

# NEW (optional - for screens that want a title bar):
self.draw_title_bar(draw, "Artists")
```

### 6. Update List Starting Y-Position
```python
# OLD:
y_start = 40  # Below old header

# NEW:
y_start = self.CONTENT_Y_START + 10  # Below action bar, or
y_start = self.CONTENT_Y_START + 30  # Below action bar + title bar if using one
```

### 7. Navigation Changes: Push Now Playing on Top When Playing
```python
# OLD (in songs/albums screens when playing):
self.app.screen_stack.pop_to_root()  # Return to now playing at root

# NEW:
# Now playing should be pushed on TOP when user selects a song
from claude.ui.screens.now_playing import NowPlayingScreen
# First start playback
self.mpd.play(0)
# Then push now playing on top of current screen
self.app.screen_stack.push(NowPlayingScreen(self.app))
```

## Icon Mapping Reference

Common button actions to icon mappings:

| Button Label | ActionIcon |
|--------------|------------|
| Back | `ActionIcon.BACK` |
| Menu | `ActionIcon.MENU` |
| Play | `ActionIcon.PLAY` |
| Pause | `ActionIcon.PAUSE` |
| Stop | `ActionIcon.STOP` |
| Next | `ActionIcon.NEXT` |
| Previous | `ActionIcon.PREVIOUS` |
| Albums | `ActionIcon.ALBUMS` |
| Songs | `ActionIcon.SONGS` |
| Playlists | `ActionIcon.PLAYLISTS` |
| Artists | `ActionIcon.ARTISTS` |
| Bluetooth | `ActionIcon.BLUETOOTH` |
| Queue | `ActionIcon.QUEUE` |
| Shuffle | `ActionIcon.SHUFFLE` |
| Repeat | `ActionIcon.REPEAT` |
| (Empty) | `ActionIcon.NONE` |

## Files That Need Updates

- [ ] `claude/ui/screens/artists.py`
- [ ] `claude/ui/screens/albums.py`
- [ ] `claude/ui/screens/songs.py`
- [ ] `claude/ui/screens/playlists.py`
- [ ] `claude/ui/screens/playlist_songs.py`

## Example: Full Artists Screen Update

### Before:
```python
def __init__(self, app):
    super().__init__(app)
    self.set_button_config(
        labels=["Back", "Albums", "Songs", "Lists"],
        colors=[self.COLOR_RED, self.COLOR_YELLOW, self.COLOR_GREEN, self.COLOR_CYAN]
    )

def render(self, draw):
    draw.rectangle([(0, 0), (320, 240)], fill=self.COLOR_BLACK)
    self.draw_header(draw, "Artists")
    y_start = 40
    # ... rest of rendering
```

### After:
```python
from claude.ui.action_bar import ActionIcon

def __init__(self, app):
    super().__init__(app)

def on_enter(self):
    super().on_enter()
    self.configure_action_bar(
        icons=[ActionIcon.BACK, ActionIcon.ALBUMS, ActionIcon.SONGS, ActionIcon.PLAYLISTS],
        colors=[self.COLOR_RED, self.COLOR_YELLOW, self.COLOR_GREEN, self.COLOR_CYAN]
    )
    self.load_artists()

def render_content(self, draw):
    draw.rectangle([(0, self.CONTENT_Y_START), (320, 240)], fill=self.COLOR_BLACK)
    self.draw_title_bar(draw, f"Artists ({len(self.artists)})")
    y_start = self.CONTENT_Y_START + 30
    # ... rest of rendering
```

## Testing Checklist

After updating screens, verify:

1. Action bar shows correct icons for each screen
2. Button LEDs match icon colors
3. Content starts below action bar (not overlapping)
4. Scrolling works correctly with new coordinates
5. Navigation flow: encoder click on now_playing goes to menu
6. Playing a song pushes now_playing on top of browse screen
7. Back button returns to previous browse screen from now_playing
