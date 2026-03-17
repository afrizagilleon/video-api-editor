# ============================================================================
# ADD FADE TRANSITIONS
# ============================================================================

from flask import request, jsonify, send_file, current_app as app
from werkzeug.utils import secure_filename
import os
import uuid

from utils import allowed_file, require_library

from moviepy import VideoFileClip, vfx

from . import api_bp


@api_bp.route('/api/add-fade', methods=['POST'])
@require_library('moviepy')
def add_fade():
    """Add fade-in and/or fade-out"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    fade_in = float(request.form.get('fade_in', 0))
    fade_out = float(request.form.get('fade_out', 0))

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    file.save(upload_path)

    try:
        video = VideoFileClip(upload_path)

        # MoviePy 2.x uses with_effects() method
        if fade_in > 0:
            video = video.with_effects([vfx.FadeIn(fade_in)])
        if fade_out > 0:
            video = video.with_effects([vfx.FadeOut(fade_out)])

        output_filename = f"fade_{uuid.uuid4()}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        video.write_videofile(output_path, codec='libx264', audio_codec='aac')

        video.close()
        os.remove(upload_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': str(e)}), 500
