# Implementation of Edge Detection Techniques Using Sobel, Prewitt and Laplacian Operators

[![Course](https://img.shields.io/badge/Course-Computer%20Vision%20(256PUPC275)-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](#)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-brightgreen.svg)](#)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-orange.svg)](#)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-blue.svg)](#)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7%2B-purple.svg)](#)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(100%25)-brightgreen.svg)](#)

A standalone Python desktop application developed for the **B.Tech Computer Vision (256PUPC275)** curriculum (Option 2, Topic 3: Edge Detection). This application provides a modern graphical suite to load, validate, preprocess, execute, and comparatively analyze spatial edge detection operators: **Sobel**, **Prewitt**, and **Laplacian**.

---

## 📋 Table of Contents

1. [Project Introduction](#-project-introduction)
2. [Problem Statement](#-problem-statement)
3. [Objectives](#-objectives)
4. [Technologies Used](#-technologies-used)
5. [Key Features](#-key-features)
6. [Project Structure](#-project-structure)
7. [Installation Instructions](#-installation-instructions)
8. [How to Run the Application](#-how-to-run-the-application)
9. [How to Use the GUI](#-how-to-use-the-gui)
10. [Algorithm Descriptions & Mathematical Equations](#-algorithm-descriptions--mathematical-equations)
11. [Automated Verification & Testing](#-automated-verification--testing)
12. [Deliverables Checklist](#-deliverables-checklist)

---

## 📖 Project Introduction

Edge detection is an indispensable foundational technique in digital image processing, feature extraction, and computer vision. It isolates object boundaries, spatial discontinuities, and structural geometric contours while filtering out homogeneous regions with redundant information.

This project delivers a **fully standalone desktop GUI application** written in Python using **Tkinter**, **OpenCV**, **NumPy**, **Pillow**, and **Matplotlib**. It eliminates reliance on cloud notebooks (Google Colab or Jupyter Notebook), providing an interactive pair of visualization panels, real-time metadata tracking, a multi-algorithm comparison studio with quantitative edge statistics, and non-destructive image export.

---

## 🎯 Problem Statement

Traditional educational demonstrations of edge detection frequently rely on non-interactive scripts or cloud-hosted Jupyter notebooks. These formats suffer from several limitations:
- Lack of interactive controls for testing arbitrary user images.
- Inability to dynamically toggle and compare different spatial filtering kernels side-by-side.
- Inadequate visual feedback regarding aspect-ratio distortion, color space conversions, and image clipping.
- Absence of real-time analytical metrics comparing the mathematical behavior of first-order gradient operators (Sobel, Prewitt) versus second-order isotropic operators (Laplacian).

This project addresses these challenges by engineering a responsive, decoupled desktop software solution tailored for rigorous academic demonstration.

---

## 📌 Objectives

1. **Standalone Execution:** Develop a modular, production-quality Python desktop application with Tkinter that executes independently of Jupyter or Colab.
2. **Robust Image Ingestion:** Safely load, decode, and validate local image files across **JPG, JPEG, PNG, and BMP** formats, with full support for Windows Unicode file paths and large resolutions.
3. **Immutability of Source Data:** Enforce non-destructive preprocessing by converting color images to single-channel 8-bit grayscale (FR-03) while retaining the original input image unaltered in memory.
4. **Algorithmic Rigor:**
   - Implement the **Sobel operator** using directional $3 \times 3$ smoothing and gradient masks.
   - Implement the **Prewitt operator** using uniform spatial differencing convolution kernels via OpenCV `cv2.filter2D`.
   - Implement the **Laplacian operator** using 2nd spatial derivatives and absolute response normalization.
5. **Comparative Analysis:** Provide a multi-algorithm comparison studio displaying a $2 \times 2$ grid containing the original image and all three operator outputs, accompanied by quantitative edge statistics.
6. **Output Management:** Enable collision-free export of processed edge outputs to `results/output/` and high-resolution visualizations (300 DPI) to `results/visualizations/`.

---

## 🛠 Technologies Used

| Technology | Role & Functionality |
| :--- | :--- |
| **Python 3.8+** | Core programming language for modular software implementation |
| **Tkinter & `ttk`** | Desktop graphical interface framework, window management, and custom styles |
| **OpenCV (`opencv-python`)** | Image decoding (`cv2.imdecode`), color space transformations, and 2D spatial convolutions |
| **NumPy** | Numerical array operations, Euclidean gradient norms (`np.hypot`), and kernel matrix definitions |
| **Pillow (`PIL`)** | High-fidelity image rendering, aspect-ratio scaling with Lanczos antialiasing for Tkinter |
| **Matplotlib** | Multi-panel figure generation, subplot arrangement, and 300 DPI export |
| **ReportLab** | Programmatic generation of academic PDF project report |
| **Python-PPTX** | Programmatic generation of academic presentation slide deck |

---

## ✨ Key Features

- **Responsive Viewport:** Dual image display cards automatically scale previews using Lanczos interpolation, preventing distortion or stretching regardless of window size.
- **Dynamic Algorithm Switching:** Select algorithms from a dropdown and process immediately without having to re-upload the image.
- **Multi-Algorithm Comparison Studio:** Runs all three operators concurrently and displays a $2 \times 2$ comparative matrix with quantitative analytics:
  - *Mean Gradient Magnitude*
  - *Edge Pixel Count* (intensity $> 30$)
  - *Edge Density Percentage*
- **Non-Destructive File Saving:** Auto-detects existing filenames in `results/output/` and `results/visualizations/` and appends collision-free suffixes (`_1`, `_2`).
- **Comprehensive Error Handling:** Rejects invalid file paths, 0-byte corrupted files, and unsupported extensions with informative user alerts.

---

## 📂 Project Structure

```text
computer-vision-edge-detection/
│
├── requirements.md                     # Official assignment specifications & acceptance criteria
├── requirements.txt                    # Python library dependencies
├── README.md                           # Main project documentation & execution guide
├── main.py                             # Application entry point
├── FINAL_SUBMISSION_CHECKLIST.md       # Final submission verification checklist
│
├── src/                                # Modular source code packages
│   ├── __init__.py                     # Package metadata and version definition
│   ├── gui.py                          # Tkinter GUI, ComparisonWindow, event handlers
│   ├── image_utils.py                  # Image I/O, Unicode handling, aspect ratio, unique naming
│   └── edge_detection.py               # Sobel, Prewitt, Laplacian, statistics, Matplotlib figures
│
├── tests/                              # Automated test suites
│   ├── test_image_pipeline.py          # Testing formats, grayscale, aspect ratio & GUI
│   ├── test_edge_algorithms.py         # Testing Sobel, Prewitt, Laplacian math & switching
│   └── test_academic_demonstration.py  # Comprehensive integration suite (Parts A, B, C, D)
│
├── data/
│   └── input/                          # Test input images (.png, .jpg, .jpeg, .bmp, large-res)
│
├── results/
│   ├── output/                         # Processed edge detection and grayscale exports
│   └── visualizations/                 # High-resolution comparison visualizations (300 DPI)
│
├── docs/                               # Academic documentation deliverables
│   ├── methodology.md                  # Comprehensive mathematical methodology
│   ├── project_report.pdf              # Complete 16-section academic PDF report
│   ├── presentation.pptx               # 10-slide academic PowerPoint presentation
│   └── video_presentation_script.md    # Multi-speaker presentation script with timings
│
└── assets/                             # Actual application screenshots and GUI mockups
    ├── gui_main_window.png             # Screenshot of main desktop application
    └── gui_comparison_window.png       # Screenshot of multi-algorithm comparison studio
```

---

## 🚀 Installation Instructions

### 1. Prerequisites
Ensure you have **Python 3.8 or newer** installed:
```bash
python --version
```

### 2. Install Dependencies
Install all required libraries using `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 🖥 How to Run the Application

Launch the desktop application using the main entry script:

```bash
python main.py
```

Console logging will confirm environment compatibility and launch the graphical interface.

---

## 🖱 How to Use the GUI

```
+-----------------------------------------------------------------------------------------+
|                  Implementation of Edge Detection Techniques                            |
|             Sobel, Prewitt and Laplacian Operators • Computer Vision (256PUPC275)        |
+------------------------------------+----------------------------------------------------+
| 1. Image Upload                    |  [ Original Image (Unmodified) ]  [ Processed Output ]
|    [ Upload Image... ]             |  +----------------------------+  +--------------------+
|    File: sample.png (600x600)      |  |                            |  |                    |
| 2. Preprocessing                   |  |      Input Image           |  |    Edge Output     |
|    [ View Grayscale ]              |  |      (Full Color)          |  |   (Normalized)     |
| 3. Algorithm Selection             |  |                            |  |                    |
|    [ Sobel           ▼ ]           |  +----------------------------+  +--------------------+
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

### Step-by-Step Walkthrough:
1. **Upload an Image:** Click **📂 Upload Image (JPG, PNG, BMP)...** and pick any image from `data/input/` (e.g. `sample.png`).
2. **Inspect Metadata:** View file name, image dimensions, color channels, and file size on the sidebar card.
3. **View Grayscale Preprocessing:** Click **⚙️ View Grayscale Preprocessing** to inspect the 1-channel luminance conversion.
4. **Select an Operator:** Choose **Sobel**, **Prewitt**, or **Laplacian** from the dropdown menu. The info card updates with the operator's mathematical formulation.
5. **Process Image:** Click **⚡ Process Image**. The normalized edge result appears immediately in the right preview panel.
6. **Switch Algorithms Instantly:** Change the dropdown selection to another operator (e.g. from Sobel to Prewitt or Laplacian) and click **⚡ Process Image** again. The application re-processes the image in memory without re-uploading.
7. **Compare All Algorithms:** Click **📊 Compare All Algorithms...** to open the dedicated comparison studio featuring the $2 \times 2$ grid and analytical metrics table.
8. **Save Outputs:**
   - Click **💾 Save Output (results/output/)...** to save the active edge image.
   - Click **💾 Save Comparison Visualization...** in the comparison window to save the 300 DPI Matplotlib figure to `results/visualizations/`.
9. **Reset:** Click **🔄 Reset All** to clear memory and canvases.

---

## 🔬 Algorithm Descriptions & Mathematical Equations

### 1. Sobel Operator
- **Order:** First-order differential gradient operator.
- **Kernels:**
  $$\mathbf{K}_x = \begin{bmatrix} -1 & 0 & +1 \\ -2 & 0 & +2 \\ -1 & 0 & +1 \end{bmatrix}, \quad \mathbf{K}_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ +1 & +2 & +1 \end{bmatrix}$$
- **Gradient Magnitude:**
  $$G(x, y) = \sqrt{G_x(x, y)^2 + G_y(x, y)^2}$$
- **Characteristics:** Incorporates center-weighted triangular smoothing ($[1, 2, 1]^T$) orthogonal to differencing, providing superior noise suppression and circular symmetry.

### 2. Prewitt Operator
- **Order:** First-order differential gradient operator.
- **Kernels:**
  $$\mathbf{K}_x = \begin{bmatrix} -1 & 0 & +1 \\ -1 & 0 & +1 \\ -1 & 0 & +1 \end{bmatrix}, \quad \mathbf{K}_y = \begin{bmatrix} -1 & -1 & -1 \\ 0 & 0 & 0 \\ +1 & +1 & +1 \end{bmatrix}$$
- **Gradient Magnitude:**
  $$G(x, y) = \sqrt{G_x(x, y)^2 + G_y(x, y)^2}$$
- **Characteristics:** Utilizes uniform spatial weighting ($[1, 1, 1]^T$), making it computationally simpler than Sobel but slightly more vulnerable to high-frequency noise.

### 3. Laplacian Operator
- **Order:** Second-order isotropic differential operator.
- **Formulation:**
  $$\nabla^2 f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2} \implies \mathbf{K} = \begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix}$$
- **Visualization:** Normalization of the absolute second derivative response:
  $$L_{\text{vis}}(x, y) = \text{clip}\left(\frac{|\nabla^2 f(x, y)| - \min(|\nabla^2 f|)}{\max(|\nabla^2 f|) - \min(|\nabla^2 f|) + \epsilon} \times 255, 0, 255\right)$$
- **Characteristics:** Rotation-invariant (isotropic); pinpoints edges at zero-crossings; highlights fine texture and sharp boundaries.

---

## 🧪 Automated Verification & Testing

Three automated test suites are provided to ensure complete reproducibility:

```bash
# 1. Full Academic Demonstration Suite (Covers Parts A, B, C, D)
python tests/test_academic_demonstration.py

# 2. Image Pipeline & Format Validation Suite
python tests/test_image_pipeline.py

# 3. Mathematical Edge Detection Operators & Dynamic Switching Suite
python tests/test_edge_algorithms.py
```

All tests execute headlessly and achieve a **100% pass rate**.

---

## 📋 Deliverables Checklist

- [x] Standalone Desktop GUI Application (`main.py`, `src/gui.py`)
- [x] Modular Image Processing Utilities (`src/image_utils.py`)
- [x] Mathematical Edge Detection Engine (`src/edge_detection.py`)
- [x] Multi-Algorithm Comparison Studio with 300 DPI Export
- [x] Comprehensive Mathematical Methodology (`docs/methodology.md`)
- [x] Full Academic Project Report (`docs/project_report.pdf`)
- [x] Presentation Slide Deck (`docs/presentation.pptx`)
- [x] Video Presentation Script (`docs/video_presentation_script.md`)
- [x] Automated Test Suites with 100% Passing Coverage (`tests/`)
- [x] Final Submission Checklist (`FINAL_SUBMISSION_CHECKLIST.md`)
