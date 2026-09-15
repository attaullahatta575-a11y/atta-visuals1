import io
import zipfile
import streamlit as st
from PIL import Image, ImageEnhance

from config import SUPPORTED_SIZES


def _export_image(image: Image.Image, size):
    image = image.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    image = ImageEnhance.Sharpness(image).enhance(1.15)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    return buffer.getvalue()


def prepare_downloads(images, plan, size_name, export_format):
    size = SUPPORTED_SIZES[size_name]
    if size is None:
        size = (2000, 2000)

    cols = st.columns(2)
    for index in range(1, 8):
        data = _export_image(images[index], size)
        filename = f"amazon_listing_{index}_{size[0]}x{size[1]}.png"
        with cols[(index - 1) % 2]:
            st.download_button(
                f"⬇️ Download Image {index}",
                data=data,
                file_name=filename,
                mime="image/png",
                key=f"download_{size_name}_{index}",
                use_container_width=True,
            )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for index in range(1, 8):
            data = _export_image(images[index], size)
            archive.writestr(
                f"amazon_listing_{index}_{size[0]}x{size[1]}.png",
                data,
            )
    zip_buffer.seek(0)

    st.download_button(
        "📦 Download All 7 Images",
        data=zip_buffer.getvalue(),
        file_name=f"amazon_listing_7_images_{size[0]}x{size[1]}.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True,
    )
