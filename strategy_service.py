import os
from groq import Groq
from config import GROQ_MODEL
from models import ProductAnalysis, ImagePlan, ListingPlan


DESIGN_RULES = """
Create a premium international Amazon visual strategy.

There must be exactly 7 images:
1 Main Product Image
2 Main Features
3 Key Benefits
4 How It Works / How to Use
5 Dimensions / Specifications
6 Lifestyle / Real-World Use
7 Brand / Premium Closing

Rules:
- Keep the product as the main visual focus.
- Do not invent specifications or claims.
- Image 1 must be clean white with no text.
- Keep copy short and easy to understand.
- Do not alter product shape, color, logo, branding, or important details.
- Use modern spacing, strong hierarchy, restrained graphics, and premium e-commerce aesthetics.
"""


def _client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is missing.")
    return Groq(api_key=key)


def _split_lines(text: str):
    return [x.strip(" -*•\t") for x in text.splitlines() if x.strip(" -*•\t")]


def _generate_text(analysis: ProductAnalysis, details: str) -> str:
    prompt = f"""
{DESIGN_RULES}

Product type: {analysis.product_type}
Purpose: {analysis.purpose}
Target customer: {analysis.target_customer}
Visible features: {", ".join(analysis.visible_features)}
Benefits: {", ".join(analysis.benefits)}
Selling points: {", ".join(analysis.selling_points)}
Verified specifications: {", ".join(analysis.verified_specs)}
User facts: {details or "None"}

Write the seven image plans using this exact compact format:

IMAGE 1
NAME:
PURPOSE:
HEADLINE:
COPY:
FEATURES:
STEPS:
SPECS:
LAYOUT:
BACKGROUND:
PALETTE:

Repeat for IMAGE 2 through IMAGE 7.

For IMAGE 5, if no verified specifications exist, use "Specifications not provided" and do not guess.
For IMAGE 6, describe a lifestyle composition but do not claim facts that are not known.
"""
    response = _client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a senior Amazon listing art director."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_completion_tokens=4000,
    )
    return response.choices[0].message.content or ""


def _block(text: str, number: int) -> str:
    marker = f"IMAGE {number}"
    start = text.find(marker)
    if start < 0:
        return ""
    next_start = text.find(f"IMAGE {number + 1}", start + len(marker)) if number < 7 else len(text)
    return text[start:next_start]


def _field(block: str, label: str) -> str:
    start = block.find(label)
    if start < 0:
        return ""
    start += len(label)
    end = len(block)
    for candidate in ["\nNAME:", "\nPURPOSE:", "\nHEADLINE:", "\nCOPY:", "\nFEATURES:",
                      "\nSTEPS:", "\nSPECS:", "\nLAYOUT:", "\nBACKGROUND:", "\nPALETTE:"]:
        pos = block.find(candidate, start)
        if pos >= 0:
            end = min(end, pos)
    return block[start:end].strip()


def create_listing_plan(analysis: ProductAnalysis, details: str = "") -> ListingPlan:
    raw = _generate_text(analysis, details)
    images = []

    names = [
        "Main Product Image", "Main Features", "Key Benefits",
        "How to Use", "Specifications", "Lifestyle", "Premium Closing"
    ]

    for number, fallback_name in enumerate(names, 1):
        block = _block(raw, number)
        images.append(
            ImagePlan(
                number=number,
                name=_field(block, "\nNAME:") or fallback_name,
                purpose=_field(block, "\nPURPOSE:"),
                headline=_field(block, "\nHEADLINE:"),
                supporting_copy=_field(block, "\nCOPY:"),
                features=_split_lines(_field(block, "\nFEATURES:")),
                steps=_split_lines(_field(block, "\nSTEPS:")),
                specs=_split_lines(_field(block, "\nSPECS:")),
                layout=_field(block, "\nLAYOUT:"),
                background=_field(block, "\nBACKGROUND:"),
                palette=_split_lines(_field(block, "\nPALETTE:")),
            )
        )

    return ListingPlan(product=analysis, images=images)
