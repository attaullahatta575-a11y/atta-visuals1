from PIL import Image, ImageEnhance
from typing import Dict, Union

from config import SUPPORTED_SIZES
from models import ListingPlan, ImagePlan


# =========================================================
# PRODUCT IMAGE FIT
# =========================================================

def _fit_product(
    product: Image.Image,
    box_width: int,
    box_height: int,
    padding: int = 80,
) -> Image.Image:
    """
    Resize the original product image while keeping
    its original proportions.
    """

    image = product.copy().convert("RGBA")

    max_width = max(1, box_width - padding * 2)
    max_height = max(1, box_height - padding * 2)

    image.thumbnail(
        (max_width, max_height),
        Image.Resampling.LANCZOS,
    )

    return image


# =========================================================
# CREATE AMAZON MAIN IMAGE
# =========================================================

def render_image(
    product: Image.Image,
    plan: ImagePlan = None,
    size_name: str = None,
    language: str = "English",
) -> Image.Image:
    """
    Create ONE clean Amazon-style product listing image.

    Important:
    - Original product image is preserved.
    - No invented product details.
    - No extra specifications.
    - No unnecessary text.
    - White background.
    - Product remains the main focus.
    """

    # -----------------------------------------------------
    # Get output size
    # -----------------------------------------------------

    if size_name in SUPPORTED_SIZES:
        size = SUPPORTED_SIZES[size_name]
    else:
        size = (2000, 2000)

    if size is None:
        size = (2000, 2000)

    width, height = size

    # -----------------------------------------------------
    # White Amazon-style background
    # -----------------------------------------------------

    canvas = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    # -----------------------------------------------------
    # Prepare product
    # -----------------------------------------------------

    product_rgba = _fit_product(
        product,
        int(width * 0.82),
        int(height * 0.82),
        padding=40,
    )

    # -----------------------------------------------------
    # Center product
    # -----------------------------------------------------

    x = (width - product_rgba.width) // 2
    y = (height - product_rgba.height) // 2

    canvas_rgba = canvas.convert("RGBA")

    canvas_rgba.alpha_composite(
        product_rgba,
        (x, y),
    )

    # -----------------------------------------------------
    # High-quality finishing
    # -----------------------------------------------------

    result = canvas_rgba.convert("RGB")

    result = ImageEnhance.Sharpness(
        result
    ).enhance(1.12)

    return result


# =========================================================
# GENERATE ONE LISTING IMAGE
# =========================================================

def generate_listing_images(
    product: Image.Image,
    plan: Union[ListingPlan, ImagePlan, list],
    size_name: str,
) -> Dict[int, Image.Image]:
    """
    Generate ONLY ONE Amazon listing image.

    The function safely accepts:
    - ListingPlan
    - ImagePlan
    - list of ImagePlan objects

    Only the first image plan is used.
    """

    # -----------------------------------------------------
    # Get first ImagePlan
    # -----------------------------------------------------

    first_plan = None

    if isinstance(plan, list):

        if plan:
            first_plan = plan[0]

    elif isinstance(plan, ImagePlan):

        first_plan = plan

    elif hasattr(plan, "images"):

        if plan.images:
            first_plan = plan.images[0]

    # -----------------------------------------------------
    # If no plan exists, still create the image
    # -----------------------------------------------------

    image = render_image(
        product=product,
        plan=first_plan,
        size_name=size_name,
        language="English",
    )

    # -----------------------------------------------------
    # Return exactly ONE image
    # -----------------------------------------------------

    return {
        1: image
    }
