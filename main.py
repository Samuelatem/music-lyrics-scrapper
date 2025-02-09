import streamlit as st
import pandas as pd
import speech_recognition as sr
import librosa
import soundfile as sf
from scraper import get_lyrics
from storage import LyricsStore
from utils import sanitize_input, create_search_url
import io
import tempfile
import os

# Initialize the lyrics store
lyrics_store = LyricsStore()
# Initialize speech recognizer
recognizer = sr.Recognizer()

def main():
    st.set_page_config(
        page_title="Lyrics Scraper",
        page_icon="🎵",
        layout="centered"
    )

    st.title("🎵 Lyrics Scraper")
    st.markdown("""
    Search for song lyrics, upload a file with multiple songs, or generate lyrics from audio files.
    """)

    # Create tabs for different functionality
    search_tab, upload_tab, audio_tab = st.tabs(["Search Lyrics", "Batch Upload", "Audio to Lyrics"])

    with search_tab:
        show_search_interface()

    with upload_tab:
        show_upload_interface()

    with audio_tab:
        show_audio_interface()

def process_audio_file(audio_file):
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        tmp_file.write(audio_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Load audio file using librosa
        audio, sr = librosa.load(tmp_path)

        # Export as WAV for speech recognition
        sf.write(tmp_path, audio, sr)

        # Perform speech recognition
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            lyrics = recognizer.recognize_google(audio_data)

        # Clean up temporary file
        os.unlink(tmp_path)

        return lyrics
    except Exception as e:
        # Clean up temporary file
        os.unlink(tmp_path)
        raise e

def show_audio_interface():
    st.markdown("Upload an audio file to generate lyrics")

    audio_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "m4a"])

    if audio_file is not None:
        with st.spinner("Processing audio and generating lyrics..."):
            try:
                lyrics = process_audio_file(audio_file)

                # Display the generated lyrics
                st.subheader("Generated Lyrics")
                st.markdown("---")
                st.markdown(lyrics, unsafe_allow_html=False)

                # Option to save the lyrics
                if st.button("Save Lyrics"):
                    # Extract filename without extension as song title
                    song_title = os.path.splitext(audio_file.name)[0]
                    lyrics_store.save_lyrics("Unknown Artist", song_title, lyrics)
                    st.success(f"Lyrics saved for song: {song_title}")

            except Exception as e:
                st.error(f"Error processing audio file: {str(e)}")

def show_search_interface():
    col1, col2 = st.columns(2)

    with col1:
        artist = st.text_input("Artist Name")
    with col2:
        song = st.text_input("Song Title")

    if st.button("Search Lyrics", type="primary"):
        if not artist or not song:
            st.error("Please enter both artist name and song title")
            return

        artist = sanitize_input(artist)
        song = sanitize_input(song)

        # Check cache first
        cached_lyrics = lyrics_store.get_lyrics(artist, song)
        if cached_lyrics:
            display_lyrics(artist, song, cached_lyrics)
            return

        with st.spinner("Fetching lyrics..."):
            try:
                lyrics = get_lyrics(artist, song)
                if lyrics:
                    lyrics_store.save_lyrics(artist, song, lyrics)
                    display_lyrics(artist, song, lyrics)
                else:
                    st.error("Lyrics not found. Please check the artist name and song title.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def show_upload_interface():
    st.markdown("Upload a CSV file with columns: 'artist' and 'song'")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if 'artist' not in df.columns or 'song' not in df.columns:
                st.error("CSV must contain 'artist' and 'song' columns")
                return

            results = []
            progress_bar = st.progress(0)

            for idx, row in df.iterrows():
                progress = (idx + 1) / len(df)
                progress_bar.progress(progress)

                artist = sanitize_input(row['artist'])
                song = sanitize_input(row['song'])

                # Check cache first
                lyrics = lyrics_store.get_lyrics(artist, song)
                if not lyrics:
                    try:
                        lyrics = get_lyrics(artist, song)
                        if lyrics:
                            lyrics_store.save_lyrics(artist, song, lyrics)
                    except Exception:
                        lyrics = "Error fetching lyrics"

                results.append({
                    'artist': artist,
                    'song': song,
                    'lyrics': lyrics if lyrics else "Not found"
                })

            # Create results DataFrame
            results_df = pd.DataFrame(results)

            # Convert to CSV for download
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Download Results",
                data=csv,
                file_name="lyrics_results.csv",
                mime="text/csv"
            )

            # Display results in the UI
            st.subheader("Results")
            for result in results:
                with st.expander(f"{result['artist']} - {result['song']}"):
                    st.text(result['lyrics'])

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def display_lyrics(artist, song, lyrics):
    st.subheader(f"{artist} - {song}")
    st.markdown("---")
    st.markdown(lyrics, unsafe_allow_html=False)

if __name__ == "__main__":
    main()