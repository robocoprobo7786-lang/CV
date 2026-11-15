"""
Unit & Integration Test Suite for Image Loading, Grayscale Preprocessing & GUI
Course: Computer Vision (256PUPC275)
"""

import os
import sys
import numpy as np
from PIL import Image
import tkinter as tk

# Ensure workspace root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.image_utils import (
    validate_image_path,
    load_image,
    convert_to_grayscale,
    cv_to_pil,
    resize_image_aspect_ratio,
    get_image_metadata,
    SUPPORTED_EXTENSIONS
)
from src.gui import EdgeDetectionApp


def run_tests():
    print("=" * 68)
    print("RUNNING IMAGE PIPELINE & GUI PREPROCESSING TESTS")
    print("=" * 68)

    # 1. Validation and Format Support
    print("\n[TEST 1] Testing Validation & Format Support (JPG, JPEG, PNG, BMP)...")
    test_files = ["sample.png", "sample.jpg", "sample.jpeg", "sample.bmp", "sample_large.png"]
    for f in test_files:
        p = os.path.join(BASE_DIR, "data", "input", f)
        valid, msg = validate_image_path(p)
        assert valid, f"Validation unexpectedly failed for {f}: {msg}"
        print(f"  ✓ Validated {f}: {msg}")

    # Negative validation tests
    v1, m1 = validate_image_path(os.path.join(BASE_DIR, "data", "input", "invalid_doc.txt"))
    assert not v1, "Validation should reject .txt files"
    print(f"  ✓ Rejected unsupported file extension (.txt): {m1}")

    v2, m2 = validate_image_path(os.path.join(BASE_DIR, "data", "input", "empty_file.png"))
    assert not v2, "Validation should reject 0-byte files"
    print(f"  ✓ Rejected 0-byte file: {m2}")

    v3, m3 = validate_image_path(os.path.join(BASE_DIR, "data", "input", "non_existent.jpg"))
    assert not v3, "Validation should reject non-existent paths"
    print(f"  ✓ Rejected non-existent file path: {m3}")

    # 2. Loading via OpenCV & Metadata Extraction
    print("\n[TEST 2] Testing OpenCV Loading & Metadata Extraction...")
    for f in test_files:
        p = os.path.join(BASE_DIR, "data", "input", f)
        img = load_image(p)
        assert img is not None, f"Failed to load {f} using OpenCV"
        assert isinstance(img, np.ndarray), "Loaded image must be a numpy ndarray"
        meta = get_image_metadata(p, img)
        print(f"  ✓ {f:<18} Shape={str(img.shape):<14} Mode={meta['color_mode']:<18} Size={meta['filesize']}")

    # 3. Grayscale Conversion and Immutability of Original Image
    print("\n[TEST 3] Testing Grayscale Conversion (FR-03) & Original Immutability...")
    sample_path = os.path.join(BASE_DIR, "data", "input", "sample.png")
    original = load_image(sample_path)
    original_snapshot = original.copy()

    gray = convert_to_grayscale(original)
    assert len(gray.shape) == 2, "Grayscale image must be 2D"
    assert gray.dtype == np.uint8, "Grayscale image dtype must be uint8"
    assert gray.shape[:2] == original.shape[:2], "Spatial dimensions (H, W) must match"

    # Strict check: Original image is NOT modified
    assert np.array_equal(original, original_snapshot), "Original image was mutated in-place!"
    print("  ✓ Converted BGR color image to 8-bit single-channel grayscale.")
    print("  ✓ Confirmed original image array remains 100% unaltered (immutable).")

    # 4. Aspect Ratio Preservation & Large Resolution Scaling
    print("\n[TEST 4] Testing Aspect Ratio Preservation & Large-Res Scaling...")
    large_path = os.path.join(BASE_DIR, "data", "input", "sample_large.png")
    large_img = load_image(large_path)
    large_pil = cv_to_pil(large_img)
    orig_w, orig_h = large_pil.size
    orig_aspect = orig_w / orig_h

    # Test scaling to a 400x300 canvas
    target_max_w, target_max_h = 400, 300
    resized_pil = resize_image_aspect_ratio(large_pil, target_max_w, target_max_h)
    new_w, new_h = resized_pil.size
    new_aspect = new_w / new_h

    assert new_w <= target_max_w, f"Width {new_w} exceeds target {target_max_w}"
    assert new_h <= target_max_h, f"Height {new_h} exceeds target {target_max_h}"
    assert abs(orig_aspect - new_aspect) < 0.02, "Aspect ratio was distorted!"
    print(f"  ✓ Original: {orig_w}x{orig_h} (Aspect: {orig_aspect:.4f})")
    print(f"  ✓ Scaled:   {new_w}x{new_h} (Aspect: {new_aspect:.4f})")
    print("  ✓ Zero stretching or distortion detected.")

    # 5. Tkinter GUI Integration
    print("\n[TEST 5] Testing Tkinter GUI Integration & Reset Action...")
    root = tk.Tk()
    root.withdraw()
    app = EdgeDetectionApp(root)

    # Verify initial state
    assert app.original_cv_image is None
    assert app.grayscale_cv_image is None
    assert str(app.btn_convert_gray["state"]) == "disabled"
    print("  ✓ Initial GUI state verified (Controls appropriately disabled).")

    # Test image upload integration across formats
    for f in ["sample.png", "sample.jpg", "sample.bmp"]:
        p = os.path.join(BASE_DIR, "data", "input", f)
        loaded = load_image(p)
        app.current_file_path = p
        app.original_cv_image = loaded.copy()
        app.original_pil_image = cv_to_pil(app.original_cv_image)
        app._refresh_original_preview()

        assert app._tk_orig_img is not None, "Original preview image failed to create PhotoImage"

        # Trigger grayscale conversion through GUI method
        app.on_convert_to_grayscale(silent=True)
        assert app.grayscale_cv_image is not None, "Grayscale image state not set"
        assert len(app.grayscale_cv_image.shape) == 2, "Grayscale state is not 2D"
        assert app._tk_proc_img is not None, "Processed preview failed to create PhotoImage"
        assert "Grayscale" in app.lbl_proc_badge["text"]
        print(f"  ✓ GUI image display and grayscale preview verified for {f}")

    # Test Reset Functionality
    app.on_reset()
    assert app.original_cv_image is None, "Reset failed to clear original image"
    assert app.grayscale_cv_image is None, "Reset failed to clear grayscale image"
    assert app.processed_cv_image is None, "Reset failed to clear processed image"
    assert app._tk_orig_img is None, "Reset failed to clear Tk original image cache"
    assert app._tk_proc_img is None, "Reset failed to clear Tk processed image cache"
    assert str(app.btn_convert_gray["state"]) == "disabled", "Reset failed to disable button"
    assert "Application reset" in app.lbl_status["text"], "Reset status message incorrect"
    print("  ✓ GUI Reset functionality verified (all state, caches, and UI elements restored).")

    root.destroy()
    print("\n" + "=" * 68)
    print("ALL TESTS COMPLETED SUCCESSFULLY! (100% PASS)")
    print("=" * 68)


if __name__ == "__main__":
    run_tests()

