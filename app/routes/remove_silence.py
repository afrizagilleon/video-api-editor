# ============================================================================
# REMOVE SILENCE
# ============================================================================

from flask import request, jsonify, send_file, current_app as app
from werkzeug.utils import secure_filename
import os
import uuid
import subprocess

from utils import allowed_file, check_auto_editor

from . import api_bp


@api_bp.route('/remove-silence', methods=['POST'])
def remove_silence():
    """Remove silent parts using auto-editor"""
    if not check_auto_editor():
        return jsonify({'error': 'auto-editor not installed'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    threshold = request.form.get('threshold', '-40dB')
    margin = request.form.get('margin', '0.2sec')

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    file.save(upload_path)

    try:
        output_filename = f"silence_removed_{uuid.uuid4()}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        cmd = [
            'auto-editor',
            upload_path,
            '--margin', margin,
            '--edit', f'audio:threshold={threshold}',
            '-o', output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return jsonify({'error': f'auto-editor failed: {result.stderr}'}), 500

        os.remove(upload_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except subprocess.TimeoutExpired:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': 'Processing timeout'}), 500
    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({'error': str(e)}), 500
