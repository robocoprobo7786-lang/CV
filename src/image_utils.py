"""
Image Utility Functions
Provides helper utilities for loading, validating, converting, resizing,
and saving images using OpenCV and Pillow.
Handles Windows Unicode path encodings and large-resolution images safely.
"""

import os
from typing import Optional, Tuple, Dict, Any
import cv2
import numpy as np
from PIL import Image

# Supported image file extensions
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")


def validate_image_path(file_path: str) -> Tuple[bool, str]:
    """
    Validates that a file path exists, has a supported format, and is non-empty.

    Args:
        file_path: Path to the image file.

    Returns:
        Tuple[bool, str]: (is_valid, error_or_success_message)
    """
    if not file_path or not isinstance(file_path, str):
        return False, "File path cannot be empty."

    if not os.path.exists(file_path):
        return False, f"File does not exist: {file_path}"

    if not os.path.isfile(file_path):
        return False, f"Specified path is not a file: {file_path}"

    # Validate file extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        supported_str = ", ".join(SUPPORTED_EXTENSIONS)
        return False, f"Unsupported file format '{ext}'. Supported formats: {supported_str}"

    # Check non-zero file size
    try:
        size = os.path.getsize(file_path)
        if size == 0:
            return False, "File is empty (0 bytes)."
    except OSError as e:
        return False, f"Unable to read file size: {e}"

    return True, "File is valid."


