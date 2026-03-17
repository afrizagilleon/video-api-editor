# ============================================================================
# CONCATENATE VIDEOS
# ============================================================================

from flask import request, jsonify, send_file, current_app as app
from werkzeug.utils import secure_filename
import os
import uuid

from utils import allowed_file, require_library

from moviepy import VideoFileClip, concatenate_videoclips

from . import api_bp

@api_bp.route('/concat', methods=['POST'])
@require_library('moviepy')
def concatenate_videos():
    """Concatenate multiple videos"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    if len(files) < 2:
        return jsonify({'error': 'Need at least 2 videos'}), 400

    method = request.form.get('method', 'chain')
    upload_paths = []

    try:
        for file in files:
            if not allowed_file(file.filename):
                continue
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
            file.save(upload_path)
            upload_paths.append(upload_path)

        clips = [VideoFileClip(path) for path in upload_paths]
        final_clip = concatenate_videoclips(clips, method=method)

        output_filename = f"concat_{uuid.uuid4()}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

        for clip in clips:
            clip.close()
        final_clip.close()
        for path in upload_paths:
            os.remove(path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        for path in upload_paths:
            if os.path.exists(path):
                os.remove(path)
        return jsonify({'error': str(e)}), 500

