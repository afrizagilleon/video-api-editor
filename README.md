# 🎬 Video API Editor

REST API for programmatic video editing using Python. Built with Flask, MoviePy 2.x, and faster-whisper to automate common editing tasks like trimming, concatenation, subtitle generation, effects, and transitions.​

**Contributions are highly welcome and encouraged**; feel free to fork the repository and open a pull request

In this README file:
- Features
- Quick start
- API endpoints
- Project structures
- Configuration & Troubleshoot
- Contributing
- Ideas for future
- Contact


---

## ✨ Features

- **Video trimming** – cut video based on timestamps.
    
- **Concatenation** – merge multiple video files into one.
    
- **Auto subtitle generation** – generate subtitles using faster-whisper (Whisper ASR).[[community.hetzner](https://community.hetzner.com/tutorials/building-a-flask-api-to-transcribe-audio-files-using-whisper-ai/)]​
    
- **Text overlay** – add text overlays with configurable position and style.
    
- **Effects** – apply effects such as fade in/out, mirror, color adjustments, and speed changes.​
    
- **Transitions** – crossfade transitions between clips.
    
- **Silence removal** – automatically remove silent parts using auto-editor.
    
- **Health check** – monitor status of MoviePy, FFmpeg, Whisper, and auto-editor.
    

---

## 📋 Prerequisites

This project is designed to run via **Docker** and **Docker Compose**.

- **Docker**  
    Install: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/​)
    
- **Docker Compose** (v2 or higher, usually bundled with Docker Desktop)  
    Install: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)​
    

Make sure both commands work:


```bash
docker --version docker compose version
```

---

## 🚀 Quick Start (Docker Only)

### 1. Clone the repository

```bash
git clone https://github.com/afrizagilleon/video-api-editor.git 

cd video-api-editor
```

### 2. Build and start the containers


```bash
docker compose up -d --build
```

This will:

- Build the application image.
    
- Start the Flask API server.
    
- Expose the API on `http://localhost:5000`.

### 3. Verify the API is running


```bash
curl http://localhost:5000/api/health
```

Expected JSON response (example):

```json
{   
	"status": "healthy",  
	"dependencies": {    
		"moviepy": true,    
		"ffmpeg": true,    
		"whisper": true,    
		"auto_editor": false  
		} 
	}
```

---

## 📚 API Endpoints

Base URL:

```
http://localhost:5000/api
```

### 1. Health Check

**GET** `/health`  
Check overall service and dependency status.

```bash
curl http://localhost:5000/api/health
```

---

### 2. Trim Video

**POST** `/trim`  
Trim a video between `start` and `end` seconds.

**Request (multipart/form-data):**

- `file` – video file (mp4, avi, mov, mkv, webm)
    
- `start` – start time in seconds (float)
    
- `end` – end time in seconds (float)
    

```bash
curl -X POST http://localhost:5000/api/trim \
  -F "file=@input.mp4" \
  -F "start=10.5" \
  -F "end=30.0"
```
---

### 3. Concatenate Videos

**POST** `/concatenate`  
Merge multiple videos into a single output.

**Request (multipart/form-data):**
- `files` – multiple video files
    

bash
```bash
curl -X POST http://localhost:5000/api/concatenate \
  -F "files=@video1.mp4" \
  -F "files=@video2.mp4" \
  -F "files=@video3.mp4"
```

---

### 4. Generate Subtitle

