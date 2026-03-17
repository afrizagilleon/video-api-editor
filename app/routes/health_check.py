# ============================================================================
# HEALTH CHECK
# ============================================================================

from flask import jsonify
from datetime import datetime
from utils import state, check_ffmpeg, check_auto_editor

from . import api_bp

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Check API health and available features"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'moviepy': state.MOVIEPY_AVAILABLE,
            'whisper': state.WHISPER_AVAILABLE,
            'ffmpeg': check_ffmpeg(),
            'auto_editor': check_auto_editor()
        }
    })