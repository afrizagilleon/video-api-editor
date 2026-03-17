"""
Flask Video Editing API - CORRECTED for MoviePy 2.x
Support: MoviePy 2.0+, auto-editor, faster-whisper
"""

from flask import Flask
from pathlib import Path

from utils import state, check_ffmpeg, check_auto_editor

# ============================================================================
# MOVIEPY 2.x IMPORTS (CRITICAL FIX)
# ============================================================================
try:
    # MoviePy 2.x uses direct imports, NOT moviepy.editor
    from moviepy import (
        VideoFileClip,
        concatenate_videoclips,
        vfx
    )
    state.MOVIEPY_AVAILABLE = True
    print("✅ MoviePy imported successfully")
except ImportError as e:
    state.MOVIEPY_AVAILABLE = False
    print(f"⚠️  MoviePy import failed: {e}")

# ============================================================================
# FASTER-WHISPER IMPORTS
# ============================================================================
try:
    from faster_whisper import WhisperModel
    state.WHISPER_AVAILABLE = True
    print("✅ faster-whisper imported successfully")
except ImportError as e:
    state.WHISPER_AVAILABLE = False
    print(f"⚠️  faster-whisper import failed: {e}")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Create directories
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🎬 Flask Video Editing API v2.0 (MoviePy 2.x Compatible)")
    print("=" * 60)
    print(f"MoviePy: {'✅ Available' if state.MOVIEPY_AVAILABLE else '❌ Not installed'}")
    print(f"Whisper: {'✅ Available' if state.WHISPER_AVAILABLE else '❌ Not installed'}")
    print(f"FFmpeg: {'✅ Available' if check_ffmpeg() else '❌ Not installed'}")
    print(f"auto-editor: {'✅ Available' if check_auto_editor() else '❌ Not installed'}")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("=" * 60)
    
    from routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    app.run(debug=True, host='0.0.0.0', port=5000)
    
