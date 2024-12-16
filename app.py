from flask import Flask, render_template, request, send_file, jsonify
from flask_socketio import SocketIO, emit
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
socketio = SocketIO(app)

# Ensure the uploads and downloads directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("downloads", exist_ok=True)


# Home Route
@app.route("/")
def home():
    return render_template("index.html")


# Route for uploading cookies file
@app.route("/upload-cookies", methods=["POST"])
def upload_cookies():
    cookies_file = request.files.get("cookies")
    if cookies_file:
        save_path = os.path.join("uploads", "youtube_cookies.txt")
        cookies_file.save(save_path)
        return jsonify({"success": "Cookies file uploaded successfully."}), 200
    return jsonify({"error": "No cookies file uploaded."}), 400


# Progress update hook for yt-dlp
def progress_hook(d):
    if d["status"] == "downloading":
        progress = d.get("_percent_str", "0%")
        eta = d.get("eta", "Unknown")
        socketio.emit("progress", {"progress": progress.strip(), "eta": eta})


# Route for downloading video/audio
@app.route("/download", methods=["POST"])
def download():
    try:
        youtube_url = request.form.get("url")
        download_type = request.form.get("type")  # 'video' or 'audio'
        cookies_file_path = os.path.join("uploads", "youtube_cookies.txt")

        # Check if cookies file exists
        if not os.path.exists(cookies_file_path):
            return (
                jsonify({"error": "No cookies file found. Please upload one first."}),
                400,
            )

        # Output template for downloaded files
        output_template = "downloads/%(title)s.%(ext)s"

        # Set options based on user choice
        if download_type == "video":
            options = {
                "format": "bestvideo[height<=1080]+bestaudio/best",
                "outtmpl": output_template,
                "cookiefile": cookies_file_path,
                "progress_hooks": [progress_hook],
            }
        elif download_type == "audio":
            options = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "cookiefile": cookies_file_path,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "progress_hooks": [progress_hook],
            }
        else:
            return jsonify({"error": "Invalid download type!"}), 400

        # Download video/audio using yt-dlp
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            file_path = ydl.prepare_filename(info)
            if download_type == "audio":
                file_path = file_path.replace(".webm", ".mp3")  # Adjust for audio

        # Send the downloaded file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the app
if __name__ == "__main__":
    socketio.run(app, debug=True)
