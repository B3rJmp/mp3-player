from python_mpd2 import MPDClient

class MPDService:
    def __init__(self):
        self._client = MPDClient()
        self._client.timeout = 10
        self._client.idletimeout = None
        self._client.connect("localhost", 6600)

    def status(self):
        return self._client.status()

    def play(self):
        self._client.play()

    def pause(self):
        self._client.pause()

    def stop(self):
        self._client.stop()

    def next(self):
        self._client.next()

    def previous(self):
        self._client.previous()

    def toggle_shuffle(self):
        s = self.status()
        self._client.random(int(not bool(int(s.get("random", 0)))))
    
    def cycle_repeat(self):
        s = self.status()
        repeat = int(s.get("repeat", 0))
        single = int(s.get("single", 0))
        if not repeat:
            self._client.repeat(1)
            self._client.single(0)
        elif repeat and not single:
            self._client.single(1)
        else:
            self._client.repeat(0)
            self._client.single(0)

mpd = MPDService()