def load_image(file_path: str) -> Optional[np.ndarray]:
    """
    Safely load an image from disk using OpenCV.
    Uses numpy byte decoding to ensure Windows Unicode paths work reliably.

    Args:
        file_path: Absolute or relative path to the image file.

    Returns:
        np.ndarray: Loaded image in BGR format, or None if loading fails.
    """
    is_valid, _ = validate_image_path(file_path)
    if not is_valid:
        return None

    try:
        # np.fromfile handles Unicode filepaths seamlessly on Windows
        image_bytes = np.fromfile(file_path, dtype=np.uint8)
        img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if img is None or img.size == 0:
            return None

        return img
    except Exception as e:
        print(f"Error loading image from {file_path}: {e}")
        return None


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Converts an input image to 8-bit single-channel grayscale.
    Guarantees that the input image array is NOT modified (creates a new array).

    Args:
        image: Input image (BGR color or already grayscale).

    Returns:
        np.ndarray: A new single-channel 8-bit grayscale image (uint8).
    """
    if image is None:
        raise ValueError("Input image cannot be None.")

    if not isinstance(image, np.ndarray):
        raise TypeError(f"Expected numpy.ndarray, got {type(image)}")

    # If already a 2D grayscale image, return an independent copy
    if len(image.shape) == 2:
        return image.copy()

    # If 3-channel color image (OpenCV default BGR)
    elif len(image.shape) == 3:
        if image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        elif image.shape[2] == 1:
            return image[:, :, 0].copy()

    raise ValueError(f"Unsupported image dimensions for grayscale conversion: shape {image.shape}")


def cv_to_pil(image: np.ndarray) -> Image.Image:
    """
    Converts an OpenCV image (numpy ndarray) to a PIL Image suitable for Tkinter.

    Args:
        image: BGR or single-channel grayscale numpy array.

    Returns:
        PIL.Image.Image: Converted RGB or L format PIL image.
    """
    if image is None:
        raise ValueError("Cannot convert None image to PIL.")

    if not isinstance(image, np.ndarray):
        raise TypeError(f"Expected numpy.ndarray, got {type(image)}")

    if len(image.shape) == 2:
        # Single channel Grayscale -> PIL 'L' mode
        return Image.fromarray(image, mode="L")
    elif len(image.shape) == 3:
        if image.shape[2] == 1:
            return Image.fromarray(image[:, :, 0], mode="L")
        # OpenCV standard is BGR -> convert to RGB for PIL
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb, mode="RGB")
    else:
        raise ValueError(f"Unsupported image shape for PIL conversion: {image.shape}")


def resize_image_aspect_ratio(pil_img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    """
    Resizes a PIL image to fit within max_w and max_h while strictly
    preserving the original aspect ratio without distortion or stretching.
    Handles large-resolution images correctly and efficiently using Lanczos resampling.

    Args:
        pil_img: Source PIL Image.
        max_w: Maximum allowed width in pixels.
        max_h: Maximum allowed height in pixels.

    Returns:
        PIL.Image.Image: Resized PIL image.
    """
    if max_w <= 10 or max_h <= 10:
        return pil_img

    orig_w, orig_h = pil_img.size
    if orig_w <= 0 or orig_h <= 0:
        return pil_img

    # Calculate uniform scaling factor that fits both width and height bounds
    ratio = min(max_w / orig_w, max_h / orig_h)

    # Calculate new integer dimensions (at least 1x1)
    new_w = max(1, int(round(orig_w * ratio)))
    new_h = max(1, int(round(orig_h * ratio)))

    # Fast check: if dimensions already fit and are identical, return copy
    if new_w == orig_w and new_h == orig_h:
        return pil_img.copy()

    # Lanczos filter provides optimal sharpness for downsampling large images
    return pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def get_unique_filepath(target_dir: str, base_name: str, ext: str = ".png") -> str:
    """
    Generates a unique, non-colliding file path within target_dir.
    If 'image.png' exists, appends an incrementing counter: 'image_1.png', 'image_2.png', etc.
    Prevents accidental file overwriting (Part C Requirement).

    Args:
        target_dir: Destination folder path.
        base_name: Desired file name without extension.
        ext: File extension (e.g. '.png').

    Returns:
        str: Absolute or relative file path that does not currently exist.
    """
    os.makedirs(target_dir, exist_ok=True)
    if not ext.startswith("."):
        ext = "." + ext

    # Clean base_name of existing extension if present
    root_name, existing_ext = os.path.splitext(base_name)
    if existing_ext:
        base_name = root_name
        ext = existing_ext

    candidate = os.path.join(target_dir, f"{base_name}{ext}")
    if not os.path.exists(candidate):
        return candidate

    counter = 1
    while True:
        candidate = os.path.join(target_dir, f"{base_name}_{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def save_image(file_path: str, image: np.ndarray, overwrite: bool = True) -> Tuple[bool, str]:
    """
    Safely saves an OpenCV image to disk using numpy encoding to support Unicode paths.
    If overwrite is False and file exists, automatically finds a unique non-colliding filename.

    Args:
        file_path: Target save file path.
        image: Image array to save.
        overwrite: Whether to overwrite existing file if it exists.

    Returns:
        Tuple[bool, str]: (Success, actual_file_path_saved)
    """
    if image is None or not isinstance(image, np.ndarray):
        return False, ""

    try:
        dir_name = os.path.dirname(file_path) or "."
        base_name = os.path.basename(file_path)
        ext = os.path.splitext(base_name)[1].lower() or ".png"
        raw_name = os.path.splitext(base_name)[0]

        if not overwrite and os.path.exists(file_path):
            file_path = get_unique_filepath(dir_name, raw_name, ext)

        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        success, encoded = cv2.imencode(ext, image)
        if success:
            with open(file_path, "wb") as f:
                encoded.tofile(f)
            return True, file_path
        return False, file_path
    except Exception as e:
        print(f"Error saving image to {file_path}: {e}")
        return False, file_path


def get_image_metadata(file_path: str, image: Optional[np.ndarray]) -> Dict[str, Any]:
    """
    Extracts informative metadata for display in the GUI status or info panel.

    Args:
        file_path: Path to the image file.
        image: Numpy image array (or None).

    Returns:
        dict: Metadata dictionary with filename, dimensions, channels, color_mode, dtype, filesize.
    """
    filename = os.path.basename(file_path) if file_path else "None"
    ext = os.path.splitext(filename)[1].upper().replace(".", "") if file_path else "N/A"
    filesize_str = "N/A"

    if file_path and os.path.exists(file_path):
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                filesize_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                filesize_str = f"{size_bytes / 1024:.1f} KB"
            else:
                filesize_str = f"{size_bytes / (1024 * 1024):.2f} MB"
        except OSError:
            filesize_str = "Unknown"

    if image is None:
        return {
            "filename": filename,
            "format": ext,
            "width": 0,
            "height": 0,
            "dimensions": "--",
            "channels": 0,
            "color_mode": "--",
            "dtype": "--",
            "filesize": filesize_str
        }

    h, w = image.shape[:2]
    if len(image.shape) == 2:
        channels = 1
        color_mode = "Grayscale (1-ch)"
    else:
        channels = image.shape[2]
        color_mode = f"Color ({channels}-ch BGR)"

    return {
        "filename": filename,
        "format": ext,
        "width": w,
        "height": h,
        "dimensions": f"{w} × {h}",
        "channels": channels,
        "color_mode": color_mode,
        "dtype": str(image.dtype),
        "filesize": filesize_str
    }
