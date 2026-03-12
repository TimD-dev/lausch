"""Build script for creating a standalone Windows executable with PyInstaller."""

import os
import shutil
import sys

import PyInstaller.__main__


# Ensure we run from the project root, not from scripts/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)


def clean_build_dirs() -> None:
    """Remove previous build and dist directories to ensure a clean build."""
    print("Cleaning up old build directories...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Deleted {dir_name}/")


def build_app() -> None:
    """Run PyInstaller with the required arguments."""
    print("Starting PyInstaller build process...")

    args = [
        os.path.join("lausch", "__main__.py"),
        "--name=lausch",
        "--onedir",
        "--noconfirm",
        "--clean",
        # Console enabled for development; change to --windowed for release
        "--console",
        # Collect all dependencies for heavy ML libraries
        "--collect-all=faster_whisper",
        "--collect-all=ctranslate2",
        "--collect-all=tokenizers",
        # Explicit hidden imports
        "--hidden-import=sounddevice",
        "--hidden-import=soundfile",
        "--hidden-import=keyboard",
        "--hidden-import=pyperclip",
        "--hidden-import=numpy",
        # Ensure package root is on path
        f"--pathex={PROJECT_ROOT}",
    ]

    PyInstaller.__main__.run(args)

    print("Build process completed successfully!")
    print("You can find the executable in the 'dist/lausch' directory.")
    print("To distribute the app, zip the entire 'dist/lausch' folder.")


if __name__ == "__main__":
    clean_build_dirs()
    build_app()
