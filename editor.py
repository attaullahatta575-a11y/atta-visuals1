import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from image_service import render_image
from models import ImagePlan
from config import SUPPORTED_SIZES


def _rerender_with_text(product, plan, size_name, language, headline, copy):
    edited = ImagePlan(
        number=plan.number,
        name=plan.name,
        purpose=plan.purpose,
        headline=headline,
        supporting_copy=copy,
        features=plan.features,
        steps=plan.steps,
        specs=plan.specs,
        layout=plan.layout,
        background=plan.background,
        palette=plan.palette,
    )
    return render_image(product, edited, size_name, language=language)


def render_editor(images, plan, size_name):
    tabs = st.tabs([f"Image {i}" for i in range(1, 8)])
    output = dict(images)

    for index, tab in enumerate(tabs, start=1):
        with tab:
            item = plan.images[index - 1]
            st.caption(f"{item.name} — {item.purpose}")

            col1, col2 = st.columns([1.2, 1])
            with col1:
                st.image(output[index], use_container_width=True)

            with col2:
                language = st.selectbox(
                    "Language",
                    ["English", "Urdu"],
                    key=f"lang_{index}",
                )
                headline = st.text_input(
                    "Headline",
                    value=item.headline if index != 1 else "",
                    key=f"headline_{index}",
                    disabled=index == 1,
                )
                copy = st.text_area(
                    "Supporting copy",
                    value=item.supporting_copy,
                    key=f"copy_{index}",
                    disabled=index == 1,
                )

                if st.button("Apply edits", key=f"apply_{index}", type="primary"):
                    if index == 1:
                        st.warning("The main Amazon image intentionally stays clean and text-free.")
                    else:
                        output[index] = _rerender_with_text(
                            st.session_state["original"],
                            item,
                            size_name,
                            language,
                            headline,
                            copy,
                        )
                        st.success("Updated.")

                st.write("Design notes:")
                st.write(item.layout or "Premium minimal layout")
                if item.palette:
                    st.write("Palette:", ", ".join(item.palette[:5]))

    return output
