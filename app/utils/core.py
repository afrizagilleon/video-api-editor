# utils/core.py
from functools import wraps
from flask import current_app, jsonify
import subprocess

def allowed_file(filename: str) -> bool:
    exts = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in exts


def require_library(library_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from .state import MOVIEPY_AVAILABLE, WHISPER_AVAILABLE

            if library_name == "moviepy" and not MOVIEPY_AVAILABLE:
                return jsonify({"error": "MoviePy not installed"}), 500
            if library_name == "whisper" and not WHISPER_AVAILABLE:
                return jsonify({"error": "faster-whisper not installed"}), 500
            return f(*args, **kwargs)

        return decorated_function

    return decorator

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE,
                      timeout=5)
        return True
    except:
        return False

def check_auto_editor():
    """Check if auto-editor is installed"""
    try:
        subprocess.run(['auto-editor', '--version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE,
                      timeout=5)
        return True
    except:
        return False

