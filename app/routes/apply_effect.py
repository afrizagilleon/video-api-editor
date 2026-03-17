# ============================================================================
# APPLY EFFECTS
# ============================================================================

from flask import request, jsonify, send_file, current_app as app
from werkzeug.utils import secure_filename
import os
import uuid

from utils import allowed_file, require_library

from moviepy import VideoFileClip, vfx

from . import api_bp

@api_bp.route('/apply-effect', methods=['POST'])
@require_library('moviepy')
def apply_effect():
    """Apply video effects"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    effect = request.form.get('effect', 'blackwhite')
    value = request.form.get('value', '1.0')

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    file.save(upload_path)

    try:
        video = VideoFileClip(upload_path)

        # MoviePy 2.x effects
        if effect == 'blackwhite':
            video = video.with_effects([vfx.BlackAndWhite()])
        elif effect == 'mirror_x':
            video = video.with_effects([vfx.MirrorX()])
        elif effect == 'mirror_y':
            video = video.with_effects([vfx.MirrorY()])
        elif effect == 'speedx':
            factor = float(value)
            video = video.with_effects([vfx.MultiplySpeed(factor)])
        elif effect == 'resize':
            factor = float(value)
            video = video.with_effects([vfx.Resize(factor)])
        else:
            return jsonify({'error': f'Unknown effect: {effect}'}), 400

        output_filename = f"effect_{uuid.uuid4()}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        video.write_videofile(output_path, codec='libx264', audio_codec='aac')

        video.close()
        os.remove(upload_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': str(e)}), 500
