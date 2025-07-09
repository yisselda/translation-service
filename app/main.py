from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Translation Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "translation"}

@app.get("/api/v1/languages")
async def get_languages():
    return {
        "supported_languages": [
            {"code": "ht", "name": "Haitian Creole"},
            {"code": "en", "name": "English"},
            {"code": "fr", "name": "French"},
            {"code": "es", "name": "Spanish"}
        ]
    }