**POST** `/generate-subtitle`  
Generate subtitles (SRT) from the video audio using Whisper ASR.[[community.hetzner](https://community.hetzner.com/tutorials/building-a-flask-api-to-transcribe-audio-files-using-whisper-ai/)]​

**Request (multipart/form-data):**

- `file` – video file
    
- `language` – optional, language code (default: `id` for Indonesian)

- `model_size` – optional, one of: `tiny`, `base`, `small`, `medium`, `large` (default: `base`)
    

```bash
curl -X POST http://localhost:5000/api/generate-subtitle \
  -F "file=@video.mp4" \
  -F "language=id" \
  -F "model_size=base"
```

---

### 5. Add Subtitle to Video

**POST** `/add-subtitle`  
Burn SRT subtitles into a video.

**Request (multipart/form-data):**

- `video` – video file
    
- `subtitle` – SRT subtitle file
    
- `font_size` – optional, default: `24`
    
- `font_color` – optional, default: `white`
    
```bash
curl -X POST http://localhost:5000/api/generate-subtitle \
  -F "file=@video.mp4" \
  -F "language=id" \
  -F "model_size=base"
```

---

### 6. Add Text Overlay

**POST** `/add-text`  
Add a text overlay to the video.

**Request (multipart/form-data):**

- `file` – video file
    
- `text` – text content
    
- `position` – optional, `center`, `top`, or `bottom` (default: `bottom`)
    
- `font_size` – optional, default: `70`
    
- `font_color` – optional, default: `white`
    
- `duration` – optional, duration in seconds (default: full video)
    

```bash
curl -X POST http://localhost:5000/api/add-text \
  -F "file=@video.mp4" \
  -F "text=Subscribe Now!" \
  -F "position=bottom" \
  -F "font_size=80" \
  -F "font_color=yellow"
```

---

### 7. Apply Effect

**POST** `/apply-effect`  
Apply a visual effect to the video.

**Request (multipart/form-data):**

- `file` – video file
    
    
- `duration` – optional, fade duration (default: `1.0`)
    
- `factor` – optional, factor for `colorx` / `speedx` (default: `1.5`)
    

```bash
curl -X POST http://localhost:5000/api/apply-effect \
  -F "file=@video.mp4" \
  -F "effect=fadein" \
  -F "duration=2.0"
```

---

### 8. Add Fade Transition

**POST** `/add-fade-transition`  
Create a crossfade transition between two clips.

**Request (multipart/form-data):**

- `file1` – first video file
    
- `file2` – second video file
    
- `duration` – optional, transition duration in seconds (default: `1.0`)
    

```bash
curl -X POST http://localhost:5000/api/add-fade-transition \
  -F "file1=@video1.mp4" \
  -F "file2=@video2.mp4" \
  -F "duration=1.5"
```

---

### 9. Remove Silence

**POST** `/remove-silence`  
Automatically remove silent parts from a video (requires auto-editor).[[community.openai](https://community.openai.com/t/how-to-use-whisper-to-handle-long-video/530862)]​

**Request (multipart/form-data):**

- `file` – video file
    
- `threshold` – optional, silence threshold in dB (default: `-40`)
    

```bash
curl -X POST http://localhost:5000/api/remove-silence \
  -F "file=@video.mp4" \
  -F "threshold=-35"
```

---

## 🗂️ Project Structure

```text
video-api-editor/
├── app/
│   ├── routes/              # API route handlers
│   │   ├── __init__.py
│   │   ├── health_check.py
│   │   ├── trim_video.py
│   │   ├── concatenate.py
│   │   ├── generate_subtitle.py
│   │   ├── add_subtitle.py
│   │   ├── add_text_overlay.py
│   │   ├── apply_effect.py
│   │   ├── add_fade_transition.py
│   │   └── remove_silence.py
│   ├── utils/               # Utility functions
│   │   └── __init__.py
│   └── video_editing_api.py # Main Flask application
├── uploads/                 # Upload directory (auto-created)
├── outputs/                 # Output directory (auto-created)
├── Oswald/                  # Font files for subtitles
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
---

## 🔧 Configuration

### Environment variables

You can configure these via `docker-compose.yml` or an `.env` file:

- `FLASK_ENV` – `development` or `production` (default: `development`)
- `MAX_CONTENT_LENGTH` – max upload size in bytes (default: `524288000` = 500 MB)

### Docker resource limits

Example snippet from `docker-compose.yml`:

```yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```
Adjust CPU and memory based on your server capacity.

---

### 🔗 n8n Integration

This API is designed to integrate easily with **n8n** workflows for automation.​

### Example workflow (high-level)

1. **HTTP Request Node** – upload video to this API.
    
2. **Generate Subtitle Node** – call `/generate-subtitle`.
    
3. **Add Subtitle Node** – call `/add-subtitle`.
    
4. **Apply Effect Node** – call `/apply-effect` (e.g. fade in).
    
5. **Webhook / Response Node** – return the final video download URL.
    

### Example n8n HTTP Request to `/trim`

```json
{
  "method": "POST",
  "url": "http://video-api:5000/api/trim",
  "sendBody": true,
  "bodyContentType": "multipart-form-data",
  "bodyParameters": {
    "parameters": [
      {
        "name": "file",
        "value": "={{$binary.data}}"
      },
      {
        "name": "start",
        "value": "10"
      },
      {
        "name": "end",
        "value": "30"
      }
    ]
  }
}
```

---

##  🐛 Troubleshooting

### FFmpeg not found

If you see errors about FFmpeg inside the container, ensure the base image and Dockerfile install FFmpeg correctly. Check FFmpeg version inside the running container:

```bash
docker compose exec video-api ffmpeg -version
```

---

### Slow subtitle generation

Whisper models have different trade-offs between speed and accuracy.​

- `tiny` – fastest, lowest accuracy.
    
- `base` – good balance (default).
    
- `small` – better accuracy, slower.
    
- `medium` – high accuracy, slower.
    
- `large` – best accuracy, slowest.

Use a smaller model in production if you need faster throughput.

---

## 🤝 Contributing

Contributions are **very welcome**. This project follows the standard GitHub workflow: **Fork → Clone → Branch → Commit → Pull Request**

### 1. Fork the repository

Click the **Fork** button on the top-right of the GitHub page to create your own copy.

### 2. Clone your fork


```bash
git clone https://github.com/YOUR_USERNAME/video-api-editor.git cd video-api-editor
```

### 3. Create a feature branch


```bash
git checkout -b feature/your-feature-name
```

Examples:

- `feature/audio-mixing`
    
- `feature/video-stabilization`
    

### 4. Develop and test

- Implement your changes.
    
- Run the project with Docker and test the API endpoints.
    
- Ensure there are no breaking changes.

### 5. Commit your changes

Use clear, conventional commit messages:
```bash
git add . git commit -m "Add: audio mixing endpoint"
```

Suggested prefixes:

- `Add:` – new feature
    
- `Fix:` – bug fix
    
- `Update:` – improvements/refactoring
    
- `Docs:` – documentation changes
    

### 6. Push your branch


```bash
git push origin feature/your-feature-name
```

### 7. Open a Pull Request

1. Go to your fork on GitHub.
    
2. Click **Compare & pull request**.
    
3. Describe clearly what you changed and why.
    
4. Submit the pull request.
    

---

## Ideas for future features

Some ideas that would be great contributions:

-  Audio mixing / replacement
    
-  Video stabilization
    
-  Object detection & tracking
    
-  Custom font upload for subtitles
    
-  Batch processing of multiple videos
    
-  Progress tracking for long-running jobs
    
-  Video compression / optimization
    
-  Thumbnail generation
    
-  Audio normalization
    
-  Background music addition
    

---

## 📝 License

This project is licensed under the **MIT License**.  
You are free to use it for personal or commercial projects​

---

## 📧 Contact

If you have questions, feature requests, or find bugs:

- Open an issue: [https://github.com/afrizagilleon/video-api-editor/issues](https://github.com/afrizagilleon/video-api-editor/issues)​
    
- Start a discussion

- My Instagram [@afrizagilleon](httpsL//instagram.com/afrizagilleon)
