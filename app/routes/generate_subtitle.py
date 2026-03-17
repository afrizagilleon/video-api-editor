# ============================================================================
# GENERATE SUBTITLES
# ============================================================================

from flask import request, jsonify, send_file, current_app as app
from werkzeug.utils import secure_filename
import os
import uuid
import json

from utils import allowed_file, require_library

from faster_whisper import WhisperModel

from . import api_bp


# Global whisper model (lazy loaded)
whisper_model = None


@api_bp.route('/generate-subtitles', methods=['POST'])
@require_library('whisper')
def generate_subtitles():
    """Generate subtitles using faster-whisper"""
    global whisper_model

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    language = request.form.get('language', None)
    model_size = request.form.get('model', 'base')
    output_format = request.form.get('format', 'srt')

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    file.save(upload_path)

    try:
        if whisper_model is None:
            whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")

        segments, info = whisper_model.transcribe(
            upload_path, 
            language=language,
            word_timestamps=False
        )

        segments_list = list(segments)

        output_filename = f"subtitles_{uuid.uuid4()}.{output_format}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        if output_format == 'srt':
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments_list, 1):
                    f.write(f"{i}\n")
                    f.write(f"{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n")
                    f.write(f"{segment.text.strip()}\n\n")

        elif output_format == 'vtt':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                for segment in segments_list:
                    f.write(f"{format_timestamp(segment.start, vtt=True)} --> {format_timestamp(segment.end, vtt=True)}\n")
                    f.write(f"{segment.text.strip()}\n\n")

        elif output_format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                result = {
                    'language': info.language,
                    'duration': info.duration,
                    'segments': [
                        {
                            'start': seg.start,
                            'end': seg.end,
                            'text': seg.text.strip()
                        }
                        for seg in segments_list
                    ]
                }
                json.dump(result, f, ensure_ascii=False, indent=2)

        os.remove(upload_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': str(e)}), 500

def format_timestamp(seconds, vtt=False):
    """Convert seconds to SRT/VTT timestamp"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    if vtt:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
