import re

def sanitize_input(text: str) -> str:
    """Clean and normalize input text"""
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s-]', '', text)
    text = ' '.join(text.split())
    return text.strip()

def create_search_url(artist: str, song: str) -> str:
    """Create the URL for searching lyrics"""
    # Format artist and song for URL
    artist = artist.lower().replace(' ', '')
    song = song.lower().replace(' ', '')
    
    # Create AZLyrics-style URL
    return f"https://www.azlyrics.com/lyrics/{artist}/{song}.html"
