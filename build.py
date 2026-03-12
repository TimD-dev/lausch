import PyInstaller.__main__
import os
import shutil

def clean_build_dirs():
    """Removes previous build and dist directories to ensure a clean build."""
    print("🧹 Cleaning up old build directories...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Deleted {dir_name}/")

def build_app():
    """Runs PyInstaller with the required arguments."""
    print("🚀 Starting PyInstaller build process...")
    
    # Define the PyInstaller arguments
    args = [
        'main.py',                 # Entry point script
        '--name=lausch',           # Name of the output executable/folder
        '--onedir',                # Create a directory-based build (faster startup than --onefile)
        '--noconfirm',             # Automatically overwrite existing output
        '--clean',                 # Clean PyInstaller cache
        
        # We need a console for now to see the prints.
        # Once a UI is fully integrated and logging is implemented,
        # this can be changed to '--noconsole' or '--windowed'.
        '--console',               
        
        # Collect all dependencies for heavy ML libraries
        '--collect-all=faster_whisper',
        '--collect-all=ctranslate2',
        '--collect-all=tokenizers',
        
        # Explicit hidden imports that might not be picked up automatically
        '--hidden-import=sounddevice',
        '--hidden-import=soundfile',
        '--hidden-import=keyboard',
        '--hidden-import=pyperclip',
        '--hidden-import=numpy'
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("✅ Build process completed successfully!")
    print("📁 You can find the executable in the 'dist/lausch' directory.")
    print("📦 To distribute the app, zip the entire 'dist/lausch' folder.")

if __name__ == "__main__":
    clean_build_dirs()
    build_app()
