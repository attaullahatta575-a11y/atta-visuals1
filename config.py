import os
from pathlib import Path

APP_NAME = "Amazon Listing AI"

# Groq vision-capable model. Change it in .env if you want to test another supported model.
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")

DEFAULT_SIZE = "2000 × 2000"
SUPPORTED_SIZES = {
    "2000 × 2000": (2000, 2000),
    "1100 × 1100": (1100, 1100),
    "1500 × 1500": (1500, 1500),
    "1080 × 1080": (1080, 1080),
    "Custom": None,
}

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "generated_images"
OUTPUT_DIR.mkdir(exist_ok=True)
DATABASE_PATH = BASE_DIR / "database.db"

MAX_UPLOAD_MB = 20
