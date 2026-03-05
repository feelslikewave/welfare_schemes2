"""
Complete Working FastAPI Application - Sahayta AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from pathlib import Path
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services with error handling
try:
    from services.scraper import SchemesScraper
    from services.summarizer import SchemeSummarizer
    from services.translator import MultilingualTranslator
    from services.text_to_speech import TextToSpeechService
    from services.sign_language_service import SignLanguageService
    logger.info("✓ All services imported successfully")
except Exception as e:
    logger.error(f"Error importing services: {e}")
    raise

# Initialize FastAPI app (ONE app only - FastAPI, not Flask)
app = FastAPI(
    title="Sahayta AI - Government Welfare Schemes Portal",
    description="AI-Powered scheme discovery with accessibility features",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    Path("static").mkdir(exist_ok=True)
    Path("static/audio").mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("✓ Static files mounted")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Initialize services
try:
    scraper = SchemesScraper()
    summarizer = SchemeSummarizer(language="en")   # ← Sahayta AI summarizer
    translator = MultilingualTranslator()           # ← Sahayta AI translator
    tts_service = TextToSpeechService()
    sign_service = SignLanguageService()
    logger.info("✓ All services initialized")
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    raise

# Load schemes data on startup
@app.on_event("startup")
async def startup_event():
    try:
        scraper.load_schemes()
        logger.info(f"✓ Loaded {len(scraper.schemes)} schemes")
        logger.info("✓ Sahayta AI ready!")
    except Exception as e:
        logger.error(f"Error loading schemes: {e}")


# ─────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────

class SchemeSearchRequest(BaseModel):
    state: Optional[str] = None
    category: Optional[str] = None
    keyword: Optional[str] = None


class SummaryRequest(BaseModel):
    scheme_id: str
    language: str = "en"


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


class SignLanguageRequest(BaseModel):
    text: str


# ─────────────────────────────────────────────
# Error handler
# ─────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc), "detail": "Internal server error"}
    )


# ─────────────────────────────────────────────
# Page Routes
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        html_path = Path("templates/index.html")
        if not html_path.exists():
            return HTMLResponse("<h1>Error: index.html not found</h1>", status_code=404)
        return FileResponse(html_path)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {e}</h1>", status_code=500)


@app.get("/test-video", response_class=HTMLResponse)
async def test_video():
    try:
        html_path = Path("templates/test_video.html")
        if html_path.exists():
            return FileResponse(html_path)
        return HTMLResponse("<h1>Test page not found</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {e}</h1>", status_code=500)


# ─────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────

@app.get("/api/states")
async def get_states():
    try:
        return JSONResponse({
            "success": True,
            "states": [
                "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
                "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
                "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
                "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
                "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
                "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir"
            ]
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/categories")
async def get_categories():
    try:
        return JSONResponse({
            "success": True,
            "categories": [
                "Agriculture", "Education", "Health", "Housing", "Employment",
                "Social Welfare", "Women and Child", "Financial Inclusion",
                "Rural Development", "Senior Citizens", "Disability Welfare"
            ]
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/languages")
async def get_languages():
    try:
        return JSONResponse({
            "success": True,
            "languages": translator.get_language_options()  # uses MultilingualTranslator
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/schemes/search")
async def search_schemes(request: SchemeSearchRequest):
    try:
        logger.info(f"Search request: {request}")
        schemes = scraper.search_schemes(
            state=request.state,
            category=request.category,
            keyword=request.keyword
        )
        return JSONResponse({"success": True, "count": len(schemes), "schemes": schemes})
    except Exception as e:
        logger.error(f"Error in search_schemes: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/schemes/{scheme_id}")
async def get_scheme(scheme_id: str, language: str = "en"):
    """Get detailed scheme information, translated to chosen language"""
    try:
        logger.info(f"Getting scheme: {scheme_id}, language: {language}")
        scheme = scraper.get_scheme_by_id(scheme_id)
        if not scheme:
            return JSONResponse({"success": False, "error": "Scheme not found"}, status_code=404)

        # Translate scheme fields if language is not English
        if language != "en":
            translator.set_language(language)
            scheme = translator.translate_scheme(scheme, language)

        return JSONResponse({"success": True, "scheme": scheme})
    except Exception as e:
        logger.error(f"Error in get_scheme: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/summarize")
async def summarize_scheme(request: SummaryRequest):
    """
    Summarize a scheme and return it in the user's chosen language.
    Uses SchemeSummarizer from services/summarizer.py
    """
    try:
        logger.info(f"Summarize request: scheme={request.scheme_id}, lang={request.language}")

        scheme = scraper.get_scheme_by_id(request.scheme_id)
        if not scheme:
            return JSONResponse({"success": False, "error": "Scheme not found"}, status_code=404)

        # Set language and summarize+translate using SchemeSummarizer
        summarizer.set_language(request.language)
        result = summarizer.summarize_scheme(scheme)

        return JSONResponse({
            "success": True,
            "summary": result["summary"],          # translated summary
            "name": result.get("name", ""),        # translated name
            "benefits": result.get("benefits", ""),
            "eligibility": result.get("eligibility", ""),
            "language": result.get("language", "English")
        })
    except Exception as e:
        logger.error(f"Error in summarize: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/text-to-speech")
async def text_to_speech(request: TTSRequest):
    try:
        logger.info(f"TTS request: language={request.language}, text length={len(request.text)}")
        audio_file = tts_service.generate_speech(text=request.text, language=request.language)
        return JSONResponse({"success": True, "audio_url": f"/static/audio/{audio_file}"})
    except Exception as e:
        logger.error(f"Error in TTS: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/sign-language")
async def generate_sign_language(request: SignLanguageRequest):
    try:
        logger.info(f"Sign language request: {request.text[:100]}...")
        video_info = sign_service.generate_video(request.text)
        return JSONResponse({
            "success": True,
            "video_url": f"/data/videos/{video_info['filename']}",
            "duration": video_info['duration'],
            "words_count": video_info['words_count'],
            "gestures_used": video_info['gestures_used']
        })
    except Exception as e:
        logger.error(f"Error generating sign language: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
            "detail": traceback.format_exc()
        }, status_code=500)


@app.get("/data/videos/{filename}")
async def serve_video(filename: str):
    try:
        video_path = Path("data/videos") / filename
        if not video_path.exists():
            return JSONResponse({"success": False, "error": "Video not found"}, status_code=404)

        def iterfile():
            with open(video_path, mode="rb") as f:
                yield from f

        return StreamingResponse(
            iterfile(),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Accept-Ranges": "bytes"
            }
        )
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/videos/list")
async def list_videos():
    try:
        video_dir = Path("data/videos")
        if not video_dir.exists():
            return JSONResponse({"success": True, "videos": [], "count": 0})
        videos = [
            {"filename": f.name, "size": f.stat().st_size, "size_kb": round(f.stat().st_size / 1024, 2)}
            for f in video_dir.glob("*.mp4")
        ]
        return JSONResponse({"success": True, "videos": videos, "count": len(videos)})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/health")
async def health_check():
    try:
        return JSONResponse({
            "status": "healthy",
            "app": "Sahayta AI",
            "schemes_loaded": len(scraper.schemes),
            "services": {
                "scraper": "active",
                "summarizer": "active",
                "translator": "active",
                "tts": "active",
                "sign_language": "active"
            }
        })
    except Exception as e:
        return JSONResponse({"status": "unhealthy", "error": str(e)}, status_code=500)


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Sahayta AI - Government Welfare Schemes Portal")
    print("="*60)
    print("\n📍 Access at:    http://localhost:8000")
    print("🧪 Test page:    http://localhost:8000/test-video")
    print("❤️  Health check: http://localhost:8000/health")
    print("\n" + "="*60 + "\n")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)