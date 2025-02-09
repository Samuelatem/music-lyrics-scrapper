import requests
from bs4 import BeautifulSoup
from utils import create_search_url
import time
import trafilatura

def get_lyrics(artist: str, song: str) -> str | None:
    """
    Scrape lyrics using multiple sources for the given artist and song.
    """
    try:
        # Create the URL for the lyrics page
        url = create_search_url(artist, song)

        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Make the request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Try to get lyrics using trafilatura first
        downloaded = trafilatura.fetch_url(url)
        lyrics = trafilatura.extract(downloaded)

        if lyrics and len(lyrics.strip()) > 0:
            return lyrics.strip()

        # Fallback to BeautifulSoup parsing
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the lyrics div
        lyrics_div = soup.find('div', class_='lyricbox')
        if not lyrics_div:
            lyrics_div = soup.find('div', class_='lyrics')

        if lyrics_div:
            # Extract and clean the lyrics
            lyrics = lyrics_div.get_text().strip()
            return lyrics

        return None

    except Exception as e:
        print(f"Error fetching lyrics: {str(e)}")
        return None

    finally:
        # Add a small delay to be respectful to the website
        time.sleep(1)