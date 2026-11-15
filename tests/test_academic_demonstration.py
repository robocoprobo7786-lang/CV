"""
Comprehensive Test Suite for Academic Demonstration & Validation
Covers Part A (GUI), Part B (Comparison), Part C (Output Management), and Part D (Testing).

Course: Computer Vision (256PUPC275)
"""

import os
import sys
import numpy as np
import cv2
import tkinter as tk

# Ensure workspace root is in sys.path
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
    get_unique_filepath,
    save_image
)
from src.edge_detection import (
    apply_sobel,
    apply_prewitt,
    apply_laplacian,
    process_image,
    run_all_operators,
    compute_edge_statistics,
    create_comparison_figure,
    save_comparison_figure
)
from src.gui import EdgeDetectionApp, ComparisonWindow


def run_comprehensive_tests():
    print("=" * 76)
    print("ACADEMIC DEMONSTRATION VERIFICATION & REGRESSION SUITE")
    print("Course: Computer Vision (256PUPC275) - Topic 3: Edge Detection")
    print("=" * 76)

    # -------------------------------------------------------------
    # 1. TEST: IMAGE UPLOAD & FORMAT SUPPORT (JPG, JPEG, PNG, BMP)
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Image Upload & Validation across Formats...")
    formats = ["sample.png", "sample.jpg", "sample.jpeg", "sample.bmp", "sample_large.png"]
    for fname in formats:
        fpath = os.path.join(BASE_DIR, "data", "input", fname)
        is_valid, msg = validate_image_path(fpath)
        assert is_valid, f"Validation failed for {fname}: {msg}"

        img = load_image(fpath)
        assert img is not None and isinstance(img, np.ndarray), f"OpenCV failed to load {fname}"
        meta = get_image_metadata(fpath, img)
        assert meta["channels"] in (1, 3, 4), f"Invalid channel count for {fname}"
        print(f"  ✓ {fname:<18} Loaded successfully: Shape={str(img.shape):<15} {meta['filesize']}")

    # -------------------------------------------------------------
    # 2. TEST: INVALID IMAGE HANDLING (ERROR RESILIENCE)
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Invalid Image Handling & Error Recovery...")
    # Unsupported file extension
    v_txt, m_txt = validate_image_path(os.path.join(BASE_DIR, "data", "input", "invalid_doc.txt"))
    assert not v_txt, "Validation must reject .txt"
    print(f"  ✓ Rejected unsupported file: {m_txt}")

    # Zero-byte empty file
    v_empty, m_empty = validate_image_path(os.path.join(BASE_DIR, "data", "input", "empty_file.png"))
    assert not v_empty, "Validation must reject 0-byte file"
    print(f"  ✓ Rejected empty 0-byte file: {m_empty}")

    # Non-existent file
    v_miss, m_miss = validate_image_path(os.path.join(BASE_DIR, "data", "input", "missing_file_xyz.jpg"))
    assert not v_miss, "Validation must reject missing file"
    print(f"  ✓ Rejected non-existent file path: {m_miss}")

    # -------------------------------------------------------------
    # 3. TEST: GRAYSCALE CONVERSION & IMMUTABILITY
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing Grayscale Preprocessing (FR-03) & Master Immutability...")
    sample_path = os.path.join(BASE_DIR, "data", "input", "sample.png")
    original_bgr = load_image(sample_path)
    bgr_snapshot = original_bgr.copy()

    gray = convert_to_grayscale(original_bgr)
    assert gray.ndim == 2, "Grayscale image must be single-channel 2D"
    assert gray.dtype == np.uint8, "Grayscale dtype must be uint8"
    assert gray.shape[:2] == original_bgr.shape[:2], "Spatial dimensions must match"
    assert np.array_equal(original_bgr, bgr_snapshot), "Original image mutated during grayscale conversion!"
    print("  ✓ Grayscale conversion produced 8-bit single-channel representation.")
    print("  ✓ Verified original image is strictly preserved in memory without modification.")

    # -------------------------------------------------------------
    # 4. TEST: SOBEL, PREWITT & LAPLACIAN ALGORITHMS
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing Sobel, Prewitt, and Laplacian Operators...")
    # Sobel
    sobel_out = apply_sobel(gray)
    assert sobel_out.shape == gray.shape and sobel_out.dtype == np.uint8
    assert sobel_out.min() >= 0 and sobel_out.max() <= 255
    print(f"  ✓ Sobel Operator: min={sobel_out.min()}, max={sobel_out.max()} (uint8 normalized)")

    # Prewitt
    prewitt_out = apply_prewitt(gray)
    assert prewitt_out.shape == gray.shape and prewitt_out.dtype == np.uint8
    assert prewitt_out.min() >= 0 and prewitt_out.max() <= 255
    print(f"  ✓ Prewitt Operator: min={prewitt_out.min()}, max={prewitt_out.max()} (uint8 normalized)")

    # Laplacian
    laplacian_out = apply_laplacian(gray)
    assert laplacian_out.shape == gray.shape and laplacian_out.dtype == np.uint8
    assert laplacian_out.min() >= 0 and laplacian_out.max() <= 255
    print(f"  ✓ Laplacian Operator: min={laplacian_out.min()}, max={laplacian_out.max()} (uint8 normalized)")

    # Verify algorithmic distinctions
    diff_sobel_prewitt = np.mean(np.abs(sobel_out.astype(float) - prewitt_out.astype(float)))
    diff_sobel_laplacian = np.mean(np.abs(sobel_out.astype(float) - laplacian_out.astype(float)))
    assert diff_sobel_prewitt > 0, "Sobel and Prewitt outputs must not be identical"
    assert diff_sobel_laplacian > 0, "Sobel and Laplacian outputs must not be identical"
    print(f"  ✓ Confirmed distinct mathematical responses (Sobel vs Prewitt diff: {diff_sobel_prewitt:.2f})")

    # -------------------------------------------------------------
    # 5. TEST: COMPARISON FEATURE (PART B)
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing Multi-Algorithm Comparison Feature (Part B)...")
    comp_results = run_all_operators(original_bgr)
    assert "original" in comp_results
    assert "sobel" in comp_results
    assert "prewitt" in comp_results
    assert "laplacian" in comp_results
    print("  ✓ run_all_operators executed all 3 edge operators and preserved reference image.")

    stats = compute_edge_statistics(comp_results, threshold=30)
    assert "sobel" in stats and "prewitt" in stats and "laplacian" in stats
    for op, data in stats.items():
        print(f"    - {op.capitalize()}: Mean={data['mean_intensity']:.1f}, Edge Pixels={data['edge_pixel_count']:,}, Density={data['edge_density_pct']}%")

    fig = create_comparison_figure(comp_results, "sample.png")
    assert fig is not None, "Failed to create Matplotlib comparison figure"
    assert len(fig.axes) == 4, f"Expected 4 subplots (2x2 grid), got {len(fig.axes)}"
    print("  ✓ Matplotlib 4-panel comparison figure generated successfully.")

    # -------------------------------------------------------------
    # 6. TEST: OUTPUT MANAGEMENT & NON-DESTRUCTIVE SAVING (PART C)
    # -------------------------------------------------------------
    print("\n[TEST 6] Testing Output Management (Part C)...")
    out_dir = os.path.join(BASE_DIR, "results", "output")
    vis_dir = os.path.join(BASE_DIR, "results", "visualizations")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(vis_dir, exist_ok=True)

    # Test collision-free filename generator
    path1 = get_unique_filepath(out_dir, "collision_test", ".png")
    # Touch file
    with open(path1, "w") as f:
        f.write("test")
    path2 = get_unique_filepath(out_dir, "collision_test", ".png")
    assert path1 != path2, "get_unique_filepath failed to generate unique name"
    assert path2.endswith("collision_test_1.png"), f"Unexpected unique name format: {path2}"
    print(f"  ✓ Non-destructive naming verified: '{os.path.basename(path1)}' -> '{os.path.basename(path2)}'")

    # Clean up collision test files
    os.remove(path1)

    # Test saving comparison visualization
    vis_path = get_unique_filepath(vis_dir, "academic_demo_comparison", ".png")
    vis_success = save_comparison_figure(fig, vis_path, dpi=150)
    assert vis_success, "Failed to save comparison figure"
    assert os.path.exists(vis_path) and os.path.getsize(vis_path) > 0
    print(f"  ✓ Saved comparison visualization to: {os.path.relpath(vis_path, BASE_DIR)}")

    # Test saving processed edge output
    edge_out_path = get_unique_filepath(out_dir, "academic_demo_sobel", ".png")
    edge_success, saved_edge_path = save_image(edge_out_path, sobel_out, overwrite=True)
    assert edge_success and os.path.exists(saved_edge_path) and os.path.getsize(saved_edge_path) > 0
    print(f"  ✓ Saved processed edge output to: {os.path.relpath(saved_edge_path, BASE_DIR)}")

    # -------------------------------------------------------------
    # 7. TEST: TKINTER GUI LIFECYCLE & RESET ACTION
    # -------------------------------------------------------------
    print("\n[TEST 7] Testing Tkinter Desktop GUI Lifecycle & Comparison Window Integration...")
    root = tk.Tk()
    root.withdraw()
    app = EdgeDetectionApp(root)

    # Verify initial control state
    assert app.original_cv_image is None
    assert str(app.btn_process["state"]) == "disabled"
    assert str(app.btn_compare["state"]) == "disabled"
    assert str(app.btn_save["state"]) == "disabled"
    print("  ✓ Initial GUI states validated (Buttons properly disabled).")

    # Simulate Image Upload
    app.current_file_path = sample_path
    app.original_cv_image = original_bgr.copy()
    app.original_pil_image = cv_to_pil(app.original_cv_image)
    app.btn_process.config(state="normal")
    app.btn_compare.config(state="normal")
    app.btn_convert_gray.config(state="normal")
    app._refresh_original_preview()

    # Process Sobel through GUI
    app.selected_operator.set("Sobel")
    app.on_process_image()
    assert app.processed_cv_image is not None
    assert "Sobel" in app.lbl_proc_badge["text"]
    assert str(app.btn_save["state"]) == "normal"
    print("  ✓ Executed Sobel processing via GUI.")

    # Switch to Prewitt without re-uploading
    app.selected_operator.set("Prewitt")
    app.on_process_image()
    assert "Prewitt" in app.lbl_proc_badge["text"]
    print("  ✓ Switched to Prewitt and re-processed without re-uploading.")

    # Switch to Laplacian without re-uploading
    app.selected_operator.set("Laplacian")
    app.on_process_image()
    assert "Laplacian" in app.lbl_proc_badge["text"]
    print("  ✓ Switched to Laplacian and re-processed without re-uploading.")

    # Launch Comparison Window through GUI
    comp_win = ComparisonWindow(root, comp_results, "sample.png", app)
    assert comp_win is not None
    print("  ✓ Multi-algorithm comparison studio launched via GUI.")
    comp_win.destroy()

    # Test Reset
    app.on_reset()
    assert app.original_cv_image is None
    assert app.processed_cv_image is None
    assert app.grayscale_cv_image is None
    assert str(app.btn_process["state"]) == "disabled"
    assert str(app.btn_compare["state"]) == "disabled"
    assert str(app.btn_save["state"]) == "disabled"
    assert "Application reset" in app.lbl_status["text"]
    print("  ✓ Reset functionality restored entire application to clean initial state.")

    root.destroy()

    print("\n" + "=" * 76)
    print(">>> 100% OF TESTS PASSED! READY FOR ACADEMIC DEMONSTRATION <<<")
    print("=" * 76)


if __name__ == "__main__":
    run_comprehensive_tests()

