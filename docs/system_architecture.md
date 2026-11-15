# System Architecture & Technical Design Document

**Course:** Computer Vision (256PUPC275)  
**Topic:** Option 2, Topic 3 — Edge Detection Using Sobel, Prewitt, and Laplacian Operators  
**System:** Desktop Computer Vision Application Suite  

---

## 1. Architectural Overview & Design Philosophy

The software is designed as a standalone, production-grade Python desktop application adhering strictly to the **Model-View-Controller (MVC)** architectural pattern. 

### Core Architectural Principles:
1. **Strict Decoupling:** The graphical presentation layer (`src/gui.py`) does not contain mathematical convolution kernels or image manipulation logic. Conversely, the computational engines (`src/edge_detection.py` and `src/image_utils.py`) maintain zero dependencies on Tkinter or UI widgets.
2. **Master Image Immutability:** When an image is loaded, it is stored as an immutable master copy in memory. All preprocessing (e.g., RGB to Grayscale) and edge detection operators execute on cloned buffers, guaranteeing that the original image is preserved for side-by-side comparison.
3. **Numerical Precision Safeguards:** Spatial convolutions are performed using 64-bit double-precision floating-point arrays (`cv2.CV_64F`), avoiding 8-bit integer truncation and signed underflow for negative gradient components.
4. **Platform Independence & Unicode Resilience:** On Windows systems, standard OpenCV file reading (`cv2.imread`) frequently fails on paths containing non-ASCII Unicode characters or spaces. The architecture circumvents this via an 8-bit binary buffer pipeline using `np.fromfile` and `cv2.imdecode`.

---

## 2. High-Level System Architecture Diagram

```
+--------------------------------------------------------------------------------+
|                             ENTRY POINT: main.py                               |
|        - Python >= 3.8 Version Gate                                            |
|        - Tkinter Tk() Root Lifecycle Initialization                            |
+--------------------------------------------------------------------------------+
                                       │
                                       ▼
+--------------------------------------------------------------------------------+
|                         VIEW & CONTROLLER: src/gui.py                          |
|  - EdgeDetectionApp                                                            |
|      ├── Control Sidebar (Upload, Preprocess, Dropdown, Process, Compare, Save) |
|      ├── Dual Canvas Viewports (Original vs. Processed with Lanczos Scaling)   |
|      └── Diagnostic Status Bar                                                 |
|  - ComparisonWindow (Modal 2x2 Comparative Studio with Quantitative Metrics)   |
+--------------------------------------------------------------------------------+
              │                                                │
              ▼                                                ▼
+-----------------------------+               +----------------------------------+
|    UTILITIES: image_utils   |               |   ALGORITHMIC ENGINE: edge_det   |
|  - validate_image_path()    |               |  - apply_sobel()                 |
|  - load_image() (imdecode)  |               |  - apply_prewitt()               |
|  - convert_to_grayscale()   |               |  - apply_laplacian()             |
|  - cv_to_pil() / resize()   |               |  - compute_edge_statistics()     |
|  - get_unique_filepath()    |               |  - create_comparison_figure()    |
|  - save_image()             |               |  - normalize_to_uint8()          |
+-----------------------------+               +----------------------------------+
              │                                                │
              └────────────────────────┬───────────────────────┘
                                       ▼
+--------------------------------------------------------------------------------+
|                                DATA & RESULTS                                  |
|  - data/input/               (JPG, JPEG, PNG, BMP, Large-Res)                  |
|  - results/output/           (Exported 8-bit processed edge outputs)           |
|  - results/visualizations/   (Publication-grade 300 DPI 4-panel figures)        |
+--------------------------------------------------------------------------------+
```

---

## 3. Modular Component Breakdown

### 3.1 `main.py` — Application Entry Point
- **Responsibility:** Verifies that the host Python runtime satisfies the minimum version requirement ($\ge 3.8$) and initializes the Tkinter event loop.
- **Error Trapping:** Catches startup environment exceptions and writes formatted diagnostic logs to `stderr` if graphical initialization fails.

### 3.2 `src/gui.py` — Presentation & Event Orchestration
- **Class `EdgeDetectionApp`:**
  - Manages primary application window geometry ($1180 \times 720$), custom `ttk` styling (`clam` engine), and high-contrast color palette.
  - Implements dynamic algorithm selection via `ttk.Combobox` linked to a reactive `StringVar`.
  - Maintains image state variables: `original_cv_image`, `grayscale_cv_image`, `processed_cv_image`, and display references (`ImageTk.PhotoImage`).
  - Implements debounced canvas resize observers to ensure sharp preview rendering upon window maximize/restore.
- **Class `ComparisonWindow`:**
  - Independent modal `Toplevel` window for multi-operator visual and statistical evaluation.
  - Embeds a Matplotlib `FigureCanvasTkAgg` canvas rendering a calibrated $2 \times 2$ comparative grid.
  - Generates a uniform 3-column quantitative analytics bar reporting mean gradient magnitudes, absolute edge pixel counts, and surface edge density percentages.

### 3.3 `src/image_utils.py` — File I/O & Transformation Utilities
- **Unicode-Safe Ingestion (`load_image`):**
  ```python
  buffer = np.fromfile(file_path, dtype=np.uint8)
  img = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
  ```
- **Validation Engine (`validate_image_path`):** Verifies file existence, verifies that file size $> 0$ bytes, and validates extensions against `{.jpg, .jpeg, .png, .bmp}`.
- **Aspect-Ratio Preserving Scaler (`resize_image_aspect_ratio`):**
  Computes the scale factor $s = \min\left(\frac{W_{\text{box}}}{W_{\text{orig}}}, \frac{H_{\text{box}}}{H_{\text{orig}}}\right)$ and resamples using high-order **Lanczos filtering** to eliminate aliasing artifacts.
