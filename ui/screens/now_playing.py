from ui.screens.base import Screen
from PIL import ImageDraw

class NowPlayingScreen(Screen):
    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event):
        # Nothing yet
        pass

    def draw(self, draw: ImageDraw.ImageDraw, region):
        x0, y0, x1, y1 = region
        draw.rectangle(region, fill=(0,0,0))
        w = x1 - x0
        h = y1 - y0

        text = "(No Music)"
        text_w, text_h = draw.textsize(text)
        draw.text(
            (x0 + (w - text_w) // 2, y0 + (h - text_h) // 2),
            text,
            fill=(255,255,255)
        )
