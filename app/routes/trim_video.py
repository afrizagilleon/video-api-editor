# ============================================================================
# TRIM VIDEO
# ============================================================================

from flask import request, jsonify, send_file, current_app as app
from werkzeug.utils import secure_filename
import os
import uuid

from utils import allowed_file, require_library

from moviepy import VideoFileClip

from . import api_bp

@api_bp.route('/trim', methods=['POST'])
@require_library('moviepy')
def trim_video():
    """Trim video by start and end time"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    start = float(request.form.get('start', 0))
    end = request.form.get('end', None)
    if end:
        end = float(end)

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    file.save(upload_path)

    try:
        video = VideoFileClip(upload_path)
        trimmed = video.subclipped(start, end)  # MoviePy 2.x uses subclipped()

        output_filename = f"trimmed_{uuid.uuid4()}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        trimmed.write_videofile(output_path, codec='libx264', audio_codec='aac')

        video.close()
        trimmed.close()
        os.remove(upload_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': str(e)}), 500
