# ============================================================================
# ADD TEXT OVERLAY
# ============================================================================

import os
import uuid
import json
from io import BytesIO

from werkzeug.utils import secure_filename
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from flask import request, jsonify, send_file, current_app as app
from PIL import Image, ImageDraw

from utils import require_library, allowed_file
from . import api_bp


DEFAULT_FONT = "/usr/share/fonts/truetype/oswald/Oswald-Medium.ttf"


def color_name_to_rgb(name: str):
    mapping = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "yellow": (255, 255, 0),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "gray": (128, 128, 128),
    }
    return mapping.get(name.lower(), (0, 0, 0))


def create_rounded_bg_image(text_size, radius, bg_color, opacity):
    """
    Return (PIL.Image, pad_x, pad_y)
    """
    w, h = text_size
    pad_x = 20
    pad_y = 10

    bg_w = w + 2 * pad_x
    bg_h = h + 2 * pad_y

    # transparan
    img = Image.new("RGBA", (bg_w, bg_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    r, g, b = bg_color
    fill = (r, g, b, opacity)

    draw.rounded_rectangle(
        [(0, 0), (bg_w, bg_h)],
        radius=radius,
        fill=fill,
    )

    return img, pad_x, pad_y


@api_bp.route("/add-text", methods=["POST"])
@require_library("moviepy")
def add_text_overlay():
    """Add text overlay to video with optional rounded background"""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    # basic params
    text = request.form.get("text", "Sample Text")
    fontsize = int(request.form.get("fontsize", 50))
    color = request.form.get("color", "white")
    position = request.form.get("position", "center")
    start = float(request.form.get("start", 0))
    duration = request.form.get("duration")
    if duration:
        duration = float(duration)

    # background params
    use_bg = request.form.get("bg", "false").lower() in ("true", "1", "yes")
    bg_color_name = request.form.get("bg_color", "black")
    bg_opacity = int(request.form.get("bg_opacity", 180))  # 0–255
    bg_radius = int(request.form.get("bg_radius", 20))

    filename = secure_filename(file.filename)
    upload_path = os.path.join(
        app.config["UPLOAD_FOLDER"], f"{uuid.uuid4()}_{filename}"
    )
    file.save(upload_path)

    try:
        video = VideoFileClip(upload_path)
        video_duration = video.duration

        font_path = request.form.get("font", DEFAULT_FONT)

        # 1) Text clip (size None = mengikuti text, bukan full video)
        vw, vh = video.size
        max_width = int(vw * 0.8)
        txt_clip = TextClip(
            text=text,
            font_size=fontsize,
            color=color,
            font=font_path,
            method="caption",
            size=(max_width, None)
        )
        text_w, text_h = txt_clip.size

        pad_x = pad_y = 0
        bg_clip = None

        # 2) Background bubble (optional)
        if use_bg:
            bg_rgb = color_name_to_rgb(bg_color_name)
            bg_img, pad_x, pad_y = create_rounded_bg_image(
                (text_w, text_h),
                radius=bg_radius,
                bg_color=bg_rgb,
                opacity=bg_opacity,
            )

            buf = BytesIO()
            bg_img.save(buf, format="PNG")
            buf.seek(0)

            bg_clip = ImageClip(buf)

        # 3) Position
        vw, vh = video.size

        box_w = text_w + 2 * pad_x
        box_h = text_h + 2 * pad_y

        if position in ("center", "top", "bottom"):
            x = (vw - box_w) / 2

            if position == "center":
                y = (vh - box_h) / 2
            elif position == "top":
                y = vh * 0.1
            else:  # bottom
                y = vh - box_h - vh * 0.05

            bg_pos = (x, y)
            txt_pos = (x + pad_x, y + pad_y)
        else:
            # custom [x, y]
            try:
                pos = json.loads(position)
                if isinstance(pos, list) and len(pos) == 2:
                    txt_pos = tuple(pos)
                else:
                    txt_pos = ("center", "center")
            except Exception:
                txt_pos = ("center", "center")
            bg_pos = txt_pos  # background align with text

        # 4) Timing
        effective_duration = duration if duration else (video_duration - start)

        txt_clip = txt_clip.with_start(start).with_duration(effective_duration)
        txt_clip = txt_clip.with_position(txt_pos)

        clips = [video]

        if use_bg and bg_clip is not None:
            bg_clip = bg_clip.with_start(start).with_duration(effective_duration)
            bg_clip = bg_clip.with_position(bg_pos)
            clips.append(bg_clip)

        clips.append(txt_clip)

        final = CompositeVideoClip(clips)

        output_filename = f"text_{uuid.uuid4()}.mp4"
        output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)
        final.write_videofile(output_path, codec="libx264", audio_codec="aac")

        # cleanup
        video.close()
        txt_clip.close()
        if bg_clip is not None:
            bg_clip.close()
        final.close()
        os.remove(upload_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        # log detail ke stdout supaya muncul di docker logs
        print("ERROR in /add-text:", repr(e))
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return jsonify({"error": str(e)}), 500
