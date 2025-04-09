# Spotify-Playlist-to-MP3-Downloader

Spotify-Playlist-to-MP3-Downloader is a web application built with Flask that allows users to convert their favorite Spotify playlists into downloadable MP3 files. The app retrieves track information from Spotify, searches for corresponding audio on YouTube, and uses yt-dlp to download and convert the videos into MP3 files. All MP3 files are saved in a folder named after the Spotify playlist.

## Key Features

- **Spotify Integration:**  
  Uses the Spotify API (via Spotipy) to fetch details such as track names and artist information from a given Spotify playlist. The application supports input as either the full Spotify playlist URL or the pure playlist ID.

- **YouTube Search and Audio Download:**  
  For each track in the playlist, the app constructs a search query (formatted as "Artist - Track Name") and uses the youtube-search-python package (VideosSearch) to find the best matching YouTube video. Then, it downloads the video’s audio using yt-dlp and extracts it as an MP3 file using FFmpeg.

- **Folder Creation:**  
  The application automatically creates a directory with the Spotify playlist’s name (after sanitization to remove invalid folder characters) to store all the downloaded MP3 files.

- **Real-Time Status Updates:**  
  With the integration of Flask-SocketIO, the app provides live progress updates to the user, displaying status messages (like when each track is found, when a download starts, and when it finishes) on a dedicated download page.

## How It Works

1. **User Input:**  
   The user is presented with a simple web form where they enter a Spotify playlist URI, link, or pure ID. The application then extracts the pure playlist ID from the input.

2. **Fetching Playlist Details:**  
   Using Spotipy with the Client Credentials Flow, the application retrieves the playlist’s metadata, including the playlist name and a list of tracks. For each track, it extracts the track’s name and the primary artist, formatting the information as "Artist - Track Name" for further processing.

3. **Creating a Download Folder:**  
   The app sanitizes the playlist name (removing or replacing characters that are not allowed in folder names) and creates a directory with that name. This folder is where all the MP3 files will be saved.

4. **Searching and Downloading Audio:**  
   For every track in the playlist, the app uses the formatted query to search YouTube for a corresponding video. Once a match is found, yt-dlp downloads the best available audio stream and uses FFmpeg to convert it to an MP3 file. The resulting MP3 is saved in the designated folder.

5. **Live Feedback with SocketIO:**  
   Throughout the process, the backend sends real-time status updates to the frontend using SocketIO. This allows the user to see ongoing messages such as “Searching YouTube for: …”, “Downloading MP3 for: …”, and “Finished downloading: …” on the web page.

## Project Structure

- **app.py:**  
  The main Flask application file that contains all the logic for retrieving Spotify playlist details, downloading audio from YouTube, saving files, and providing real-time updates via SocketIO.

- **templates/index.html:**  
  The landing page that hosts the playlist input form. It features a modern, responsive design using Tailwind CSS.

- **templates/download.html:**  
  The status page that displays real-time progress messages during the download process. This page updates dynamically as the backend emits events via SocketIO.

- **requirements.txt:**  
  A file listing all Python package dependencies (e.g., Flask, flask-socketio, spotipy, yt-dlp, youtube-search-python).

## Installation and Setup

1. **Clone the Repository:**  
   Clone this repository to your local machine.

2. **Install Dependencies:**  
   It is recommended to use a virtual environment. Then, install the required packages using:
   ```bash
   pip install -r requirements.txt
