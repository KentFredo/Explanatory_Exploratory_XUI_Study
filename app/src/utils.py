import base64
import streamlit as st

#####################################################################################
### Functions that are reused in this file                                          ###
#####################################################################################

# Function to load and encode the images as base64


def get_image_as_base64(image_path):
    """
    Load an image from the specified path and encode it as base64.
    Args:
        image_path (str): Path to the image file.
    Returns:
        str: Base64 encoded string of the image.
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error(
            f"Error loading image: {image_path}. Please check the file path.")
        return None
