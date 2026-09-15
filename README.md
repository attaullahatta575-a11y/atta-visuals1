# Amazon Listing AI

A modular Streamlit application that takes one product image and creates a 7-image Amazon listing visual set.

## What it does

1. Upload one product image.
2. Groq vision analyzes only visible/product-provided information.
3. Groq creates a 7-image Amazon art direction.
4. Python/Pillow renders high-resolution listing graphics.
5. You can edit headline/copy in English or Urdu.
6. Export at 2000x2000, 1100x1100, 1500x1500, 1080x1080, or a custom-size-ready architecture.
7. Download individual images or all 7 as a ZIP.

## Important architecture note

Groq is used for multimodal product understanding and copy/art direction. The final graphics are rendered locally in Python so text remains editable and does not depend on text being perfectly rendered inside an AI-generated image.

This version does not use a separate image-generation API. It creates professional e-commerce compositions from the uploaded product image. A future image-generation provider can be added behind `image_service.py` without changing the rest of the application.

## Setup

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and add your Groq API key.

```text
GROQ_API_KEY=your_key_here
```

Then run:

```powershell
streamlit run main.py
```

## Project structure

```text
main.py
config.py
models.py
vision_service.py
strategy_service.py
image_service.py
editor.py
export_service.py
database.py
requirements.txt
.env.example
.gitignore
README.md
```

## Design principles

- Single Responsibility Principle
- Separation of Concerns
- Loose coupling
- High cohesion
- No JSON reports shown to users
- Product source image is treated as the source of truth
- No invented specifications
- Main image remains clean and text-free
