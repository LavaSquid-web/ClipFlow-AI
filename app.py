import os
import shutil
import subprocess
import imageio_ffmpeg
from yt_dlp import YoutubeDL
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.', template_folder='.')

ffmpeg_source = imageio_ffmpeg.get_ffmpeg_exe()
local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg.exe")
if not os.path.exists(local_ffmpeg):
    shutil.copy(ffmpeg_source, local_ffmpeg)

os.environ["PATH"] += os.pathsep + os.getcwd()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('.', filename, as_attachment=True)

@app.route('/api/process', methods=['POST'])
def process_video():
    data = request.json
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({'error': 'No YouTube URL provided'}), 400

    full_video_path = "full_source.mp4"

    clips_config = [
        {'start': 10,  'duration': 20, 'name': 'viral_short_1.mp4'},
        {'start': 45,  'duration': 20, 'name': 'viral_short_2.mp4'},
        {'start': 80,  'duration': 20, 'name': 'viral_short_3.mp4'},
        {'start': 120, 'duration': 20, 'name': 'viral_short_4.mp4'},
        {'start': 160, 'duration': 20, 'name': 'viral_short_5.mp4'}
    ]

    generated_files = []

    try:
        if os.path.exists(full_video_path):
            os.remove(full_video_path)

        ydl_opts = {
        'format': 'best',  # <--- Changed to 'best' for maximum compatibility
        'outtmpl': full_video_path,
        'ffmpeg_location': os.getcwd(),
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'cookiefile': 'cookies.txt'
    }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        if not os.path.exists(full_video_path):
            return jsonify({'error': 'Failed to download source video from YouTube.'}), 500

        for clip in clips_config:
            output_filename = clip['name']
            if os.path.exists(output_filename):
                os.remove(output_filename)

            ffmpeg_cmd = [
                os.path.join(os.getcwd(), 'ffmpeg.exe'),
                '-y',
                '-ss', str(clip['start']),
                '-i', full_video_path,
                '-t', str(clip['duration']),
                '-vf', "crop=ih*(9/16):ih",
                '-c:v', 'libx264',
                '-crf', '23',
                '-c:a', 'aac',
                output_filename
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            
            if os.path.exists(output_filename):
                generated_files.append(output_filename)

        if not generated_files:
            return jsonify({'error': 'Failed to generate any video clips.'}), 500

        return jsonify({
            'success': True,
            'files': generated_files
        })

    except Exception as e:
        print(f"Error processing video package: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    