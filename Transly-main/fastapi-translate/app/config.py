# app/config.py
"""Configuration and setup utilities for the application."""

import os
import shutil
from pathlib import Path

# FFmpeg configuration
FFMPEG_BIN = r"C:\Users\deepu\Downloads\ffmpeg-2025-11-27-git-61b034a47c-full_build\ffmpeg-2025-11-27-git-61b034a47c-full_build\bin"

def setup_ffmpeg():
    """Setup FFmpeg path for audio processing."""
    if Path(FFMPEG_BIN).is_dir():
        os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")
        ffmpeg_path = shutil.which("ffmpeg")
        print(f"✓ FFmpeg found: {ffmpeg_path}")
    else:
        print(f"⚠ FFmpeg path not found: {FFMPEG_BIN}")

def setup_pydub():
    """Configure pydub with FFmpeg converter."""
    try:
        from pydub import AudioSegment
        converter_path = str(Path(FFMPEG_BIN) / "ffmpeg.exe")
        AudioSegment.converter = converter_path
        print(f"✓ pydub converter configured")
    except Exception as e:
        print(f"ℹ pydub setup skipped: {type(e).__name__}")
