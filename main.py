from flask import Flask, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/info/<video_id>', methods=['GET'])
def get_video_info(video_id):
    try:
        # Build the full YouTube URL from the video_id
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Options for yt-dlp (you can add more options if needed)
        ydl_opts = {}

        # Use yt-dlp to extract video information
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)  # download=False prevents downloading the video

            # Prepare video details
            video_info = {
                "title": info.get('title'),
                "uploader": info.get('uploader'),
                "views": info.get('view_count'),
                "duration_seconds": info.get('duration'),
                "description": info.get('description'),
                "thumbnail_url": info.get('thumbnail'),
                "streams": []
            }

            # Loop through available formats and filter for mixed (progressive) streams only
            formats = info.get('formats', [])
            for fmt in formats:
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') != 'none':  # Filter for mixed video and audio
                    stream_info = {
                        "format_id": fmt.get('format_id'),
                        "resolution": fmt.get('format_note'),
                        "file_size": fmt.get('filesize'),
                        "mime_type": fmt.get('ext'),
                        "download_url": fmt.get('url')
                    }
                    video_info["streams"].append(stream_info)

        # Return video details as JSON
        return jsonify(video_info), 200

    except yt_dlp.utils.DownloadError:
        # If yt-dlp can't download or fetch the video info (e.g., invalid video ID or video not available)
        return jsonify({"error": "Unable to retrieve video information. The video may be unavailable or the ID is incorrect."}), 404

    except Exception as e:
        # Catch-all for other exceptions
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