- **Collision-Free Path Resolver (`get_unique_filepath`):** Scans the destination directory and appends incremental numeric suffixes (`_1`, `_2`) if a file with the target name exists, preventing destructive overwrites.

### 3.4 `src/edge_detection.py` — Mathematical Convolution Engine
- **Sobel Operator (`apply_sobel`):**
  Computes 64-bit spatial derivatives $G_x = \text{Sobel}(I, \text{CV\_64F}, 1, 0)$ and $G_y = \text{Sobel}(I, \text{CV\_64F}, 0, 1)$. Combines responses via Euclidean norm $G = \text{hypot}(G_x, G_y)$.
- **Prewitt Operator (`apply_prewitt`):**
  Defines discrete kernels $\mathbf{K}_x, \mathbf{K}_y$ and applies spatial 2D filtering via `cv2.filter2D(..., ddepth=cv2.CV_64F)`. Combines responses via Euclidean norm $G = \text{hypot}(G_x, G_y)$.
- **Laplacian Operator (`apply_laplacian`):**
  Applies the second-derivative isotropic Laplacian operator $\nabla^2 f$ via `cv2.Laplacian(..., ddepth=cv2.CV_64F, ksize=3)`. Extracts the absolute response $|\nabla^2 f|$ to identify boundary zero-crossings.
- **Normalization Engine (`normalize_to_uint8`):**
  Linearly maps continuous floating-point responses into $[0, 255]$:
  $$I_{\text{norm}} = \text{clip}\left(\frac{I - \min(I)}{\max(I) - \min(I) + \epsilon} \times 255, 0, 255\right)$$
- **Analytical Metrics Engine (`compute_edge_statistics`):**
  Computes statistical metrics (mean intensity, standard deviation, max intensity, edge pixel count, and edge density percentage above threshold $T=30$).

---

## 4. Computational Pipeline & Dataflow

The end-to-end data processing workflow proceeds through the following deterministic stages:

```
[ Input File on Disk ] (JPG / PNG / BMP)
          │
          ▼  (src/image_utils.load_image via np.fromfile + cv2.imdecode)
[ Master Color Array (BGR) ]  <--- Stored immutably in memory
          │
          ▼  (src/image_utils.convert_to_grayscale via cv2.cvtColor)
[ Grayscale Array (8-bit uint8) ]  <--- Cached for operator execution
          │
          ├─────────────────────────┬─────────────────────────┐
          ▼                         ▼                         ▼
   apply_sobel()            apply_prewitt()          apply_laplacian()
 (cv2.Sobel 64F)          (cv2.filter2D 64F)       (cv2.Laplacian 64F)
          │                         │                         │
   np.hypot(gx, gy)         np.hypot(gx, gy)            np.absolute()
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    ▼
                    normalize_to_uint8() (Min-Max Scaling)
                                    │
                                    ▼
                     [ 8-bit uint8 Processed Image ]
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
      cv_to_pil() + Lanczos                     save_image() / save_fig()
               │                                         │
               ▼                                         ▼
   [ Tkinter GUI Display ]                     [ Disk Export in results/ ]
```

---

## 5. Application State Lifecycle

The application operates as a finite state machine governed by user actions:

| State | Active Controls | Inactive Controls | Trigger Event | Next State |
| :--- | :--- | :--- | :--- | :--- |
| **UNLOADED** | Upload Image | Preprocessing, Process, Compare, Save, Reset | User selects valid image file | `IMAGE_LOADED` |
| **IMAGE_LOADED** | Upload, View Grayscale, Dropdown, Process, Compare, Reset | Save Output | User clicks `Process Image` | `PROCESSED` |
| **PROCESSED** | All controls active (Upload, Preprocess, Dropdown, Process, Compare, Save, Reset) | None | User clicks `Compare All` | `COMPARING` |
| **COMPARING** | Modal Studio Active | None (Main window remains responsive) | User closes comparison studio | `PROCESSED` |
| **RESET** | Upload Image | Preprocessing, Process, Compare, Save, Reset | User clicks `Reset All` | `UNLOADED` |

---

## 6. Testing & Quality Assurance Architecture

The test suite in `tests/` provides complete verification across four testing tiers:

1. **`test_image_pipeline.py`:**
   - Verifies path validation across supported formats (`.png`, `.jpg`, `.jpeg`, `.bmp`).
   - Verifies error rejection for non-existent files, 0-byte corrupted files, and unsupported extensions (`.txt`).
   - Verifies that BGR master arrays remain immutable during grayscale conversion.
   - Verifies that Lanczos scaling preserves exact spatial aspect ratios without geometric distortion.
2. **`test_edge_algorithms.py`:**
   - Validates horizontal gradient ($G_x$), vertical gradient ($G_y$), Euclidean magnitude ($G$), and $[0, 255]$ normalization for Sobel.
   - Validates custom kernel convolutions and Euclidean magnitude for Prewitt.
   - Validates isotropic second-derivative response and absolute value normalization for Laplacian.
   - Confirms algorithmic divergence between Sobel and Prewitt (mean absolute difference $> 0$).
   - Verifies dynamic operator switching without image re-uploading.
3. **`test_academic_demonstration.py`:**
   - Full integration regression test covering GUI lifecycle, output management, non-destructive file collision handling, and Matplotlib figure generation.
   - Executes headlessly with **100% pass rate**.

