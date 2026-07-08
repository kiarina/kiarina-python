from io import BytesIO

try:
    from PIL import Image
except ImportError as exc:
    raise ImportError(
        "pillow is required to use OpenAIVideoGenerationProvider. "
        "Install it with: "
        "pip install 'kiarina-agi-video[video-generation-provider-openai]'"
    ) from exc


def resize_image_to_target_size(image_data: bytes, target_size: str) -> bytes:
    """
    Resize an image to the specified size (preserving aspect ratio with center cropping)

    Args:
        image_data: Binary data of the original image
        target_size: Target size (e.g., "1280x720")

    Returns:
        Resized image data (JPEG format)
    """
    # Parse target size
    target_width, target_height = map(int, target_size.split("x"))

    # Open the image
    img = Image.open(BytesIO(image_data))

    # Original image size
    orig_width, orig_height = img.size

    # Return as-is if already the same size
    if orig_width == target_width and orig_height == target_height:
        return image_data

    # Calculate aspect ratios
    target_aspect = target_width / target_height
    orig_aspect = orig_width / orig_height

    # Calculate size after resizing (to cover the target dimensions)
    if orig_aspect > target_aspect:
        # Original image is wider → match height, crop width
        new_height = target_height
        new_width = int(target_height * orig_aspect)
    else:
        # Original image is taller → match width, crop height
        new_width = target_width
        new_height = int(target_width / orig_aspect)

    # Resize
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)  # type: ignore

    # Center crop
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    img = img.crop((left, top, right, bottom))  # type: ignore

    # Convert to RGB mode (for JPEG saving)
    if img.mode != "RGB":
        img = img.convert("RGB")  # type: ignore

    # Convert to binary data
    output = BytesIO()
    img.save(output, format="JPEG", quality=95)
    output.seek(0)

    return output.read()
