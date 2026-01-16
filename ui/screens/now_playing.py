from .base import Screen
from services.mpd import mpd
from PIL import ImageDraw

class NowPlayingScreen(Screen):
    NAME = "Now Playing"

    def handle_event(self, event):
        if event.type == "button" and event.pressed:
            if event.button == "BTN1":
                mpd.previous()
            elif event.button == "BTN2":
                mpd.play()
            elif event.button == "BTN3":
                mpd.stop()
            elif event.button == "BTN4":
                mpd.next()

    def draw(self, draw: ImageDraw.ImageDraw, region):
        x0, y0, x1, y1 = region
        draw.rectangle(region, fill="black")

        status = mpd.status()
        song = status.get("title", "Unknown Track")
        artist = status.get("artist", "Unknown Artist")

        draw.text((x0+10, y0+10), song, fill="white")
        draw.text((x0+10, y0+30), artist, fill="white")
