import asyncio
import os
import re
import yt_dlp

DOWNLOAD_DIR = "/tmp/serene_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def download_youtube(url: str, chat_id: int):
    if not re.match(r"^https?://(www\.)?(youtube\.com|youtu\.be)/", url):
        raise ValueError("Please provide a valid YouTube video URL.")
    output = os.path.join(DOWNLOAD_DIR, f"{chat_id}_%(id)s.%(ext)s")
    options = {
        "format": "bestaudio/best",
        "outtmpl": output,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
    }

    def fetch():
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            mp3 = base + ".mp3"
            return mp3, info.get("title", "YouTube audio")

    path, title = await asyncio.to_thread(fetch)
    if not os.path.exists(path):
        raise FileNotFoundError("Audio download did not produce an MP3 file.")
    return path, title
