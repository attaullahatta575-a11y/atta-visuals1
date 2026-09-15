import base64
import os
import re
from groq import Groq

from config import GROQ_MODEL
from models import ProductAnalysis


SYSTEM_PROMPT = """
You are a senior Amazon product listing art director and e-commerce visual marketing specialist.

Analyze only what is visible in the product image and what the user explicitly provides.
Never invent dimensions, weight, materials, certifications, compatibility, performance claims,
medical claims, guarantees, or other specifications.

Return a concise human-readable analysis with these exact section labels:
PRODUCT TYPE:
TARGET CUSTOMER:
PURPOSE:
VISIBLE FEATURES:
CUSTOMER BENEFITS:
POSSIBLE SELLING POINTS:
DESIGN STYLE:
COLOR PALETTE:
TYPOGRAPHY:
VERIFIED SPECIFICATIONS:

For unknown information write "Not provided / not visible".
"""


def _client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")
    return Groq(api_key=api_key)


def _data_url(image_bytes: bytes) -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def _section(text: str, label: str) -> str:
    pattern = rf"{re.escape(label)}\s*(.*?)(?=\n[A-Z][A-Z /_-]+:|\Z)"
    match = re.search(pattern, text, re.I | re.S)
    return match.group(1).strip() if match else ""


def _list(value: str):
    if not value:
        return []
    parts = re.split(r"\n|•|- ", value)
    return [p.strip(" -*•\t") for p in parts if p.strip(" -*•\t")]


def analyze_product(image_bytes: bytes, product_details: str = "") -> ProductAnalysis:
    prompt = SYSTEM_PROMPT + "\nUser-provided facts:\n" + (product_details or "None.")

    response = _client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a precise visual product analyst."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": _data_url(image_bytes)},
                    },
                ],
            },
        ],
        temperature=0.2,
        max_completion_tokens=900,
    )

    text = response.choices[0].message.content or ""

    return ProductAnalysis(
        product_type=_section(text, "PRODUCT TYPE:"),
        target_customer=_section(text, "TARGET CUSTOMER:"),
        purpose=_section(text, "PURPOSE:"),
        visible_features=_list(_section(text, "VISIBLE FEATURES:")),
        benefits=_list(_section(text, "CUSTOMER BENEFITS:")),
        selling_points=_list(_section(text, "POSSIBLE SELLING POINTS:")),
        design_style=_section(text, "DESIGN STYLE:"),
        color_palette=_list(_section(text, "COLOR PALETTE:")),
        typography=_section(text, "TYPOGRAPHY:"),
        verified_specs=_list(_section(text, "VERIFIED SPECIFICATIONS:")),
    )
