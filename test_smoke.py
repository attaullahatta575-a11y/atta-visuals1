from PIL import Image
from models import ProductAnalysis, ImagePlan, ListingPlan
from image_service import render_image

def test_render():
    product = Image.new("RGB", (600, 600), "white")
    plan = ImagePlan(
        number=2,
        name="Main Features",
        purpose="Test",
        headline="Premium Features",
        supporting_copy="Simple supporting copy.",
        features=["Feature one", "Feature two"],
    )
    listing = ListingPlan(product=ProductAnalysis(), images=[plan])
    out = render_image(product, plan, "1100 × 1100")
    assert out.size == (1100, 1100)
