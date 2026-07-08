"""MPD Service - Wrapper for Music Player Daemon control"""
from mpd import MPDClient
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class MPDService:
    """Service for controlling MPD (Music Player Daemon)"""

    def __init__(self, host: str = "localhost", port: int = 6600):
        self.host = host
        self.port = port
        self.client = MPDClient()
        self._connected = False

    def connect(self) -> bool:
        """Connect to MPD server"""
        try:
            if not self._connected:
                self.client.connect(self.host, self.port)
                self._connected = True
                logger.info(f"Connected to MPD at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MPD: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Disconnect from MPD server"""
        try:
            if self._connected:
                self.client.close()
                self.client.disconnect()
                self._connected = False
                logger.info("Disconnected from MPD")
        except Exception as e:
            logger.error(f"Error disconnecting from MPD: {e}")

    def reconnect(self) -> bool:
        """Reconnect to MPD server"""
        self.disconnect()
        return self.connect()

    # Playback Control
    def play(self, song_pos: Optional[int] = None):
        """Start playback, optionally from specific position in queue"""
        try:
            if song_pos is not None:
                self.client.play(song_pos)
            else:
                self.client.play()
        except Exception as e:
            logger.error(f"Error playing: {e}")
            self.reconnect()

    def pause(self, state: Optional[bool] = None):
        """Pause/unpause playback. If state is None, toggle."""
        try:
            if state is None:
                self.client.pause()
            else:
                self.client.pause(1 if state else 0)
        except Exception as e:
            logger.error(f"Error pausing: {e}")
            self.reconnect()

    def stop(self):
        """Stop playback"""
        try:
            self.client.stop()
        except Exception as e:
            logger.error(f"Error stopping: {e}")
            self.reconnect()

    def next(self):
        """Skip to next track"""
        try:
            self.client.next()
        except Exception as e:
            logger.error(f"Error skipping to next: {e}")
            self.reconnect()

    def previous(self):
        """Go to previous track"""
        try:
            self.client.previous()
        except Exception as e:
            logger.error(f"Error going to previous: {e}")
            self.reconnect()

    def seek(self, time_seconds: int):
        """Seek to position in current song"""
        try:
            self.client.seekcur(time_seconds)
        except Exception as e:
            logger.error(f"Error seeking: {e}")
            self.reconnect()

    # Volume Control
    def set_volume(self, volume: int):
        """Set volume (0-100)"""
        try:
            volume = max(0, min(100, volume))  # Clamp to 0-100
            self.client.setvol(volume)
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            self.reconnect()

    def volume_up(self, amount: int = 5):
        """Increase volume"""
        status = self.get_status()
        if status:
            current = int(status.get('volume', 50))
            self.set_volume(current + amount)

    def volume_down(self, amount: int = 5):
        """Decrease volume"""
        status = self.get_status()
        if status:
            current = int(status.get('volume', 50))
            self.set_volume(current - amount)

    # Playlist Control
    def toggle_random(self):
        """Toggle random/shuffle mode"""
        try:
            status = self.get_status()
            if status:
                current = status.get('random', '0')
                self.client.random(0 if current == '1' else 1)
        except Exception as e:
            logger.error(f"Error toggling random: {e}")
            self.reconnect()

    def toggle_repeat(self):
        """Toggle repeat mode"""
        try:
            status = self.get_status()
            if status:
                current = status.get('repeat', '0')
                self.client.repeat(0 if current == '1' else 1)
        except Exception as e:
            logger.error(f"Error toggling repeat: {e}")
            self.reconnect()

    def toggle_single(self):
        """Toggle single mode"""
        try:
            status = self.get_status()
            if status:
                current = status.get('single', '0')
                self.client.single(0 if current == '1' else 1)
        except Exception as e:
            logger.error(f"Error toggling single: {e}")
            self.reconnect()

    # Queue Management
    def clear_queue(self):
        """Clear the current queue"""
        try:
            self.client.clear()
        except Exception as e:
            logger.error(f"Error clearing queue: {e}")
            self.reconnect()

    def add_to_queue(self, uri: str):
        """Add song/album/playlist to queue"""
        try:
            self.client.add(uri)
        except Exception as e:
            logger.error(f"Error adding to queue: {e}")
            self.reconnect()

    def get_queue(self) -> List[Dict]:
        """Get current queue"""
        try:
            return self.client.playlistinfo()
        except Exception as e:
            logger.error(f"Error getting queue: {e}")
            self.reconnect()
            return []

    # Status and Information
    def get_status(self) -> Optional[Dict]:
        """Get current player status"""
        try:
            return self.client.status()
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            self.reconnect()
            return None

    def get_current_song(self) -> Optional[Dict]:
        """Get currently playing song info"""
        try:
            return self.client.currentsong()
        except Exception as e:
            logger.error(f"Error getting current song: {e}")
            self.reconnect()
            return None

    # Library Browsing
    def get_artists(self) -> List[str]:
        """Get list of all artists"""
        try:
            return self.client.list('artist')
        except Exception as e:
            logger.error(f"Error getting artists: {e}")
            self.reconnect()
            return []

    def get_albums(self, artist: Optional[str] = None) -> List[str]:
        """Get list of albums, optionally filtered by artist"""
        try:
            if artist:
                return self.client.list('album', 'artist', artist)
            return self.client.list('album')
        except Exception as e:
            logger.error(f"Error getting albums: {e}")
            self.reconnect()
            return []

    def get_songs(self, artist: Optional[str] = None, album: Optional[str] = None) -> List[Dict]:
        """Get list of songs, optionally filtered by artist and/or album"""
        try:
            filters = []
            if artist:
                filters.extend(['artist', artist])
            if album:
                filters.extend(['album', album])

            if filters:
                return self.client.find(*filters)
            return self.client.listallinfo()
        except Exception as e:
            logger.error(f"Error getting songs: {e}")
            self.reconnect()
            return []

    def get_playlists(self) -> List[Dict]:
        """Get list of saved playlists"""
        try:
            return self.client.listplaylists()
        except Exception as e:
            logger.error(f"Error getting playlists: {e}")
            self.reconnect()
            return []

    def get_playlist_songs(self, playlist_name: str) -> List[Dict]:
        """Get songs in a specific playlist"""
        try:
            return self.client.listplaylistinfo(playlist_name)
        except Exception as e:
            logger.error(f"Error getting playlist songs: {e}")
            self.reconnect()
            return []

    def load_playlist(self, playlist_name: str):
        """Load a playlist into the queue"""
        try:
            self.client.load(playlist_name)
        except Exception as e:
            logger.error(f"Error loading playlist: {e}")
            self.reconnect()

    # Utility
    def update_database(self):
        """Update MPD music database"""
        try:
            self.client.update()
        except Exception as e:
            logger.error(f"Error updating database: {e}")
            self.reconnect()
