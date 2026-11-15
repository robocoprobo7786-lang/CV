"""
Comprehensive Test Suite for Sobel, Prewitt, and Laplacian Edge Detection Algorithms
and GUI Algorithm Switching.
Course: Computer Vision (256PUPC275)
"""

import os
import sys
import numpy as np
import cv2
import tkinter as tk

# Ensure workspace root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.image_utils import load_image, cv_to_pil, convert_to_grayscale
from src.edge_detection import (
    apply_sobel,
    apply_prewitt,
    apply_laplacian,
    normalize_to_uint8,
    process_image,
    OperatorType
)
from src.gui import EdgeDetectionApp


def run_tests():
    print("=" * 72)
    print("RUNNING EDGE DETECTION ALGORITHM & GUI INTEGRATION TESTS")
    print("=" * 72)

    # 1. Load actual input image
    test_image_path = os.path.join(BASE_DIR, "data", "input", "sample.png")
    color_image = load_image(test_image_path)
    assert color_image is not None, f"Failed to load test image: {test_image_path}"
    color_snapshot = color_image.copy()

    gray_image = convert_to_grayscale(color_image)
    assert gray_image.ndim == 2, "Grayscale image must be 2D"

    # --- 2. TEST SOBEL OPERATOR ---
    print("\n[TEST 1] Testing Sobel Operator (Gx, Gy, Combined Magnitude, Normalization)...")
    sobel_mag, sobel_gx, sobel_gy = apply_sobel(gray_image, return_components=True)

    assert sobel_mag.shape == gray_image.shape, "Sobel magnitude shape mismatch"
    assert sobel_gx.shape == gray_image.shape, "Sobel Gx shape mismatch"
    assert sobel_gy.shape == gray_image.shape, "Sobel Gy shape mismatch"
    assert sobel_mag.dtype == np.uint8, "Sobel output must be uint8"
    assert sobel_mag.min() >= 0 and sobel_mag.max() <= 255, "Sobel output out of [0, 255] bounds"
    assert sobel_mag.max() > 0, "Sobel magnitude cannot be completely black for an edge-rich image"

    print(f"  ✓ Sobel X (Gx) min/max: {sobel_gx.min()}/{sobel_gx.max()}, shape: {sobel_gx.shape}")
    print(f"  ✓ Sobel Y (Gy) min/max: {sobel_gy.min()}/{sobel_gy.max()}, shape: {sobel_gy.shape}")
    print(f"  ✓ Sobel Combined Magnitude min/max: {sobel_mag.min()}/{sobel_mag.max()} (uint8 normalized)")

    # --- 3. TEST PREWITT OPERATOR ---
    print("\n[TEST 2] Testing Prewitt Operator (Custom Kernels, Convolutions, Magnitude, Normalization)...")
    prewitt_mag, prewitt_gx, prewitt_gy = apply_prewitt(gray_image, return_components=True)

    assert prewitt_mag.shape == gray_image.shape, "Prewitt magnitude shape mismatch"
    assert prewitt_gx.shape == gray_image.shape, "Prewitt Gx shape mismatch"
    assert prewitt_gy.shape == gray_image.shape, "Prewitt Gy shape mismatch"
    assert prewitt_mag.dtype == np.uint8, "Prewitt output must be uint8"
    assert prewitt_mag.min() >= 0 and prewitt_mag.max() <= 255, "Prewitt output out of [0, 255] bounds"
    assert prewitt_mag.max() > 0, "Prewitt magnitude cannot be empty"

    print(f"  ✓ Prewitt X (Gx) min/max: {prewitt_gx.min()}/{prewitt_gx.max()}, shape: {prewitt_gx.shape}")
    print(f"  ✓ Prewitt Y (Gy) min/max: {prewitt_gy.min()}/{prewitt_gy.max()}, shape: {prewitt_gy.shape}")
    print(f"  ✓ Prewitt Combined Magnitude min/max: {prewitt_mag.min()}/{prewitt_mag.max()} (uint8 normalized)")

    # Compare differences between Sobel and Prewitt (Sobel uses center weight 2, Prewitt uses 1)
    diff_sobel_prewitt = np.abs(sobel_mag.astype(np.float64) - prewitt_mag.astype(np.float64))
    assert np.any(diff_sobel_prewitt > 0), "Sobel and Prewitt outputs should differ in intensity response"
    print(f"  ✓ Verified algorithmic distinction between Sobel and Prewitt (Mean absolute diff: {diff_sobel_prewitt.mean():.2f})")

    # --- 4. TEST LAPLACIAN OPERATOR ---
    print("\n[TEST 3] Testing Laplacian Operator (2nd Derivative, Absolute Value, Normalization)...")
    laplacian_out = apply_laplacian(gray_image)

    assert laplacian_out.shape == gray_image.shape, "Laplacian shape mismatch"
    assert laplacian_out.dtype == np.uint8, "Laplacian output must be uint8"
    assert laplacian_out.min() >= 0 and laplacian_out.max() <= 255, "Laplacian out of [0, 255] bounds"
    assert laplacian_out.max() > 0, "Laplacian output cannot be empty"

    print(f"  ✓ Laplacian 2nd derivative response min/max: {laplacian_out.min()}/{laplacian_out.max()} (uint8 normalized)")

    # --- 5. TEST IMMUTABILITY & ERROR HANDLING ---
    print("\n[TEST 4] Testing Input Immutability & Edge Case Handling...")
    assert np.array_equal(color_image, color_snapshot), "Original color image was mutated by operators!"
    print("  ✓ Original image remained 100% immutable across all operator executions.")

    # Error handling tests
    try:
        process_image(None, "Sobel")
        assert False, "Should raise ValueError for None image"
    except ValueError:
        print("  ✓ Handled None image input gracefully.")

    try:
        process_image(gray_image, "NonExistentOperator")
        assert False, "Should raise ValueError for unknown operator"
    except ValueError:
        print("  ✓ Handled unknown operator name gracefully.")

    # Constant flat image test
    flat_image = np.full((100, 100), 128, dtype=np.uint8)
    flat_sobel = apply_sobel(flat_image)
    assert np.all(flat_sobel == 0), "Edge response for flat uniform image should be zero"
    print("  ✓ Handled uniform flat image correctly (returns zero edge intensity).")

    # --- 6. TEST GUI ALGORITHM SWITCHING (WITHOUT RE-UPLOADING) ---
    print("\n[TEST 5] Testing GUI Dropdown & Dynamic Algorithm Switching...")
    root = tk.Tk()
    root.withdraw()
    app = EdgeDetectionApp(root)

    # Simulate uploading the image once
    app.current_file_path = test_image_path
    app.original_cv_image = color_image.copy()
    app.original_pil_image = cv_to_pil(app.original_cv_image)
    app.btn_process.config(state="normal")
    app.btn_convert_gray.config(state="normal")
    app._refresh_original_preview()

    # Verify Dropdown options
    assert app.combo_algorithm["values"] == ("Sobel", "Prewitt", "Laplacian"), "Dropdown values mismatch"
    print("  ✓ Combobox dropdown contains: Sobel, Prewitt, Laplacian.")

    # 1. Select Sobel and Process
    app.selected_operator.set("Sobel")
    app.on_process_image()
    assert app.processed_cv_image is not None
    assert "Sobel" in app.lbl_proc_badge["text"]
    assert str(app.btn_save["state"]) == "normal"
    sobel_gui_result = app.processed_cv_image.copy()
    print("  ✓ Executed Sobel through GUI, verified display badge and output.")

    # 2. Switch to Prewitt and Process WITHOUT re-uploading
    app.selected_operator.set("Prewitt")
    app.on_process_image()
    assert "Prewitt" in app.lbl_proc_badge["text"]
    prewitt_gui_result = app.processed_cv_image.copy()
    assert not np.array_equal(sobel_gui_result, prewitt_gui_result), "Prewitt output should differ from Sobel"
    print("  ✓ Switched to Prewitt and executed without re-uploading image.")

    # 3. Switch to Laplacian and Process WITHOUT re-uploading
    app.selected_operator.set("Laplacian")
    app.on_process_image()
    assert "Laplacian" in app.lbl_proc_badge["text"]
    laplacian_gui_result = app.processed_cv_image.copy()
    assert not np.array_equal(prewitt_gui_result, laplacian_gui_result), "Laplacian output should differ from Prewitt"
    print("  ✓ Switched to Laplacian and executed without re-uploading image.")

    # 4. Save output test
    out_test_path = os.path.join(BASE_DIR, "results", "output", "test_sobel_out.png")
    cv2.imwrite(out_test_path, sobel_gui_result)
    assert os.path.exists(out_test_path) and os.path.getsize(out_test_path) > 0
    print(f"  ✓ Output successfully written to disk: {os.path.basename(out_test_path)}")

    # 5. Reset test
    app.on_reset()
    assert app.original_cv_image is None
    assert app.processed_cv_image is None
    assert str(app.btn_process["state"]) == "disabled"
    print("  ✓ GUI Reset completed successfully.")

    root.destroy()

    print("\n" + "=" * 72)
    print("ALL EDGE DETECTION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 72)


if __name__ == "__main__":
    run_tests()

