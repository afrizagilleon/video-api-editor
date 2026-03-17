# ============================================================================
# ADD TEXT OVERLAY
# ============================================================================

import os
import uuid
from werkzeug.utils import secure_filename
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from flask import request, jsonify, send_file, current_app as app
import json

from utils import require_library, allowed_file

from . import api_bp

DEFAULT_FONT = '/usr/share/fonts/truetype/oswald/Oswald-Medium.ttf'

@api_bp.route('/add-text', methods=['POST'])
@require_library('moviepy')
def add_text_overlay():
    """Add text overlay to video"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    text = request.form.get('text', 'Sample Text')
    fontsize = int(request.form.get('fontsize', 50))
    color = request.form.get('color', 'white')
    position = request.form.get('position', 'center')
    start = float(request.form.get('start', 0))
    duration = request.form.get('duration', None)
    if duration:
        duration = float(duration)

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    file.save(upload_path)

    try:
        video = VideoFileClip(upload_path)

        # MoviePy 2.x TextClip syntax
        font_path = request.form.get('font', DEFAULT_FONT)
        
        txt_clip = TextClip(
            text=text,
            font_size=fontsize,
            color=color,
            font=font_path,
            size=video.size
        )

        # MoviePy 2.x uses with_* methods instead of set_*
        if position in ['center', 'top', 'bottom']:
            txt_clip = txt_clip.with_position(position)
        else:
            try:
                pos = json.loads(position)
                txt_clip = txt_clip.with_position(pos)
            except:
                txt_clip = txt_clip.with_position('center')

        txt_clip = txt_clip.with_start(start)
        if duration:
            txt_clip = txt_clip.with_duration(duration)
        else:
            txt_clip = txt_clip.with_duration(video.duration - start)

        final = CompositeVideoClip([video, txt_clip])

        output_filename = f"text_{uuid.uuid4()}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        final.write_videofile(output_path, codec='libx264', audio_codec='aac')

        video.close()
        txt_clip.close()
        final.close()
        os.remove(upload_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': str(e)}), 500
