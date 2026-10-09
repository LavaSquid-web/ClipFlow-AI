import os
import shutil
import subprocess
import imageio_ffmpeg
from yt_dlp import YoutubeDL

# Automatically copy the python-managed binary to a standard 'ffmpeg.exe' in your project folder
ffmpeg_source = imageio_ffmpeg.get_ffmpeg_exe()
local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg.exe")
if not os.path.exists(local_ffmpeg):
    shutil.copy(ffmpeg_source, local_ffmpeg)

# Inject current directory into PATH so yt-dlp and subprocess find it immediately
os.environ["PATH"] += os.pathsep + os.getcwd()

def parse_time(time_str):
    if not time_str or not isinstance(time_str, str):
        return 10
    parts = list(map(int, time_str.split(':')))
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return int(parts[0])

def download_and_slice_section(youtube_url, start_time="00:00:10", end_time="00:00:55", output_filename="viral_short.mp4"):
    ydl_opts = {
        'format': 'bv*[ext=mp4]+ba[ext=mp4]/b[ext=mp4]',
        'download_ranges': lambda info, ydl: [{'start_time': parse_time(start_time), 'end_time': parse_time(end_time)}],
        'force_keyframes_at_cuts': True,
        'outtmpl': 'temp_section.mp4',
        'ffmpeg_location': os.getcwd(),
        'extract_flat': False,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    print(f"Extracting section {start_time} to {end_time} directly from YouTube...")
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
        
    print("Converting to vertical 9:16 layout using local FFmpeg...")
    ffmpeg_cmd = [
        local_ffmpeg, '-y',
        '-i', 'temp_section.mp4',
        '-vf', "crop=ih*9/16:ih",
        '-c:v', 'libx264', '-c:a', 'aac',
        output_filename
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"Success! Vertical short saved as {output_filename}")

if __name__ == "__main__":
    url = input("Paste YouTube URL: ").strip()
    start = input("Enter start time [default 00:00:10]: ").strip() or "00:00:10"
    end = input("Enter end time [default 00:00:55]: ").strip() or "00:00:55"
    download_and_slice_section(url, start, end)