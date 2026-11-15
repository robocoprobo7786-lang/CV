# Desktop Application User Guide: Edge Detection Studio

**Course:** Computer Vision (256PUPC275)  
**Project:** Implementation of Edge Detection Techniques Using Sobel, Prewitt and Laplacian Operators  
**Application:** Standalone Tkinter Computer Vision Desktop Suite  

---

## 1. Introduction

**Edge Detection Studio** is a standalone Python desktop application developed for the Computer Vision (256PUPC275) curriculum. It provides an interactive graphical interface to inspect, preprocess, execute, and comparatively analyze spatial edge detection algorithms—specifically the **Sobel**, **Prewitt**, and **Laplacian** operators.

The software is engineered with a strict Model-View-Controller (MVC) architectural separation, ensuring zero coupling between user interface widgets and mathematical image-processing logic.

---

## 2. System Requirements & Setup

### 2.1 Hardware & OS Compatibility
- **Operating System:** Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Display Resolution:** Minimum $1024 \times 768$ (Optimized for $1920 \times 1080$ and $1366 \times 768$)
- **Memory:** Minimum 512 MB RAM (2 GB recommended for high-resolution images)

### 2.2 Software Prerequisites
- **Python:** Version 3.8 or higher
- **Core Dependencies:**
  - `opencv-python >= 4.8.0` (Image I/O, color conversion, 2D convolution)
  - `numpy >= 1.24.0` (Matrix operations, Euclidean norms)
  - `Pillow >= 10.0.0` (Antialiased image display for Tkinter)
  - `matplotlib >= 3.7.0` (Comparative multi-panel figures)
  - `reportlab >= 4.0.0` (Academic PDF report compilation)
  - `python-pptx >= 0.6.21` (Academic presentation deck compilation)

### 2.3 Installation Steps
```bash
# Clone or navigate to the project directory
cd cv-assignment

# Install dependencies via pip
pip install -r requirements.txt
```

### 2.4 Launching the Application
```bash
python main.py
```

---

## 3. Graphical Interface Overview

The interface consists of a two-column responsive layout: a dedicated **Control Sidebar** on the left and a **Dual-Panel Canvas Viewport** on the right, capped by a top header and a bottom diagnostic status bar.

```
+-----------------------------------------------------------------------------------------+
|                  Implementation of Edge Detection Techniques                            |
|             Sobel, Prewitt and Laplacian Operators • Computer Vision (256PUPC275)        |
+------------------------------------+----------------------------------------------------+
| 1. Image Upload                    |  [ Original Image (Unmodified) ]  [ Processed Output ]
|    [ Upload Image... ]             |  +----------------------------+  +--------------------+
|    File: sample.png                |  |                            |  |                    |
|    Dimensions: 600 x 600           |  |      Input Image           |  |    Edge Output     |
| 2. Preprocessing                   |  |      (Full Color)          |  |   (Normalized)     |
|    [ View Grayscale ]              |  |                            |  |                    |
| 3. Algorithm Selection             |  +----------------------------+  +--------------------+
|    [ Sobel           ▼ ]           |                                                    
|    Formula: G = √(Gx² + Gy²)       |                                                    
| 4. Actions & Demonstration         |                                                    
|    [ ⚡ Process Image ]            |                                                    
|    [ 📊 Compare All Algorithms... ]|                                                    
|    [ 💾 Save Output... ]           |                                                    
|    [ 🔄 Reset All ]                |                                                    
+------------------------------------+----------------------------------------------------+
| ● Ready | Sobel operator completed successfully. Output normalized to [0, 255].         |
+-----------------------------------------------------------------------------------------+
```

### 3.1 Header Banner
- Displays the official project title and course metadata (`256PUPC275`).
- Styled in dark navy (`#0F172A`) with high-contrast typography.

### 3.2 Sidebar Section 1: Image Upload
- **`📂 Upload Image (JPG, PNG, BMP)...`**: Opens a native OS file picker filtering for supported raster graphic formats:
  - Portable Network Graphics (`*.png`)
  - Joint Photographic Experts Group (`*.jpg`, `*.jpeg`)
  - Windows Bitmap (`*.bmp`)
- **Metadata Card:** Displays real-time file diagnostics upon loading:
  - File name
  - Spatial dimensions (Width $\times$ Height)
  - Color mode (e.g., Color 3-channel BGR)
  - File size formatted in KB or MB

### 3.3 Sidebar Section 2: Preprocessing
- **`⚙️ View Grayscale Preprocessing`**: Displays the 8-bit single-channel luminance representation in the Processed Output panel.
- Validates Functional Requirement **FR-03** without modifying the master in-memory color image.

### 3.4 Sidebar Section 3: Algorithm Selection
- **Algorithm Dropdown (Combobox):** Allows instant switching between:
  1. `Sobel` — First-order directional derivative with central triangular smoothing.
  2. `Prewitt` — First-order directional derivative with uniform box smoothing.
  3. `Laplacian` — Second-order isotropic spatial derivative highlighting rapid transitions.
- **Dynamic Formulation Box:** Automatically updates to display the formal mathematical equation and operational summary for the selected algorithm.

