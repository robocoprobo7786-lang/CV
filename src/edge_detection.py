"""
Edge Detection Module
Comprehensive implementations of Sobel, Prewitt, and Laplacian operators
for image edge detection using OpenCV and NumPy.

Course: Computer Vision (256PUPC275)
Topic: Edge Detection Using Sobel, Prewitt, and Laplacian Operators
"""

from enum import Enum
from typing import Dict, Any, Optional, Tuple, Union
import os
import numpy as np
import cv2
from matplotlib.figure import Figure

from src.image_utils import convert_to_grayscale


class OperatorType(str, Enum):
    """Enumeration of available edge detection operators."""
    SOBEL = "Sobel"
    PREWITT = "Prewitt"
    LAPLACIAN = "Laplacian"


OPERATOR_DETAILS: Dict[str, Dict[str, str]] = {
    OperatorType.SOBEL.value: {
        "title": "Sobel Operator (1st Derivative)",
        "order": "First-order differential operator",
        "formula": "G = √(Gx² + Gy²)",
        "description": (
            "Directional 3×3 convolution with orthogonal smoothing "
            "to suppress noise and detect clear boundaries."
        ),
        "kernels": "Gx: [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]\nGy: [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]"
    },
    OperatorType.PREWITT.value: {
        "title": "Prewitt Operator (1st Derivative)",
        "order": "First-order differential operator",
        "formula": "G = √(Gx² + Gy²)",
        "description": (
            "Directional 3×3 convolution with uniform spatial differencing "
            "for balanced edge sensitivity."
        ),
        "kernels": "Gx: [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]\nGy: [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]"
    },
    OperatorType.LAPLACIAN.value: {
        "title": "Laplacian Operator (2nd Derivative)",
        "order": "Second-order differential operator",
        "formula": "∇²f = ∂²f/∂x² + ∂²f/∂y²",
        "description": (
            "Isotropic rotation-invariant operator highlighting zero-crossings "
            "and rapid intensity transitions."
        ),
        "kernels": "Standard 3×3: [[0, 1, 0], [1, -4, 1], [0, 1, 0]]"
    }
}


def normalize_to_uint8(image: np.ndarray) -> np.ndarray:
    """
    Normalizes a floating-point image array into an 8-bit unsigned integer
    representation [0, 255] using min-max scaling.

    Args:
        image: Input numerical array (2D grayscale or gradient magnitude).

    Returns:
        np.ndarray: Normalized 8-bit image array of type uint8.
    """
    if image is None:
        raise ValueError("Cannot normalize None image.")

    if not isinstance(image, np.ndarray):
        raise TypeError(f"Expected numpy.ndarray, got {type(image)}")

    # Handle constant image case (zero variance)
    min_val, max_val = float(image.min()), float(image.max())
    if max_val - min_val < 1e-8:
        return np.zeros(image.shape, dtype=np.uint8)

    # Use OpenCV min-max normalization for numerical precision
    normalized = cv2.normalize(
        image,
        dst=None,
        alpha=0,
        beta=255,
        norm_type=cv2.NORM_MINMAX,
        dtype=cv2.CV_8U
    )
    return normalized


