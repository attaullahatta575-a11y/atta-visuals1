import os

from groq import Groq

from models import ProductAnalysis, ImagePlan, ListingPlan


DESIGN_RULES = """
Create ONE premium international Amazon listing visual.

There must be exactly ONE image:
1 Main Product Image

Rules:
- Product must remain the main visual focus.
- Use the user's product description as the source for product-related facts.
- Do not invent specifications, claims, features, dimensions, materials, or certifications.
- Keep the product's original shape, color, logo, branding, and important details unchanged.
- Use a clean, modern, premium Amazon e-commerce composition.
- Do not add unnecessary information.
- Keep the design simple and professional.
"""


def _client():
    key = os.getenv("GROQ_API_KEY")

    if not key:
        raise RuntimeError("GROQ_API_KEY is missing.")

    return Groq(api_key=key)


def _split_lines(text: str):
    return [
        x.strip(" -*•\t")
        for x in text.splitlines()
        if x.strip(" -*•\t")
    ]


def _generate_text(
    analysis: ProductAnalysis,
    details: str,
) -> str:

    prompt = f"""
{DESIGN_RULES}

Product type:
{analysis.product_type}

Purpose:
{analysis.purpose}

Target customer:
{analysis.target_customer}

Visible features:
{", ".join(analysis.visible_features)}

Benefits:
{", ".join(analysis.benefits)}

Selling points:
{", ".join(analysis.selling_points)}

Verified specifications:
{", ".join(analysis.verified_specs)}

User product description:
{details or "None"}

Write ONLY ONE image plan using this exact compact format:

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

Do not create IMAGE 2, IMAGE 3, or any other image.

Keep the design directly related to the user's product description.
Do not add unnecessary details.
Do not invent product information.
"""

    response = _client().chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior Amazon listing art director. "
                    "Create only one simple product listing visual plan."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.3,
        max_completion_tokens=2000,
    )

    return response.choices[0].message.content or ""


def _block(text: str, number: int) -> str:

    marker = f"IMAGE {number}"

    start = text.find(marker)

    if start < 0:
        return ""

    return text[start:]


def _field(block: str, label: str) -> str:

    start = block.find(label)

    if start < 0:
        return ""

    start += len(label)

    end = len(block)

    labels = [
        "\nNAME:",
        "\nPURPOSE:",
        "\nHEADLINE:",
        "\nCOPY:",
        "\nFEATURES:",
        "\nSTEPS:",
        "\nSPECS:",
        "\nLAYOUT:",
        "\nBACKGROUND:",
        "\nPALETTE:",
    ]

    for candidate in labels:

        if candidate == label:
            continue

        pos = block.find(candidate, start)

        if pos >= 0:
            end = min(end, pos)

    return block[start:end].strip()


def create_listing_plan(
    analysis: ProductAnalysis,
    details: str = "",
) -> ListingPlan:

    raw = _generate_text(
        analysis,
        details,
    )

    images = []

    fallback_name = "Main Product Image"

    block = _block(
        raw,
        1,
    )

    images.append(
        ImagePlan(
            number=1,
            name=_field(
                block,
                "\nNAME:",
            ) or fallback_name,

            purpose=_field(
                block,
                "\nPURPOSE:",
            ),

            headline=_field(
                block,
                "\nHEADLINE:",
            ),

            supporting_copy=_field(
                block,
                "\nCOPY:",
            ),

            features=_split_lines(
                _field(
                    block,
                    "\nFEATURES:",
                )
            ),

            steps=_split_lines(
                _field(
                    block,
                    "\nSTEPS:",
                )
            ),

            specs=_split_lines(
                _field(
                    block,
                    "\nSPECS:",
                )
            ),

            layout=_field(
                block,
                "\nLAYOUT:",
            ),

            background=_field(
                block,
                "\nBACKGROUND:",
            ),

            palette=_split_lines(
                _field(
                    block,
                    "\nPALETTE:",
                )
            ),
        )
    )

    return ListingPlan(
        product=analysis,
        images=images,
    )
