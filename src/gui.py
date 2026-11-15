"""
GUI Module for Edge Detection Application
Provides a professional, modern Tkinter desktop interface with algorithm dropdown,
dual-panel preview, dynamic multi-algorithm comparison window, and robust output management.

Course: Computer Vision (256PUPC275)
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any
import numpy as np
from PIL import Image, ImageTk

# Matplotlib integration for Tkinter comparison view
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.image_utils import (
    load_image,
    validate_image_path,
    convert_to_grayscale,
    save_image,
    cv_to_pil,
    resize_image_aspect_ratio,
    get_image_metadata,
    get_unique_filepath,
    SUPPORTED_EXTENSIONS
)
from src.edge_detection import (
    OperatorType,
    OPERATOR_DETAILS,
    process_image,
    run_all_operators,
    compute_edge_statistics,
    create_comparison_figure,
    save_comparison_figure
)


class ComparisonWindow(tk.Toplevel):
    """
    Dedicated Multi-Algorithm Comparison Window (Part B).
    Displays the original image alongside Sobel, Prewitt, and Laplacian results
    with analytical metrics and high-resolution export capability.
    """

    def __init__(
        self,
        parent: tk.Tk,
        results: Dict[str, np.ndarray],
        image_name: str,
        app_ref: "EdgeDetectionApp"
    ):
        super().__init__(parent)
        self.results = results
        self.image_name = image_name
        self.app_ref = app_ref

        self.title("Multi-Algorithm Comparison Studio | Sobel, Prewitt & Laplacian")
        self.geometry("1100x820")
        self.minsize(960, 720)
        self.configure(bg="#F8FAFC")

        # Create Matplotlib Figure
        self.fig = create_comparison_figure(self.results, image_title=self.image_name)

        self._build_header()
        self._build_toolbar()
        self._build_analytics_bar()
        self._build_canvas()

        # Center on parent window
        self.transient(parent)
        self.focus_set()

    def _build_header(self):
        """Constructs top header bar of the comparison studio."""
        header = tk.Frame(self, bg="#0F172A", height=54)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        inner = tk.Frame(header, bg="#0F172A")
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        title_lbl = tk.Label(
            inner,
            text="Edge Detection Multi-Algorithm Comparison Studio",
            font=("Segoe UI", 12, "bold"),
            fg="#FFFFFF",
            bg="#0F172A"
        )
        title_lbl.pack(side=tk.LEFT)

    def _build_toolbar(self):
        """Builds action toolbar with export button."""
        toolbar = tk.Frame(self, bg="#FFFFFF", height=46, bd=1, relief="solid")
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=14, pady=(10, 6))
        toolbar.pack_propagate(False)

        inner = tk.Frame(toolbar, bg="#FFFFFF")
        inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        info_lbl = tk.Label(
            inner,
            text="Side-by-side comparison of 1st and 2nd derivative spatial filters against the original image.",
            font=("Segoe UI", 9),
            fg="#475569",
            bg="#FFFFFF"
        )
        info_lbl.pack(side=tk.LEFT)

        btn_save_vis = ttk.Button(
            inner,
            text="💾  Save Comparison Visualization (results/visualizations/)...",
            style="Success.TButton",
            command=self.on_save_visualization
        )
        btn_save_vis.pack(side=tk.RIGHT, padx=4)

        btn_close = ttk.Button(
            inner,
            text="Close",
            style="Secondary.TButton",
            command=self.destroy
        )
        btn_close.pack(side=tk.RIGHT, padx=4)

    def _build_analytics_bar(self):
        """Constructs a quantitative analytics table comparing all three operators."""
        stats = compute_edge_statistics(self.results, threshold=30)
        card = tk.Frame(self, bg="#FFFFFF", bd=1, relief="solid")
        card.pack(side=tk.TOP, fill=tk.X, padx=14, pady=4)

        header_frame = tk.Frame(card, bg="#FFFFFF")
        header_frame.pack(fill=tk.X, padx=12, pady=(6, 2))

        tk.Label(
            header_frame,
            text="Quantitative Edge Statistics (Intensity Threshold = 30)",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A"
        ).pack(side=tk.LEFT)

        cols_frame = tk.Frame(card, bg="#FFFFFF")
        cols_frame.pack(fill=tk.X, padx=8, pady=(2, 6))
        cols_frame.columnconfigure(0, weight=1, uniform="stat_col")
        cols_frame.columnconfigure(1, weight=1, uniform="stat_col")
        cols_frame.columnconfigure(2, weight=1, uniform="stat_col")

        items = [
            ("Sobel (1st Deriv.)", stats.get("sobel", {})),
            ("Prewitt (1st Deriv.)", stats.get("prewitt", {})),
            ("Laplacian (2nd Deriv.)", stats.get("laplacian", {}))
        ]

        for idx, (op_name, data) in enumerate(items):
            box = tk.Frame(cols_frame, bg="#F8FAFC", bd=1, relief="solid")
            box.grid(row=0, column=idx, sticky="nsew", padx=4, pady=2)

            tk.Label(
                box,
                text=op_name,
                font=("Segoe UI", 8, "bold"),
                bg="#F8FAFC",
                fg="#1E3A8A"
            ).pack(anchor="w", padx=8, pady=(3, 1))

            txt = f"Mean: {data.get('mean_intensity', 0):.1f}   •   Edges: {data.get('edge_pixel_count', 0):,} ({data.get('edge_density_pct', 0)}%)"
            tk.Label(
                box,
                text=txt,
                font=("Segoe UI", 8),
                bg="#F8FAFC",
                fg="#334155"
            ).pack(anchor="w", padx=8, pady=(1, 3))

    def _build_canvas(self):
        """Embeds Matplotlib Figure inside Tkinter canvas."""
        canvas_frame = tk.Frame(self, bg="#0F172A", bd=1, relief="solid")
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=14, pady=(6, 12))

        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_save_visualization(self):
        """Saves the comparison visualization into results/visualizations/ with collision handling."""
        vis_dir = os.path.abspath("results/visualizations")
        os.makedirs(vis_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(self.image_name or "comparison"))[0]
        default_unique_path = get_unique_filepath(vis_dir, f"{base_name}_edge_comparison", ".png")
        suggested_name = os.path.basename(default_unique_path)

        save_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Multi-Algorithm Comparison Visualization",
            initialdir=vis_dir,
            initialfile=suggested_name,
            defaultextension=".png",
            filetypes=[
                ("PNG High-Res Image (*.png)", "*.png"),
                ("JPEG Image (*.jpg)", "*.jpg *.jpeg"),
                ("PDF Vector Document (*.pdf)", "*.pdf"),
                ("All files (*.*)", "*.*")
            ]
        )

        if not save_path:
            return

        success = save_comparison_figure(self.fig, save_path, dpi=300)
        if success:
            messagebox.showinfo(
                "Visualization Saved",
                f"Comparison visualization successfully saved to:\n{save_path}\n\nHigh-resolution 300 DPI output ready for academic reports.",
                parent=self
            )
            self.app_ref.set_status(f"Comparison visualization saved: {os.path.basename(save_path)}")
        else:
            messagebox.showerror(
                "Export Error",
                f"Failed to save visualization to:\n{save_path}",
                parent=self
            )


class EdgeDetectionApp:
    """
    Main Desktop GUI Application for Computer Vision Edge Detection.
    """

    # Color Palette - Modern Professional Aesthetic
    COLOR_BG = "#F8FAFC"             # Slate 50
    COLOR_CARD = "#FFFFFF"           # Pure White
    COLOR_HEADER = "#0F172A"         # Slate 900
    COLOR_HEADER_TEXT = "#FFFFFF"    # White
    COLOR_ACCENT = "#2563EB"         # Royal Blue 600
    COLOR_ACCENT_HOVER = "#1D4ED8"   # Blue 700
    COLOR_PREPROCESS = "#0284C7"     # Sky Blue 600
    COLOR_SUCCESS = "#059669"        # Emerald 600
    COLOR_COMPARE = "#7C3AED"        # Violet 600 (Academic highlight)
    COLOR_TEXT_PRIMARY = "#0F172A"   # Slate 900
    COLOR_TEXT_SECONDARY = "#475569" # Slate 600
    COLOR_BORDER = "#CBD5E1"         # Slate 300
    COLOR_PREVIEW_BG = "#0B0F19"     # Deep canvas background

    ALGORITHM_OPTIONS = [
        OperatorType.SOBEL.value,
        OperatorType.PREWITT.value,
        OperatorType.LAPLACIAN.value
    ]

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Edge Detection Studio | Sobel, Prewitt & Laplacian Operators")
        self.root.geometry("1180x720")
        self.root.minsize(1000, 620)
        self.root.configure(bg=self.COLOR_BG)

        # Image State Management (preserving original unmodified)
        self.current_file_path: Optional[str] = None
        self.original_cv_image: Optional[np.ndarray] = None    # Master original BGR copy
        self.grayscale_cv_image: Optional[np.ndarray] = None   # Grayscale 8-bit copy
        self.processed_cv_image: Optional[np.ndarray] = None   # Current processed output

        self.original_pil_image: Optional[Image.Image] = None
        self.processed_pil_image: Optional[Image.Image] = None

        # Display caches for Tkinter PhotoImage references
        self._tk_orig_img: Optional[ImageTk.PhotoImage] = None
        self._tk_proc_img: Optional[ImageTk.PhotoImage] = None

        # Debounce timer for smooth preview resizing
        self._resize_timer = None

        # Algorithm selection variable for Combobox dropdown
        self.selected_operator = tk.StringVar(value=OperatorType.SOBEL.value)

        # Configure styles and build interface
        self._configure_styles()
        self._build_header()
        self._build_main_content()
        self._build_status_bar()

        # Update initial operator documentation card
        self._update_operator_info()
        self.set_status("Ready. Click 'Upload Image' to load an image (JPG, PNG, BMP).")

    def _configure_styles(self):
        """Configure ttk styles for clean, modern desktop aesthetic."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Global Frame backgrounds
        style.configure("TFrame", background=self.COLOR_BG)
        style.configure("Card.TFrame", background=self.COLOR_CARD, relief="flat")

        # Label styles
        style.configure("TLabel", background=self.COLOR_BG, foreground=self.COLOR_TEXT_PRIMARY, font=("Segoe UI", 9))
        style.configure("Card.TLabel", background=self.COLOR_CARD, foreground=self.COLOR_TEXT_PRIMARY, font=("Segoe UI", 9))

        # Combobox style
        style.configure("TCombobox", font=("Segoe UI", 10))

        # Custom Buttons with optimized compact padding
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_ACCENT,
            foreground="#FFFFFF",
            padding=(10, 5)
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.COLOR_ACCENT_HOVER), ("disabled", "#94A3B8")],
            foreground=[("disabled", "#F1F5F9")]
        )

        style.configure(
            "Compare.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_COMPARE,
            foreground="#FFFFFF",
            padding=(10, 5)
        )
        style.map(
            "Compare.TButton",
            background=[("active", "#6D28D9"), ("disabled", "#94A3B8")],
            foreground=[("disabled", "#F1F5F9")]
        )

        style.configure(
            "Preprocess.TButton",
            font=("Segoe UI", 9),
            background=self.COLOR_PREPROCESS,
            foreground="#FFFFFF",
            padding=(8, 4)
        )
        style.map(
            "Preprocess.TButton",
            background=[("active", "#0369A1"), ("disabled", "#94A3B8")],
            foreground=[("disabled", "#F1F5F9")]
        )

        style.configure(
            "Success.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_SUCCESS,
            foreground="#FFFFFF",
            padding=(10, 5)
        )
        style.map(
            "Success.TButton",
            background=[("active", "#047857"), ("disabled", "#94A3B8")],
            foreground=[("disabled", "#F1F5F9")]
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 9),
            background="#E2E8F0",
            foreground=self.COLOR_TEXT_PRIMARY,
            padding=(8, 4)
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#CBD5E1")]
        )

    def _build_header(self):
        """Constructs the application top banner."""
        header_frame = tk.Frame(self.root, bg=self.COLOR_HEADER, height=56)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)

        inner = tk.Frame(header_frame, bg=self.COLOR_HEADER)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        # Title & Subtitle container
        text_container = tk.Frame(inner, bg=self.COLOR_HEADER)
        text_container.pack(side=tk.LEFT, fill=tk.Y)

        title_lbl = tk.Label(
            text_container,
            text="Implementation of Edge Detection Techniques",
            font=("Segoe UI", 13, "bold"),
            fg=self.COLOR_HEADER_TEXT,
            bg=self.COLOR_HEADER
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            text_container,
            text="Sobel, Prewitt and Laplacian Operators  •  Computer Vision (256PUPC275)",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg=self.COLOR_HEADER
        )
        subtitle_lbl.pack(anchor="w")

    def _build_main_content(self):
        """Constructs the two-column responsive interface."""
        main_container = tk.Frame(self.root, bg=self.COLOR_BG)
        main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=14, pady=8)

        # Left Control Sidebar
        sidebar = tk.Frame(main_container, bg=self.COLOR_CARD, width=340, bd=1, relief="solid")
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)

        self._build_sidebar_content(sidebar)

        # Right Preview Area
        preview_container = tk.Frame(main_container, bg=self.COLOR_BG)
        preview_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_preview_panels(preview_container)

    def _build_sidebar_content(self, parent: tk.Frame):
        """Populates the left control sidebar with compact, responsive layout."""
        canvas = tk.Canvas(parent, bg=self.COLOR_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg=self.COLOR_CARD)

        scroll_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=320)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Smooth mouse wheel support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scroll_content.bind("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        pad_x = 12
        pad_y = 6

        # --- SECTION 1: IMAGE LOADING ---
        lbl_sec1 = tk.Label(
            scroll_content,
            text="1. Image Upload",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_PRIMARY
        )
        lbl_sec1.pack(anchor="w", padx=pad_x, pady=(pad_y, 2))

        self.btn_upload = ttk.Button(
            scroll_content,
            text="📂  Upload Image (JPG, PNG, BMP)...",
            style="Primary.TButton",
            command=self.on_upload_image
        )
        self.btn_upload.pack(fill=tk.X, padx=pad_x, pady=2)

        # Metadata Card (compact)
        meta_frame = tk.Frame(scroll_content, bg="#F8FAFC", bd=1, relief="solid")
        meta_frame.pack(fill=tk.X, padx=pad_x, pady=3)

        self.lbl_meta_name = tk.Label(meta_frame, text="File: No image selected", font=("Segoe UI", 8), bg="#F8FAFC", fg=self.COLOR_TEXT_SECONDARY, anchor="w")
        self.lbl_meta_name.pack(fill=tk.X, padx=8, pady=(3, 1))

        self.lbl_meta_dim = tk.Label(meta_frame, text="Dimensions: --", font=("Segoe UI", 8), bg="#F8FAFC", fg=self.COLOR_TEXT_SECONDARY, anchor="w")
        self.lbl_meta_dim.pack(fill=tk.X, padx=8, pady=1)

        self.lbl_meta_channels = tk.Label(meta_frame, text="Color Mode: --", font=("Segoe UI", 8), bg="#F8FAFC", fg=self.COLOR_TEXT_SECONDARY, anchor="w")
        self.lbl_meta_channels.pack(fill=tk.X, padx=8, pady=1)

        self.lbl_meta_size = tk.Label(meta_frame, text="File Size: --", font=("Segoe UI", 8), bg="#F8FAFC", fg=self.COLOR_TEXT_SECONDARY, anchor="w")
        self.lbl_meta_size.pack(fill=tk.X, padx=8, pady=(1, 3))

        # --- SECTION 2: PREPROCESSING ---
        ttk.Separator(scroll_content, orient="horizontal").pack(fill=tk.X, padx=pad_x, pady=5)

        lbl_sec2 = tk.Label(
            scroll_content,
            text="2. Preprocessing",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_PRIMARY
        )
        lbl_sec2.pack(anchor="w", padx=pad_x, pady=(2, 2))

        self.btn_convert_gray = ttk.Button(
            scroll_content,
            text="⚙️  View Grayscale Preprocessing",
            style="Preprocess.TButton",
            command=self.on_convert_to_grayscale,
            state="disabled"
        )
        self.btn_convert_gray.pack(fill=tk.X, padx=pad_x, pady=2)

        # --- SECTION 3: ALGORITHM SELECTION (DROPDOWN) ---
        ttk.Separator(scroll_content, orient="horizontal").pack(fill=tk.X, padx=pad_x, pady=5)

        lbl_sec3 = tk.Label(
            scroll_content,
            text="3. Algorithm Selection",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_PRIMARY
        )
        lbl_sec3.pack(anchor="w", padx=pad_x, pady=(2, 2))

        lbl_choose = tk.Label(
            scroll_content,
            text="Select Algorithm:",
            font=("Segoe UI", 8),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_SECONDARY
        )
        lbl_choose.pack(anchor="w", padx=pad_x, pady=(0, 1))

        # Dropdown selection (Combobox)
        self.combo_algorithm = ttk.Combobox(
            scroll_content,
            textvariable=self.selected_operator,
            values=self.ALGORITHM_OPTIONS,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.combo_algorithm.pack(fill=tk.X, padx=pad_x, pady=2)
        self.combo_algorithm.bind("<<ComboboxSelected>>", self._on_combobox_selected)

        # Dynamic Algorithm Info Box (compact)
        self.info_box = tk.Frame(scroll_content, bg="#F1F5F9", bd=1, relief="solid")
        self.info_box.pack(fill=tk.X, padx=pad_x, pady=4)

        self.lbl_op_title = tk.Label(self.info_box, text="", font=("Segoe UI", 8, "bold"), bg="#F1F5F9", fg=self.COLOR_TEXT_PRIMARY, anchor="w")
        self.lbl_op_title.pack(fill=tk.X, padx=6, pady=(4, 1))

        self.lbl_op_formula = tk.Label(self.info_box, text="", font=("Consolas", 8, "italic"), bg="#F1F5F9", fg="#2563EB", anchor="w")
        self.lbl_op_formula.pack(fill=tk.X, padx=6, pady=1)

        self.lbl_op_desc = tk.Label(self.info_box, text="", font=("Segoe UI", 8), bg="#F1F5F9", fg=self.COLOR_TEXT_SECONDARY, justify=tk.LEFT, wraplength=275, anchor="w")
        self.lbl_op_desc.pack(fill=tk.X, padx=6, pady=(1, 4))

        # --- SECTION 4: ACTIONS, COMPARISON & EXPORT ---
        ttk.Separator(scroll_content, orient="horizontal").pack(fill=tk.X, padx=pad_x, pady=5)

        lbl_sec4 = tk.Label(
            scroll_content,
            text="4. Actions & Demonstration",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_PRIMARY
        )
        lbl_sec4.pack(anchor="w", padx=pad_x, pady=(2, 2))

        self.btn_process = ttk.Button(
            scroll_content,
            text="⚡  Process Image",
            style="Primary.TButton",
            command=self.on_process_image,
            state="disabled"
        )
        self.btn_process.pack(fill=tk.X, padx=pad_x, pady=2)

        # Compare All Algorithms Button (Part B)
        self.btn_compare = ttk.Button(
            scroll_content,
            text="📊  Compare All Algorithms...",
            style="Compare.TButton",
            command=self.on_compare_all,
            state="disabled"
        )
        self.btn_compare.pack(fill=tk.X, padx=pad_x, pady=2)

        # Save Output Button (Part C)
        self.btn_save = ttk.Button(
            scroll_content,
            text="💾  Save Output (results/output/)...",
            style="Success.TButton",
            command=self.on_save_output,
            state="disabled"
        )
        self.btn_save.pack(fill=tk.X, padx=pad_x, pady=2)

        self.btn_reset = ttk.Button(
            scroll_content,
            text="🔄  Reset All",
            style="Secondary.TButton",
            command=self.on_reset
        )
        self.btn_reset.pack(fill=tk.X, padx=pad_x, pady=(2, 6))

    def _build_preview_panels(self, parent: tk.Frame):
        """Constructs side-by-side original and processed preview panels."""
        parent.columnconfigure(0, weight=1, uniform="preview_col")
        parent.columnconfigure(1, weight=1, uniform="preview_col")
        parent.rowconfigure(0, weight=1)

        # Panel 1: Original Image
        card_orig = tk.Frame(parent, bg=self.COLOR_CARD, bd=1, relief="solid")
        card_orig.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=0)
        self._setup_preview_card(card_orig, is_processed=False)

        # Panel 2: Processed Output Image
        card_proc = tk.Frame(parent, bg=self.COLOR_CARD, bd=1, relief="solid")
        card_proc.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=0)
        self._setup_preview_card(card_proc, is_processed=True)

        # Bind resize event to dynamically rescale preview images without distortion
        parent.bind("<Configure>", self._on_preview_area_resize)

    def _setup_preview_card(self, card: tk.Frame, is_processed: bool):
        """Configures a single preview panel card."""
        header = tk.Frame(card, bg="#F1F5F9", height=38)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        title_text = "Processed Output" if is_processed else "Original Image (Unmodified)"
        badge_text = "Output" if is_processed else "Input"
        badge_color = "#D1FAE5" if is_processed else "#DBEAFE"
        badge_fg = "#065F46" if is_processed else "#1E40AF"

        lbl_title = tk.Label(header, text=title_text, font=("Segoe UI", 9, "bold"), bg="#F1F5F9", fg=self.COLOR_TEXT_PRIMARY)
        lbl_title.pack(side=tk.LEFT, padx=12, pady=8)

        if is_processed:
            self.lbl_proc_badge = tk.Label(header, text=badge_text, font=("Segoe UI", 8, "bold"), bg=badge_color, fg=badge_fg, padx=6, pady=2)
            self.lbl_proc_badge.pack(side=tk.RIGHT, padx=12, pady=6)
        else:
            lbl_badge = tk.Label(header, text=badge_text, font=("Segoe UI", 8, "bold"), bg=badge_color, fg=badge_fg, padx=6, pady=2)
            lbl_badge.pack(side=tk.RIGHT, padx=12, pady=6)

        # Image display container
        display_frame = tk.Frame(card, bg=self.COLOR_PREVIEW_BG)
        display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=8)

        canvas = tk.Label(
            display_frame,
            text="No image loaded.\nClick 'Upload Image' to begin." if not is_processed else "Select an algorithm and click 'Process Image',\nor click 'Compare All Algorithms'.",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg=self.COLOR_PREVIEW_BG,
            justify=tk.CENTER
        )
        canvas.pack(fill=tk.BOTH, expand=True)

        # Sub-status bar of the card
        footer = tk.Frame(card, bg=self.COLOR_CARD, height=26)
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        lbl_info = tk.Label(footer, text="Dimensions: --", font=("Segoe UI", 8), fg=self.COLOR_TEXT_SECONDARY, bg=self.COLOR_CARD)
        lbl_info.pack(side=tk.LEFT, padx=10, pady=2)

        if is_processed:
            self.canvas_proc = canvas
            self.lbl_proc_info = lbl_info
            self.frame_proc_display = display_frame
        else:
            self.canvas_orig = canvas
            self.lbl_orig_info = lbl_info
            self.frame_orig_display = display_frame

    def _build_status_bar(self):
        """Builds bottom status and metadata bar."""
        status_bar = tk.Frame(self.root, bg="#E2E8F0", height=26)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        status_bar.pack_propagate(False)

        self.lbl_status = tk.Label(
            status_bar,
            text="Ready",
            font=("Segoe UI", 8),
            bg="#E2E8F0",
            fg=self.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        self.lbl_status.pack(side=tk.LEFT, padx=12, pady=2)

        lbl_course = tk.Label(
            status_bar,
            text="Course: 256PUPC275 | Topic 3: Edge Detection",
            font=("Segoe UI", 8),
            bg="#E2E8F0",
            fg=self.COLOR_TEXT_SECONDARY,
            anchor="e"
        )
        lbl_course.pack(side=tk.RIGHT, padx=12, pady=2)

    def set_status(self, message: str):
        """Updates the status bar text."""
        self.lbl_status.config(text=message)

    def _on_combobox_selected(self, event=None):
        """Handles algorithm selection change from the Combobox dropdown."""
        self._update_operator_info()
        selected_algo = self.selected_operator.get()
        if self.original_cv_image is not None:
            self.set_status(f"Selected: {selected_algo}. Click 'Process Image' to execute.")

    def _update_operator_info(self):
        """Updates dynamic explanation box when algorithm selection changes."""
        selected_val = self.selected_operator.get()
        info = OPERATOR_DETAILS.get(selected_val, {})
        if info:
            self.lbl_op_title.config(text=info.get("title", selected_val))
            self.lbl_op_formula.config(text=f"Formula: {info.get('formula', '')}")
            self.lbl_op_desc.config(text=info.get("description", ""))
        else:
            self.lbl_op_title.config(text=selected_val)
            self.lbl_op_formula.config(text="")
            self.lbl_op_desc.config(text="")

    def on_upload_image(self):
        """
        Handles image selection via Tkinter file dialog, performs validation,
        loads image using OpenCV, and displays it in original preview.
        """
        initial_dir = os.path.abspath("data/input")
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()

        file_types = [
            ("Supported Images (*.jpg, *.jpeg, *.png, *.bmp)", "*.jpg;*.jpeg;*.png;*.bmp"),
            ("JPEG Image (*.jpg, *.jpeg)", "*.jpg;*.jpeg"),
            ("PNG Image (*.png)", "*.png"),
            ("Bitmap Image (*.bmp)", "*.bmp"),
            ("All Files (*.*)", "*.*")
        ]

        file_path = filedialog.askopenfilename(
            title="Select Input Image (JPG, JPEG, PNG, BMP)",
            initialdir=initial_dir,
            filetypes=file_types
        )

        if not file_path:
            return

        # 1. Path & File format validation
        is_valid, validation_msg = validate_image_path(file_path)
        if not is_valid:
            messagebox.showerror("Invalid Image File", f"Validation Failed:\n{validation_msg}")
            self.set_status(f"Error: {validation_msg}")
            return

        # 2. Load image via OpenCV
        self.set_status(f"Loading '{os.path.basename(file_path)}'...")
        self.root.update_idletasks()

        loaded_img = load_image(file_path)
        if loaded_img is None:
            messagebox.showerror(
                "Loading Error",
                f"Failed to decode image from:\n{file_path}\n\nThe file may be corrupted or not a valid image."
            )
            self.set_status(f"Error: Could not decode {os.path.basename(file_path)}")
            return

        # 3. Store master immutable original copy
        self.current_file_path = file_path
        self.original_cv_image = loaded_img.copy()   # Strictly preserve original unmodified
        self.original_pil_image = cv_to_pil(self.original_cv_image)

        # Clear previous processed states
        self.grayscale_cv_image = None
        self.processed_cv_image = None
        self.processed_pil_image = None

        # 4. Extract metadata and update sidebar
        meta = get_image_metadata(file_path, self.original_cv_image)
        self.lbl_meta_name.config(text=f"File: {meta['filename']} ({meta['format']})")
        self.lbl_meta_dim.config(text=f"Dimensions: {meta['dimensions']}")
        self.lbl_meta_channels.config(text=f"Color Mode: {meta['color_mode']}")
        self.lbl_meta_size.config(text=f"File Size: {meta['filesize']}")
        self.lbl_orig_info.config(text=f"Dimensions: {meta['dimensions']} | {meta['color_mode']}")

        # 5. Enable control buttons
        self.btn_convert_gray.config(state="normal")
        self.btn_process.config(state="normal")
        self.btn_compare.config(state="normal")
        self.btn_save.config(state="disabled")

        # 6. Reset right preview card
        self.canvas_proc.config(image="", text="Select an algorithm above and click 'Process Image',\nor click 'Compare All Algorithms'.")
        self.lbl_proc_info.config(text="Dimensions: --")
        self.lbl_proc_badge.config(text="Output", bg="#D1FAE5", fg="#065F46")

        # 7. Render original preview with aspect ratio preserved
        self._refresh_original_preview()

        # Precompute grayscale in background for instantaneous execution
        self.grayscale_cv_image = convert_to_grayscale(self.original_cv_image)

        self.set_status(f"Loaded '{meta['filename']}' ({meta['dimensions']}, {meta['color_mode']}). Ready to process or compare.")

    def on_convert_to_grayscale(self, silent: bool = False):
        """
        Displays the single-channel grayscale preprocessed image in the output panel.
        """
        if self.original_cv_image is None:
            if not silent:
                messagebox.showwarning("No Image", "Please upload an image first.")
            return

        try:
            gray_img = convert_to_grayscale(self.original_cv_image)
            self.grayscale_cv_image = gray_img
            self.processed_cv_image = gray_img
            self.processed_pil_image = cv_to_pil(gray_img)

            # Update right panel badge & metadata
            self.lbl_proc_badge.config(text="Grayscale (1-ch)", bg="#E0E7FF", fg="#3730A3")
            h, w = gray_img.shape[:2]
            self.lbl_proc_info.config(text=f"Dimensions: {w} × {h} | Single Channel (uint8)")

            # Enable saving
            self.btn_save.config(state="normal")

            # Render in right preview panel
            self._refresh_processed_preview()
            self.set_status(f"Displaying Grayscale image ({w} × {h}, 1-ch uint8). Original image preserved.")
        except Exception as e:
            messagebox.showerror("Grayscale Error", f"Failed to convert image:\n{e}")
            self.set_status(f"Grayscale error: {e}")

    def on_process_image(self):
        """
        Executes the selected edge detection algorithm (Sobel, Prewitt, or Laplacian)
        on the input image and renders the result in the output preview panel.
        Users can switch algorithms and re-process without re-uploading the image.
        """
        if self.original_cv_image is None:
            messagebox.showwarning("No Image", "Please upload an image first.")
            return

        selected_algo = self.selected_operator.get()
        self.set_status(f"Executing {selected_algo} edge detection algorithm...")
        self.root.update_idletasks()

        try:
            # Process using separate modular function in src/edge_detection.py
            output_img = process_image(self.original_cv_image, selected_algo)

            self.processed_cv_image = output_img
            self.processed_pil_image = cv_to_pil(output_img)

            # Update processed card header badge
            self.lbl_proc_badge.config(
                text=f"{selected_algo} Edge Output",
                bg="#FEF3C7",
                fg="#92400E"
            )
            h, w = output_img.shape[:2]
            channels = 1 if len(output_img.shape) == 2 else output_img.shape[2]
            self.lbl_proc_info.config(text=f"Dimensions: {w} × {h} | {channels} channel ({output_img.dtype})")

            # Enable save button
            self.btn_save.config(state="normal")

            # Render processed preview with aspect ratio preserved
            self._refresh_processed_preview()

            self.set_status(f"{selected_algo} operator completed successfully. Output normalized to [0, 255].")
        except Exception as e:
            messagebox.showerror("Processing Error", f"An error occurred while executing {selected_algo}:\n{e}")
            self.set_status(f"Processing error: {e}")

    def on_compare_all(self):
        """
        Executes Sobel, Prewitt, and Laplacian operators simultaneously on the input image
        and launches the dedicated Multi-Algorithm Comparison Window (Part B).
        """
        if self.original_cv_image is None:
            messagebox.showwarning("No Image", "Please upload an image first.")
            return

        self.set_status("Running multi-algorithm comparative analysis (Sobel, Prewitt, Laplacian)...")
        self.root.update_idletasks()

        try:
            results = run_all_operators(self.original_cv_image)
            image_name = os.path.basename(self.current_file_path or "Target Image")

            # Open dedicated comparison studio window
            ComparisonWindow(self.root, results, image_name, self)
            self.set_status(f"Multi-algorithm comparison displayed for '{image_name}'.")
        except Exception as e:
            messagebox.showerror("Comparison Error", f"Failed to execute multi-algorithm comparison:\n{e}")
            self.set_status(f"Comparison error: {e}")

    def on_save_output(self):
        """
        Saves the processed output image (Sobel, Prewitt, Laplacian, or Grayscale)
        to results/output/ with automatic non-destructive naming to prevent accidental overwriting (Part C).
        """
        if self.processed_cv_image is None:
            messagebox.showwarning("No Output", "There is no processed output to save.")
            return

        output_dir = os.path.abspath("results/output")
        os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(self.current_file_path or "image"))[0]
        badge_text = self.lbl_proc_badge.cget("text")
        algo_slug = badge_text.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")

        # Part C: Automatic non-colliding default filepath
        default_unique_path = get_unique_filepath(output_dir, f"{base_name}_{algo_slug}", ".png")
        suggested_filename = os.path.basename(default_unique_path)

        save_path = filedialog.asksaveasfilename(
            title=f"Save Output Image ({badge_text})",
            initialdir=output_dir,
            initialfile=suggested_filename,
            defaultextension=".png",
            filetypes=[
                ("PNG image (*.png)", "*.png"),
                ("JPEG image (*.jpg)", "*.jpg *.jpeg"),
                ("BMP image (*.bmp)", "*.bmp"),
                ("All files (*.*)", "*.*")
            ]
        )

        if not save_path:
            return

        success, actual_saved_path = save_image(save_path, self.processed_cv_image, overwrite=True)
        if success:
            messagebox.showinfo(
                "Output Saved",
                f"Image successfully saved to:\n{actual_saved_path}\n\nStored in results/output/."
            )
            self.set_status(f"Saved: {os.path.basename(actual_saved_path)}")
        else:
            messagebox.showerror("Save Error", f"Failed to save image to:\n{save_path}")
            self.set_status("Failed to save image.")

    def on_reset(self):
        """
        Resets the application to initial state:
        Clears all images, previews, metadata labels, and resets buttons and status.
        """
        self.current_file_path = None
        self.original_cv_image = None
        self.grayscale_cv_image = None
        self.processed_cv_image = None
        self.original_pil_image = None
        self.processed_pil_image = None
        self._tk_orig_img = None
        self._tk_proc_img = None

        # Reset UI metadata labels
        self.lbl_meta_name.config(text="File: No image selected")
        self.lbl_meta_dim.config(text="Dimensions: --")
        self.lbl_meta_channels.config(text="Color Mode: --")
        self.lbl_meta_size.config(text="File Size: --")

        # Reset previews
        self.canvas_orig.config(image="", text="No image loaded.\nClick 'Upload Image' to begin.")
        self.canvas_proc.config(image="", text="Select an algorithm and click 'Process Image',\nor click 'Compare All Algorithms'.")
        self.lbl_orig_info.config(text="Dimensions: --")
        self.lbl_proc_info.config(text="Dimensions: --")
        self.lbl_proc_badge.config(text="Output", bg="#D1FAE5", fg="#065F46")

        # Reset button states
        self.btn_convert_gray.config(state="disabled")
        self.btn_process.config(state="disabled")
        self.btn_compare.config(state="disabled")
        self.btn_save.config(state="disabled")

        # Reset algorithm selection to default (Sobel)
        self.selected_operator.set(OperatorType.SOBEL.value)
        self._update_operator_info()

        self.set_status("Application reset. Ready for new image.")

    def _on_preview_area_resize(self, event):
        """Debounced handler to rescale previews when user resizes the window."""
        if self._resize_timer:
            self.root.after_cancel(self._resize_timer)
        self._resize_timer = self.root.after(100, self._rerender_previews)

    def _rerender_previews(self):
        """Redraws both preview canvases with updated dimensions preserving aspect ratio."""
        if self.original_pil_image:
            self._refresh_original_preview()
        if self.processed_pil_image:
            self._refresh_processed_preview()

    def _refresh_original_preview(self):
        """Scales and draws original PIL image inside its container, strictly preserving aspect ratio."""
        if not self.original_pil_image:
            return

        w = self.frame_orig_display.winfo_width() - 16
        h = self.frame_orig_display.winfo_height() - 16

        if w < 50 or h < 50:
            w, h = 380, 380

        resized = resize_image_aspect_ratio(self.original_pil_image, w, h)
        self._tk_orig_img = ImageTk.PhotoImage(resized)
        self.canvas_orig.config(image=self._tk_orig_img, text="")

    def _refresh_processed_preview(self):
        """Scales and draws processed/edge PIL image, strictly preserving aspect ratio."""
        if not self.processed_pil_image:
            return

        w = self.frame_proc_display.winfo_width() - 16
        h = self.frame_proc_display.winfo_height() - 16

        if w < 50 or h < 50:
            w, h = 380, 380

        resized = resize_image_aspect_ratio(self.processed_pil_image, w, h)
        self._tk_proc_img = ImageTk.PhotoImage(resized)
        self.canvas_proc.config(image=self._tk_proc_img, text="")


def run_app():
    """Initializes and runs the Tkinter desktop GUI event loop."""
    root = tk.Tk()
    app = EdgeDetectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
