from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Creole Translation Service",
    description="Translation API for Haitian Creole and other languages",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_language: str
    
class BatchTranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_languages: List[str]

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    
class BatchTranslationResponse(BaseModel):
    translations: Dict[str, TranslationResponse]
    
class Language(BaseModel):
    code: str
    name: str
    native_name: str
    
class LanguagesResponse(BaseModel):
    supported_languages: List[Language]
    
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str

# Mock translation function (replace with actual ML model)
async def translate_text(text: str, source_lang: str, target_lang: str) -> TranslationResponse:
    """Mock translation function - replace with actual model inference"""
    await asyncio.sleep(0.1)  # Simulate processing time
    
    # Mock translations for demo
    mock_translations = {
        ("en", "ht"): {
            "hello": "bonjou",
            "goodbye": "orevwa",
            "thank you": "mèsi",
            "help": "èd",
            "water": "dlo",
            "food": "manje"
        },
        ("ht", "en"): {
            "bonjou": "hello",
            "orevwa": "goodbye",
            "mèsi": "thank you",
            "èd": "help",
            "dlo": "water",
            "manje": "food"
        }
    }
    
    # Simple mock translation logic
    text_lower = text.lower().strip()
    translation_key = (source_lang, target_lang)
    
    if translation_key in mock_translations:
        translated = mock_translations[translation_key].get(text_lower, f"[{target_lang}] {text}")
    else:
        translated = f"[{target_lang}] {text}"
    
    return TranslationResponse(
        translated_text=translated,
        source_language=source_lang,
        target_language=target_lang,
        confidence=0.85
    )

# Supported languages
SUPPORTED_LANGUAGES = [
    Language(code="ht", name="Haitian Creole", native_name="Kreyòl Ayisyen"),
    Language(code="en", name="English", native_name="English"),
    Language(code="fr", name="French", native_name="Français"),
    Language(code="es", name="Spanish", native_name="Español"),
]

# Routes
@app.get("/", response_model=dict)
async def root():
    return {
        "message": "Creole Translation Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="translation",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )

@app.post("/api/v1/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """Translate text from source language to target language"""
    try:
        logger.info(f"Translating: {request.text[:50]}... from {request.source_language} to {request.target_language}")
        
        # Validate languages
        valid_codes = [lang.code for lang in SUPPORTED_LANGUAGES] + ["auto"]
        if request.source_language not in valid_codes:
            raise HTTPException(status_code=400, detail=f"Unsupported source language: {request.source_language}")
        if request.target_language not in valid_codes:
            raise HTTPException(status_code=400, detail=f"Unsupported target language: {request.target_language}")
        
        # Auto-detect source language if needed
        source_lang = request.source_language
        if source_lang == "auto":
            source_lang = "en"  # Simple auto-detection mock
        
        result = await translate_text(request.text, source_lang, request.target_language)
        return result
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.post("/api/v1/translate/batch", response_model=BatchTranslationResponse)
async def translate_batch(request: BatchTranslationRequest):
    """Translate text to multiple target languages"""
    try:
        logger.info(f"Batch translating to {len(request.target_languages)} languages")
        
        # Auto-detect source language if needed
        source_lang = request.source_language
        if source_lang == "auto":
            source_lang = "en"  # Simple auto-detection mock
        
        # Translate to all target languages concurrently
        tasks = [
            translate_text(request.text, source_lang, target_lang)
            for target_lang in request.target_languages
        ]
        
        results = await asyncio.gather(*tasks)
        
        translations = {
            result.target_language: result
            for result in results
        }
        
        return BatchTranslationResponse(translations=translations)
        
    except Exception as e:
        logger.error(f"Batch translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")

@app.get("/api/v1/languages", response_model=LanguagesResponse)
async def get_languages():
    """Get list of supported languages"""
    return LanguagesResponse(supported_languages=SUPPORTED_LANGUAGES)

@app.get("/api/v1/languages/{language_code}", response_model=Language)
async def get_language(language_code: str):
    """Get information about a specific language"""
    for lang in SUPPORTED_LANGUAGES:
        if lang.code == language_code:
            return lang
    raise HTTPException(status_code=404, detail=f"Language {language_code} not supported")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)