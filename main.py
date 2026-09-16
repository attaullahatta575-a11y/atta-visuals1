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


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎨",
    layout="wide",
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🎨 Atta Visuals")

st.write(
    "Upload your product image and add a product description. "
    "Atta Visuals will create professional Amazon listing visuals."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    selected_size = st.selectbox(
        "Output Size",
        options=list(SUPPORTED_SIZES.keys()),
        index=(
            list(SUPPORTED_SIZES.keys()).index(DEFAULT_SIZE)
            if DEFAULT_SIZE in SUPPORTED_SIZES
            else 0
        ),
    )

    export_format = st.selectbox(
        "Download Format",
        ["PNG", "JPG"],
    )


# --------------------------------------------------
# PRODUCT IMAGE
# --------------------------------------------------

st.subheader("📷 Product Image")

uploaded_file = st.file_uploader(
    "Upload one product image",
    type=["png", "jpg", "jpeg", "webp","zip",],
)


# --------------------------------------------------
# PRODUCT DESCRIPTION
# --------------------------------------------------

st.subheader("📝 Product Description")

product_description = st.text_area(
    "Describe your product",
    placeholder=(
        "Example:\n"
        "This is a stainless steel water bottle with 1 liter capacity. "
        "It is leak-proof, reusable and suitable for gym, office and travel."
    ),
    height=150,
)


# --------------------------------------------------
# SHOW IMAGE
# --------------------------------------------------

product_image = None
image_bytes = None

if uploaded_file:

    image_bytes = uploaded_file.getvalue()

    try:

        product_image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        st.image(
            product_image,
            caption="Your Product",
            width=400,
        )

    except Exception as exc:

        st.error(
            f"Could not read the image: {exc}"
        )

        st.stop()


# --------------------------------------------------
# GENERATE BUTTON
# --------------------------------------------------

if uploaded_file and product_description.strip():

    st.divider()

    generate_button = st.button(
        "✨ Create Amazon Listing Images",
        type="primary",
        use_container_width=True,
    )

    if generate_button:

        try:

            with st.status(
                "Creating your Amazon listing visuals...",
                expanded=True,
            ) as status:

                # ----------------------------------
                # STEP 1: AI PRODUCT ANALYSIS
                # ----------------------------------

                st.write(
                    "🔍 AI is understanding your product..."
                )

                analysis = analyze_product(
                    image_bytes,
                    product_description,
                )


                # ----------------------------------
                # STEP 2: CREATE LISTING STRATEGY
                # ----------------------------------

                st.write(
                    "🧠 AI is creating the listing content..."
                )

                plan = create_listing_plan(
                    analysis,
                    product_description,
                )


                # ----------------------------------
                # STEP 3: CREATE 4 VISUALS
                # ----------------------------------

                st.write(
                    "🎨 Creating 4 Amazon listing visuals..."
                )

                images = generate_listing_images(
                    product_image,
                    plan,
                    selected_size,
                )


                # ----------------------------------
                # SAVE RESULTS
                # ----------------------------------

                st.session_state["analysis"] = analysis
                st.session_state["plan"] = plan
                st.session_state["images"] = images
                st.session_state["original"] = product_image
                st.session_state["size_name"] = selected_size
                st.session_state["export_format"] = export_format

                save_project(
                    analysis,
                    plan,
                )


                status.update(
                    label="✅ Your 7 listing images are ready!",
                    state="complete",
                )


        except Exception as exc:

            st.error(
                "❌ Something went wrong while creating the visuals."
            )

            st.exception(exc)


elif uploaded_file and not product_description.strip():

    st.info(
        "📝 Please add a product description before generating."
    )


# --------------------------------------------------
# EDITOR
# --------------------------------------------------

if "images" in st.session_state:

    st.divider()

    st.header("✏️ Edit Your Listing Images")

    edited_images = render_editor(
        st.session_state["images"],
        st.session_state["plan"],
        st.session_state["size_name"],
    )

    st.session_state["images"] = edited_images


# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

if "images" in st.session_state:

    st.divider()

    st.header("⬇️ Download")

    prepare_downloads(
        st.session_state["images"],
        st.session_state["plan"],
        st.session_state["size_name"],
        st.session_state["export_format"],
    )
