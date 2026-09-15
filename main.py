import io
import streamlit as st
from PIL import Image

from config import APP_NAME, DEFAULT_SIZE, SUPPORTED_SIZES
from vision_service import analyze_product
from strategy_service import create_listing_plan
from image_service import generate_listing_images
from editor import render_editor
from export_service import prepare_downloads
from database import save_project


st.set_page_config(page_title=APP_NAME, page_icon="🛒", layout="wide")

st.title("🛒 Amazon Listing AI")
st.caption("Upload one product image → create 7 professional listing visuals → edit English/Urdu text → export high quality.")

with st.sidebar:
    st.header("Settings")
    selected_size = st.selectbox(
        "Output size",
        options=list(SUPPORTED_SIZES.keys()),
        index=list(SUPPORTED_SIZES.keys()).index(DEFAULT_SIZE),
    )
    export_format = st.selectbox("Download format", ["PNG", "JPG"])
    st.info("Groq is used for product understanding and listing copy. The graphics are rendered locally in Python so the final text stays editable.")

uploaded = st.file_uploader(
    "Upload your product image",
    type=["png", "jpg", "jpeg", "webp"],
    help="Use the clearest product photo you have. Do not upload a collage if you want accurate product preservation.",
)

product_details = st.text_area(
    "Optional product details",
    placeholder="Add only facts you know: brand, dimensions, material, capacity, compatibility, etc.",
)

if uploaded:
    image_bytes = uploaded.getvalue()
    product_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Original product")
        st.image(product_image, use_container_width=True)
    with right:
        st.subheader("Generate")
        st.write("The app will create:")
        st.write("1. Main product image")
        st.write("2. Features")
        st.write("3. Benefits")
        st.write("4. How to use")
        st.write("5. Specifications")
        st.write("6. Lifestyle concept")
        st.write("7. Premium closing image")

        if st.button("✨ Generate 7 Listing Images", type="primary", use_container_width=True):
            try:
                with st.status("Creating your listing visuals...", expanded=True) as status:
                    st.write("Analyzing the product with Groq vision...")
                    analysis = analyze_product(image_bytes, product_details)

                    st.write("Creating the 7-image art direction...")
                    plan = create_listing_plan(analysis, product_details)

                    st.write("Rendering high-resolution editable graphics...")
                    images = generate_listing_images(product_image, plan, selected_size)

                    st.session_state["analysis"] = analysis
                    st.session_state["plan"] = plan
                    st.session_state["images"] = images
                    st.session_state["original"] = product_image
                    st.session_state["size_name"] = selected_size
                    st.session_state["export_format"] = export_format

                    save_project(analysis, plan)
                    status.update(label="Done — 7 listing visuals are ready.", state="complete")
            except Exception as exc:
                st.error(f"Generation failed: {exc}")

if "images" in st.session_state:
    st.divider()
    st.header("✏️ Edit your listing images")

    edited_images = render_editor(
        st.session_state["images"],
        st.session_state["plan"],
        st.session_state["size_name"],
    )
    st.session_state["images"] = edited_images

    st.divider()
    st.header("⬇️ Download")
    prepare_downloads(
        st.session_state["images"],
        st.session_state["plan"],
        st.session_state["size_name"],
        st.session_state["export_format"],
    )
