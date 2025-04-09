import os
import threading
from flask import Flask, render_template, request, redirect, url_for, flash
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import yt_dlp
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Used for flashing messages
socketio = SocketIO(app)

# ------------------------------------------------------------------
# Configuration Section
# ------------------------------------------------------------------
# Hardcoded Spotify API credentials (for personal testing only)
CLIENT_ID = "Your Client ID"
CLIENT_SECRET = "Your Client Secret"

# FFmpeg location (update this if needed)
FFMPEG_LOCATION = r"C:\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin"

# Set up Spotify client using Client Credentials Flow (for public playlists)
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(auth_manager=auth_manager)

def get_playlist_details(playlist_id: str):
    """
    Retrieves the playlist name and track queries from the Spotify playlist.
    Each track query is in the format "Artist - Track Name".
    Returns a tuple (playlist_name, track_list).
    """
    try:
        # Retrieve both the name and the tracks.
        results = spotify.playlist(
            playlist_id, 
            fields="name,tracks.items(track(name,artists(name)))", 
            market="CA"
        )
    except Exception as e:
        return f"Error retrieving playlist: {e}", []
    
    playlist_name = results.get("name", "Unknown_Playlist")
    track_list = []
    for item in results["tracks"]["items"]:
        track = item["track"]
        if track:
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            query = f"{artist_name} - {track_name}"
            track_list.append(query)
    return playlist_name, track_list

def download_mp3_from_youtube(query: str, folder: str):
    """
    Searches YouTube for the given query and downloads the audio as an MP3.
    Saves the file inside the given folder.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        # Disable creation of .part files to reduce file locking issues on Windows.
        "nopart": True,
        # Save the file in the specified folder using its title and the extension
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "ffmpeg_location": FFMPEG_LOCATION,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    }
    try:
        videos_search = VideosSearch(query, limit=1)
        result = videos_search.result()
        if result and result.get("result"):
            youtube_url = result["result"][0]["link"]
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            return f"Downloaded MP3 for: {query}"
        else:
            return f"No video found for: {query}"
    except Exception as e:
        return f"Error downloading audio for {query}: {e}"

def download_playlist_background(playlist_input: str):
    """
    Background function that downloads each track and emits a Socket.IO event after each download.
    """
    if "open.spotify.com/playlist/" in playlist_input:
        playlist_id = playlist_input.split("open.spotify.com/playlist/")[-1].split("?")[0]
    else:
        playlist_id = playlist_input

    playlist_name, track_list = get_playlist_details(playlist_id)
    if "Error" in playlist_name:
        socketio.emit('download_complete', {'message': f"Error retrieving playlist: {playlist_name}"})
        return

    # Sanitize folder name (remove spaces and special characters if needed)
    folder_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in playlist_name)
    os.makedirs(folder_name, exist_ok=True)

    for query in track_list:
        message = download_mp3_from_youtube(query, folder_name)
        # Emit a Socket.IO event for each song that finishes downloading
        socketio.emit('download_complete', {'message': message})
    socketio.emit('download_complete', {'message': "Operation complete."})

@app.route("/download", methods=["POST"])
def download():
    playlist_input = request.form.get("playlist").strip()
    # Start a background thread for the download process
    threading.Thread(target=download_playlist_background, args=(playlist_input,)).start()
    return {"status": "Download started"}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)
