from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from typing import Dict, Tuple

from config import SUPPORTED_SIZES
from models import ListingPlan, ImagePlan


def _font(size: int, bold=False, urdu=False):
    candidates = []
    if urdu:
        candidates = [
            "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit_product(product: Image.Image, box: Tuple[int, int], pad=30):
    image = product.copy().convert("RGBA")
    image.thumbnail((max(1, box[0] - pad * 2), max(1, box[1] - pad * 2)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", box, (0, 0, 0, 0))
    x = (box[0] - image.width) // 2
    y = (box[1] - image.height) // 2
    canvas.alpha_composite(image, (x, y))
    return canvas


def _shadow_layer(size, product_box, blur=30):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y, w, h = product_box
    draw.ellipse((x + w * .12, y + h * .78, x + w * .88, y + h * .94), fill=(0, 0, 0, 75))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def _draw_text(draw, xy, text, font, fill, anchor="la"):
    if text:
        draw.text(xy, text, font=font, fill=fill, anchor=anchor)


def _base(size, kind):
    w, h = size
    if kind == 1:
        return Image.new("RGB", size, "white")
    img = Image.new("RGB", size, (247, 248, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, int(h * .018)), fill=(24, 31, 42))
    if kind == 6:
        draw.rectangle((0, int(h * .62), w, h), fill=(228, 221, 209))
        draw.ellipse((int(w*.58), int(h*.10), int(w*1.05), int(h*.58)), fill=(238, 232, 220))
    elif kind in (2, 3, 4, 5, 7):
        draw.rounded_rectangle(
            (int(w*.05), int(h*.07), int(w*.95), int(h*.93)),
            radius=int(w*.035),
            outline=(225, 228, 233),
            width=max(2, w // 500),
        )
    return img


def _normalize(text):
    return " ".join(text.replace("\n", " ").split())


def render_image(product: Image.Image, plan: ImagePlan, size_name: str, language="English"):
    size = SUPPORTED_SIZES[size_name]
    if size is None:
        size = (2000, 2000)

    w, h = size
    canvas = _base(size, plan.number)
    draw = ImageDraw.Draw(canvas)

    product_area = (int(w*.42), int(h*.56))
    fitted = _fit_product(product, product_area)
    px = int(w*.50 - fitted.width/2)
    py = int(h*.37 - fitted.height/2)

    # Product remains untouched; only presentation/background is changed.
    shadow = _shadow_layer(size, (px, py, fitted.width, fitted.height), blur=max(12, w//100))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow)
    canvas.alpha_composite(fitted, (px, py))
    draw = ImageDraw.Draw(canvas)

    title_font = _font(max(38, w//18), bold=True, urdu=language=="Urdu")
    body_font = _font(max(24, w//38), bold=False, urdu=language=="Urdu")
    small_font = _font(max(20, w//48), bold=False, urdu=language=="Urdu")

    if plan.number == 1:
        # Pure main image: no text.
        return canvas.convert("RGB")

    headline = _normalize(plan.headline) or plan.name
    copy = _normalize(plan.supporting_copy)

    _draw_text(draw, (int(w*.08), int(h*.12)), headline[:70], title_font, (25, 31, 40))
    if copy:
        _draw_text(draw, (int(w*.08), int(h*.20)), copy[:130], body_font, (75, 82, 92))

    if plan.number in (2, 3):
       items = plan.features if plan.number == 2 else plan.benefits
        items = items[:5]
        y = int(h*.30)
        for i, item in enumerate(items):
            cy = y + i * int(h*.105)
            draw.ellipse((int(w*.08), cy, int(w*.08)+34, cy+34), fill=(25, 31, 40))
            _draw_text(draw, (int(w*.08)+17, cy+17), str(i+1), _font(20, True), "white", "mm")
            _draw_text(draw, (int(w*.12), cy+17), _normalize(item)[:80], body_font, (38, 44, 52), "lm")

    elif plan.number == 4:
        steps = plan.steps[:4] or ["Prepare the product", "Use as intended", "Follow the product instructions", "Enjoy the result"]
        y = int(h*.30)
        for i, step in enumerate(steps):
            cy = y + i * int(h*.105)
            draw.ellipse((int(w*.08), cy, int(w*.08)+50, cy+50), fill=(25, 31, 40))
            _draw_text(draw, (int(w*.08)+25, cy+25), str(i+1), _font(24, True), "white", "mm")
            _draw_text(draw, (int(w*.12), cy+25), _normalize(step)[:75], body_font, (38, 44, 52), "lm")

    elif plan.number == 5:
        specs = plan.specs or plan.product.verified_specs
        if not specs:
            specs = ["Specifications not provided"]
        y = int(h*.31)
        for spec in specs[:6]:
            draw.rounded_rectangle(
                (int(w*.08), y, int(w*.92), y+int(h*.075)),
                radius=18, fill="white", outline=(220, 223, 228), width=2
            )
            _draw_text(draw, (int(w*.11), y+int(h*.0375)), _normalize(spec)[:100], body_font, (45, 51, 60), "lm")
            y += int(h*.09)

    elif plan.number == 6:
        badge = "REAL-WORLD USE"
        draw.rounded_rectangle((int(w*.08), int(h*.73), int(w*.38), int(h*.79)), radius=16, fill=(25,31,40))
        _draw_text(draw, (int(w*.23), int(h*.76)), badge, small_font, "white", "mm")

    elif plan.number == 7:
        points = (plan.product.selling_points or plan.product.benefits)[:3]
        y = int(h*.30)
        for point in points:
            draw.rounded_rectangle((int(w*.08), y, int(w*.92), y+int(h*.09)), radius=22, fill="white")
            _draw_text(draw, (int(w*.11), y+int(h*.045)), "✓  " + _normalize(point)[:85], body_font, (35, 41, 50), "lm")
            y += int(h*.11)

    # Soft finishing pass for a polished export.
    canvas = ImageEnhance.Sharpness(canvas.convert("RGB")).enhance(1.12)
    return canvas


def generate_listing_images(product: Image.Image, plan: ListingPlan, size_name: str) -> Dict[int, Image.Image]:
    return {
        item.number: render_image(product, item, size_name, language="English")
        for item in plan.images
    }
