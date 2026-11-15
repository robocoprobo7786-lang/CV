"""
Computer Vision Edge Detection Application
Entry Point (main.py)

Course: Computer Vision (256PUPC275)
Topic: Edge Detection Using Sobel, Prewitt, and Laplacian Operators
"""

import sys
import os
import tkinter as tk

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.gui import EdgeDetectionApp


def main():
    """Main application entry point."""
    print("=" * 68)
    print(" Computer Vision Edge Detection Studio")
    print(" Topic: Sobel, Prewitt, and Laplacian Operators")
    print(" Course: Computer Vision (256PUPC275)")
    print("=" * 68)

    # Environment sanity check
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required to run this application.")
        sys.exit(1)

    print(f"Python interpreter: {sys.version.split()[0]} ({sys.executable})")
    print("Launching Desktop GUI...")

    try:
        root = tk.Tk()
        app = EdgeDetectionApp(root)
        root.mainloop()
        print("Application terminated cleanly.")
    except Exception as e:
        print(f"\n[FATAL ERROR] An unexpected error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

