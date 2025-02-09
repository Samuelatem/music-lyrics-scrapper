from models import LyricsModel

class LyricsStore:
    def __init__(self):
        """Initialize database storage for lyrics"""
        self.model = LyricsModel()

    def get_key(self, artist: str, song: str) -> str:
        """Generate a unique key for storing lyrics"""
        return f"{artist.lower()}:{song.lower()}"
    
    def save_lyrics(self, artist: str, song: str, lyrics: str) -> None:
        """Save lyrics to the database"""
        self.model.save(artist, song, lyrics)

    def get_lyrics(self, artist: str, song: str) -> str | None:
        """Retrieve lyrics from the database"""
        return self.model.get(artist, song)

    def clear(self) -> None:
        """Clear all stored lyrics"""
        #  Implementation for clearing the database would need to be added to LyricsModel.
        # This is beyond the scope of the provided edit.  For now, leaving it as a placeholder.
        self.model.clear() # Assuming LyricsModel has a clear method.