def apply_sobel(
    gray_image: np.ndarray,
    return_components: bool = False
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Applies the Sobel edge detection operator to a grayscale image.

    Calculates:
    - Gx: Horizontal gradient using Sobel X operator (3x3 kernel).
    - Gy: Vertical gradient using Sobel Y operator (3x3 kernel).
    - Combined gradient magnitude: G = sqrt(Gx^2 + Gy^2).
    - Normalizes the output to 8-bit [0, 255] for visual display.

    Args:
        gray_image: Single-channel 2D grayscale image array (uint8 or float).
        return_components: If True, returns (magnitude, gx_norm, gy_norm).

    Returns:
        np.ndarray (or Tuple): Normalized 8-bit gradient magnitude image.
    """
    if gray_image is None or not isinstance(gray_image, np.ndarray):
        raise ValueError("Invalid input: gray_image must be a valid numpy ndarray.")

    # Validate 2D dimensions
    if gray_image.ndim != 2:
        gray_image = convert_to_grayscale(gray_image)

    # 1. Compute horizontal gradient (Gx) using Sobel X (dx=1, dy=0)
    # Using 64-bit float to preserve negative gradients without underflow
    gx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)

    # 2. Compute vertical gradient (Gy) using Sobel Y (dx=0, dy=1)
    gy = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)

    # 3. Compute combined gradient magnitude G = sqrt(Gx^2 + Gy^2)
    magnitude = np.hypot(gx, gy)

    # 4. Normalize magnitude to 8-bit [0, 255]
    magnitude_norm = normalize_to_uint8(magnitude)

    if return_components:
        gx_norm = normalize_to_uint8(np.absolute(gx))
        gy_norm = normalize_to_uint8(np.absolute(gy))
        return magnitude_norm, gx_norm, gy_norm

    return magnitude_norm


def apply_prewitt(
    gray_image: np.ndarray,
    return_components: bool = False
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Applies the Prewitt edge detection operator to a grayscale image.

    Defines:
    - Horizontal Prewitt kernel: [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
    - Vertical Prewitt kernel:   [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
    Applies kernels via 2D spatial convolution (cv2.filter2D), calculates
    the combined gradient magnitude G = sqrt(Gx^2 + Gy^2), and normalizes.

    Args:
        gray_image: Single-channel 2D grayscale image array.
        return_components: If True, returns (magnitude, gx_norm, gy_norm).

    Returns:
        np.ndarray (or Tuple): Normalized 8-bit gradient magnitude image.
    """
    if gray_image is None or not isinstance(gray_image, np.ndarray):
        raise ValueError("Invalid input: gray_image must be a valid numpy ndarray.")

    if gray_image.ndim != 2:
        gray_image = convert_to_grayscale(gray_image)

    # 1. Define horizontal (Kx) and vertical (Ky) Prewitt convolution kernels
    kernel_x = np.array([
        [-1.0, 0.0, 1.0],
        [-1.0, 0.0, 1.0],
        [-1.0, 0.0, 1.0]
    ], dtype=np.float64)

    kernel_y = np.array([
        [-1.0, -1.0, -1.0],
        [ 0.0,  0.0,  0.0],
        [ 1.0,  1.0,  1.0]
    ], dtype=np.float64)

    # 2. Convolve image with kernels using cv2.filter2D with float64 precision
    gx = cv2.filter2D(gray_image, cv2.CV_64F, kernel_x)
    gy = cv2.filter2D(gray_image, cv2.CV_64F, kernel_y)

    # 3. Calculate combined gradient magnitude
    magnitude = np.hypot(gx, gy)

    # 4. Normalize output to [0, 255]
    magnitude_norm = normalize_to_uint8(magnitude)

    if return_components:
        gx_norm = normalize_to_uint8(np.absolute(gx))
        gy_norm = normalize_to_uint8(np.absolute(gy))
        return magnitude_norm, gx_norm, gy_norm

    return magnitude_norm


def apply_laplacian(
    gray_image: np.ndarray,
    ksize: int = 3
) -> np.ndarray:
    """
    Applies the Laplacian 2nd-derivative operator to a grayscale image.

    Calculates:
    - ∇²f = ∂²f/∂x² + ∂²f/∂y²
    - Generates edge visualization using absolute second-derivative response.
    - Normalizes the output into an 8-bit [0, 255] image.

    Args:
        gray_image: Single-channel 2D grayscale image array.
        ksize: Aperture size used to compute the second-derivative filters (must be positive and odd).

    Returns:
        np.ndarray: Normalized 8-bit Laplacian edge response image.
    """
    if gray_image is None or not isinstance(gray_image, np.ndarray):
        raise ValueError("Invalid input: gray_image must be a valid numpy ndarray.")

    if gray_image.ndim != 2:
        gray_image = convert_to_grayscale(gray_image)

    # 1. Apply Laplacian operator with 64-bit floating point precision
    laplacian_response = cv2.Laplacian(gray_image, cv2.CV_64F, ksize=ksize)

    # 2. Take absolute values to highlight edge boundaries on both sides of zero-crossings
    abs_laplacian = np.absolute(laplacian_response)

    # 3. Normalize result for visual display [0, 255]
    laplacian_norm = normalize_to_uint8(abs_laplacian)

    return laplacian_norm


def process_image(
    image: np.ndarray,
    operator: str
) -> np.ndarray:
    """
    Main dispatch function to execute edge detection on an input image.
    Converts color inputs to grayscale first (per FR-03) and leaves
    the input image unaltered.

    Args:
        image: Original input image (BGR, BGRA, or Grayscale).
        operator: Edge detection algorithm name ('Sobel', 'Prewitt', or 'Laplacian').

    Returns:
        np.ndarray: Normalized 8-bit processed edge image.
    """
    if image is None:
        raise ValueError("Input image cannot be None.")

    # Convert to grayscale first (requirement FR-03)
    gray = convert_to_grayscale(image)

    # Dispatch to appropriate operator
    op_clean = str(operator).strip()

    if op_clean in (OperatorType.SOBEL.value, "Sobel Operator", "sobel"):
        return apply_sobel(gray)
    elif op_clean in (OperatorType.PREWITT.value, "Prewitt Operator", "prewitt"):
        return apply_prewitt(gray)
    elif op_clean in (OperatorType.LAPLACIAN.value, "Laplacian Operator", "laplacian"):
        return apply_laplacian(gray)
    elif op_clean in ("Grayscale", "Grayscale (Pre-processing)", "grayscale"):
        return gray
    else:
        raise ValueError(
            f"Unknown edge detection operator: '{operator}'. "
            f"Available options: {list(OPERATOR_DETAILS.keys())}"
        )


def run_all_operators(image: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Executes Sobel, Prewitt, and Laplacian operators on the input image.
    Preserves the original image unmodified.

    Args:
        image: Original input image.

    Returns:
        Dict[str, np.ndarray]: Dictionary with 'original', 'grayscale', 'sobel', 'prewitt', 'laplacian'.
    """
    if image is None:
        raise ValueError("Cannot run operators on None image.")

    gray = convert_to_grayscale(image)
    sobel_out = apply_sobel(gray)
    prewitt_out = apply_prewitt(gray)
    laplacian_out = apply_laplacian(gray)

    return {
        "original": image.copy(),
        "grayscale": gray,
        "sobel": sobel_out,
        "prewitt": prewitt_out,
        "laplacian": laplacian_out
    }


def compute_edge_statistics(results: Dict[str, np.ndarray], threshold: int = 30) -> Dict[str, Dict[str, Any]]:
    """
    Calculates analytical edge statistics for comparison:
    - Mean gradient intensity
    - Max gradient intensity
    - Percentage of detected edge pixels (pixels > threshold)
    - Standard deviation

    Args:
        results: Dictionary containing operator results.
        threshold: Intensity threshold to classify a pixel as an edge.

    Returns:
        Dict mapping operator name to metric dictionary.
    """
    stats = {}
    for op_name in ["sobel", "prewitt", "laplacian"]:
        if op_name in results:
            img = results[op_name]
            total_pixels = img.size
            edge_pixels = int(np.count_nonzero(img > threshold))
            edge_density = (edge_pixels / total_pixels) * 100.0

            stats[op_name] = {
                "mean_intensity": float(np.mean(img)),
                "std_intensity": float(np.std(img)),
                "max_intensity": int(np.max(img)),
                "edge_pixel_count": edge_pixels,
                "edge_density_pct": round(edge_density, 2)
            }
    return stats


def create_comparison_figure(
    results: Dict[str, np.ndarray],
    image_title: str = "Input Image"
) -> Figure:
    """
    Generates a clean, publication-grade 2x2 comparison Matplotlib Figure displaying:
    1. Original Input Image (in RGB color)
    2. Sobel Edge Magnitude
    3. Prewitt Edge Magnitude
    4. Laplacian Second-Derivative Response

    Subplot spacing is calibrated to guarantee zero overlapping titles and crisp rendering.

    Args:
        results: Dictionary from run_all_operators().
        image_title: Name of the input image for the figure heading.

    Returns:
        matplotlib.figure.Figure: Configured Figure object.
    """
    fig = Figure(figsize=(10, 7.5), dpi=100, facecolor="#F8FAFC")
    # Carefully tuned margins to prevent any title collision
    fig.subplots_adjust(top=0.92, bottom=0.06, left=0.06, right=0.94, hspace=0.24, wspace=0.14)

    # 1. Original Image (Top-Left)
    ax1 = fig.add_subplot(2, 2, 1)
    orig = results["original"]
    if orig.ndim == 3 and orig.shape[2] == 3:
        ax1.imshow(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB))
    else:
        ax1.imshow(orig, cmap="gray")
    ax1.set_title("1. Original Image (Input)", fontsize=10, fontweight="bold", pad=6, color="#0F172A")
    ax1.axis("off")

    # 2. Sobel Operator (Top-Right)
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.imshow(results["sobel"], cmap="gray")
    ax2.set_title("2. Sobel Operator  |  G = √(Gx² + Gy²)", fontsize=10, fontweight="bold", pad=6, color="#0F172A")
    ax2.axis("off")

    # 3. Prewitt Operator (Bottom-Left)
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.imshow(results["prewitt"], cmap="gray")
    ax3.set_title("3. Prewitt Operator  |  G = √(Gx² + Gy²)", fontsize=10, fontweight="bold", pad=6, color="#0F172A")
    ax3.axis("off")

    # 4. Laplacian Operator (Bottom-Right)
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.imshow(results["laplacian"], cmap="gray")
    ax4.set_title("4. Laplacian Operator  |  |∇²f|", fontsize=10, fontweight="bold", pad=6, color="#0F172A")
    ax4.axis("off")

    return fig


def save_comparison_figure(
    fig: Figure,
    file_path: str,
    dpi: int = 300
) -> bool:
    """
    Saves a Matplotlib Figure to disk with high DPI resolution.

    Args:
        fig: Matplotlib Figure instance.
        file_path: Destination file path.
        dpi: Output image resolution (dots per inch).

    Returns:
        bool: True if successfully saved, False otherwise.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        fig.savefig(file_path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
        return True
    except Exception as e:
        print(f"Error saving comparison figure to {file_path}: {e}")
        return False
