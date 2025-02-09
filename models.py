from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
import os

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
        self.create_tables()
    
    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS lyrics (
                    id SERIAL PRIMARY KEY,
                    artist VARCHAR(255) NOT NULL,
                    song VARCHAR(255) NOT NULL,
                    lyrics TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(artist, song)
                )
            """)
            self.conn.commit()
    
    def close(self):
        self.conn.close()

class LyricsModel:
    def __init__(self):
        self.db = Database()
    
    def save(self, artist: str, song: str, lyrics: str) -> bool:
        try:
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO lyrics (artist, song, lyrics)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (artist, song) DO UPDATE
                    SET lyrics = EXCLUDED.lyrics
                """, (artist, song, lyrics))
                self.db.conn.commit()
                return True
        except Exception as e:
            print(f"Error saving lyrics: {e}")
            return False
    
    def get(self, artist: str, song: str) -> str | None:
        try:
            with self.db.conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT lyrics FROM lyrics
                    WHERE artist = %s AND song = %s
                """, (artist, song))
                result = cur.fetchone()
                return result['lyrics'] if result else None
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            return None