### 3.5 Sidebar Section 4: Actions & Demonstration
- **`⚡ Process Image`**: Executes the selected operator on the active image and renders the normalized 8-bit edge output.
- **`📊 Compare All Algorithms...`**: Opens the dedicated **Multi-Algorithm Comparison Studio**.
- **`💾 Save Output (results/output/)...`**: Saves the active processed edge image using collision-free automatic indexing.
- **`🔄 Reset All`**: Clears all loaded images, resets preview canvases, disables action buttons, and restores the application to a clean initial state.

### 3.6 Dual Preview Panels
- **Left Panel (Original Image):** Displays the unmodified source image centered on a dark canvas (`#0B0F19`). Includes an `Input` badge and image dimension footer.
- **Right Panel (Processed Output):** Displays the edge-detected output with an informative badge (e.g., `Sobel Edge Output`) and channel normalization metadata.
- **Aspect Ratio Safeguard:** Previews use high-order **Lanczos antialiasing** (`Image.Resampling.LANCZOS`) and dynamically compute exact bounding box fits, eliminating stretching or distortion.

### 3.7 Status Bar
- Situated at the bottom edge, providing real-time feedback on user actions, computation completion times, and file save locations.

---

## 4. Multi-Algorithm Comparison Studio

Clicking **`📊 Compare All Algorithms...`** launches a specialized modal comparison studio:

1. **Simultaneous Processing:** Concurrently runs Sobel, Prewitt, and Laplacian operators against the active grayscale representation.
2. **Quantitative Edge Statistics Bar:** Displays a uniform 3-column table comparing:
   - **Mean Gradient Magnitude:** Average pixel intensity across the response.
   - **Detected Edge Pixels:** Total pixel count exceeding the intensity threshold ($T = 30$).
   - **Edge Density Percentage:** Percentage of the image surface classified as edge boundary ($\frac{\text{Edge Pixels}}{\text{Total Pixels}} \times 100\%$).
3. **Four-Panel Visual Matrix:** A $2 \times 2$ grid containing:
   - Top-Left: Original Image (Input)
   - Top-Right: Sobel Operator ($G = \sqrt{G_x^2 + G_y^2}$)
   - Bottom-Left: Prewitt Operator ($G = \sqrt{G_x^2 + G_y^2}$)
   - Bottom-Right: Laplacian Operator ($|\nabla^2 f|$)
4. **Publication-Grade Export:** Clicking **`💾 Save Comparison Visualization...`** exports the 4-panel figure at **300 DPI** directly to `results/visualizations/`.

---

## 5. Output Management & File Naming

The application includes an automated collision-free naming engine:
- Single-operator outputs are saved to:  
  `results/output/<filename>_<operator>_edges.png`
- Comparison visualizations are saved to:  
  `results/visualizations/<filename>_edge_comparison.png`
- **Collision Protection:** If a file with the target name already exists, the system automatically appends an incrementing suffix (`_1.png`, `_2.png`) to prevent accidental overwriting of experimental results.

---

## 6. Step-by-Step Usage Tutorials

### Tutorial 1: Running Sobel Edge Detection
1. Launch the application: `python main.py`.
2. Click **`📂 Upload Image...`** and select `data/input/sample.png`.
3. Verify that the image appears in the left panel and metadata is populated.
4. Ensure `Sobel` is selected in the dropdown.
5. Click **`⚡ Process Image`**.
6. Observe the detected edges in the right preview panel.
7. Click **`💾 Save Output...`** to export the result.

### Tutorial 2: Comparing Sobel vs. Prewitt Without Re-uploading
1. With `sample.png` loaded and Sobel processed, select `Prewitt` from the dropdown.
2. Click **`⚡ Process Image`**.
3. Notice that the image is re-processed immediately in memory without reloading the file.
4. Note the subtle differences: Prewitt exhibits slightly higher sensitivity on thin linear features due to unweighted smoothing.

### Tutorial 3: Multi-Algorithm Demonstration
1. Click **`📊 Compare All Algorithms...`**.
2. Examine the Quantitative Edge Statistics table at the top.
3. Compare the first-derivative single-line boundaries (Sobel, Prewitt) against the second-derivative double-edge zero-crossing contours (Laplacian).
4. Click **`💾 Save Comparison Visualization...`** to export the publication-quality comparison figure.

---

## 7. Troubleshooting & FAQs

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **"Unsupported file format" dialog** | Selected file is not `.jpg`, `.jpeg`, `.png`, or `.bmp`. | Convert image to a supported format before uploading. |
| **"File is empty (0 bytes)" dialog** | Target file is corrupted or 0 bytes. | Verify file integrity on disk. |
| **Preview appears small** | Image has small native resolution. | The preview scales down large images to fit, but does not artificially upscale small images to prevent pixelation blur. |
| **Buttons are grayed out** | No image has been uploaded yet. | Click **`Upload Image`** to enable processing, comparison, and saving buttons. |
| **Windows display scaling clipping** | Display DPI scaling set to 125% or 150%. | The window is optimized at $1180 \times 720$ with built-in mouse wheel scrolling on the sidebar canvas. |
