# ============================================================================
# ADD SUBTITLES TO VIDEO

# ============================================================================

from flask import request, jsonify, send_file, current_app as app
from werkzeug.utils import secure_filename
import os
import uuid
import subprocess

from utils import allowed_file, check_ffmpeg

from . import api_bp

@api_bp.route('/add-subtitles', methods=['POST'])
def add_subtitles():
    """Burn subtitles using FFmpeg"""
    if not check_ffmpeg():
        return jsonify({'error': 'FFmpeg not installed'}), 500

    if 'video' not in request.files or 'subtitle' not in request.files:
        return jsonify({'error': 'Video and subtitle required'}), 400

    video_file = request.files['video']
    subtitle_file = request.files['subtitle']

    if video_file.filename == '' or subtitle_file.filename == '':
        return jsonify({'error': 'Invalid files'}), 400

    fontsize = request.form.get('fontsize', '24')
    color = request.form.get('color', 'white')

    video_filename = secure_filename(video_file.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{video_filename}")
    video_file.save(video_path)

    subtitle_filename = secure_filename(subtitle_file.filename)
    subtitle_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{subtitle_filename}")
    subtitle_file.save(subtitle_path)

    try:
        output_filename = f"subtitled_{uuid.uuid4()}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        subtitle_path_escaped = subtitle_path.replace('\\', '/').replace(':', '\\:')

        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"subtitles='{subtitle_path_escaped}':force_style='FontSize={fontsize},PrimaryColour=&H{get_hex_color(color)}'",
            '-c:a', 'copy',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return jsonify({'error': f'FFmpeg failed: {result.stderr}'}), 500

        os.remove(video_path)
        os.remove(subtitle_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except subprocess.TimeoutExpired:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(subtitle_path):
            os.remove(subtitle_path)
        return jsonify({'error': 'Processing timeout'}), 500
    except Exception as e:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(subtitle_path):
            os.remove(subtitle_path)
        return jsonify({'error': str(e)}), 500

def get_hex_color(color_name):
    """Convert color name to hex"""
    colors = {
        'white': 'FFFFFF',
        'black': '000000',
        'red': '0000FF',
        'green': '00FF00',
        'blue': 'FF0000',
        'yellow': '00FFFF'
    }
    return colors.get(color_name.lower(), 'FFFFFF')
