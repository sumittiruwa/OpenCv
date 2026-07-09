#!/usr/bin/env python3
"""
J.A.R.V.I.S. System Installation Script
Installs all required dependencies for Iron Man HUD Face Detection
"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """Run a shell command and return success status"""
    print(f"\n► {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {description} - SUCCESS")
            return True
        else:
            print(f"  ✗ {description} - FAILED")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Error running command: {e}")
        return False

def check_python():
    """Check Python version"""
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"\n✓ Python {version} detected")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher required!")
        return False
    return True

def check_import(module_name, package_name=""):
    """Check if a module can be imported"""
    if not package_name:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"  ✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"  ✗ {package_name} is NOT installed")
        return False

def main():
    print("=" * 70)
    print(" " * 15 + "J.A.R.V.I.S. SYSTEM INSTALLATION")
    print("=" * 70)
    
    # Check Python version
    if not check_python():
        print("\nDownload Python 3.8+ from: https://www.python.org/downloads/")
        sys.exit(1)
    
    # Upgrade pip
    print("\n" + "=" * 70)
    print("STEP 1: Updating pip")
    print("=" * 70)
    run_command(f"{sys.executable} -m pip install --upgrade pip", 
                "Upgrading pip")
    
    # Install packages
    print("\n" + "=" * 70)
    print("STEP 2: Installing Required Packages")
    print("=" * 70)
    
    packages = [
        ("opencv-python", "OpenCV (Computer Vision)"),
        ("mediapipe", "MediaPipe (ML Vision)"),
        ("numpy", "NumPy (Numerical Computing)"),
    ]
    
    for package, description in packages:
        run_command(f"pip install --upgrade {package}", 
                    f"Installing {description}")
    
    # Verify installation
    print("\n" + "=" * 70)
    print("STEP 3: Verifying Installation")
    print("=" * 70)
    
    imports_ok = True
    
    print("\nChecking imports:")
    for module, name in [("cv2", "OpenCV"), ("mediapipe", "MediaPipe"), ("numpy", "NumPy")]:
        if not check_import(module, name):
            imports_ok = False
    
    # Final result
    print("\n" + "=" * 70)
    if imports_ok:
        print("✅ SUCCESS! All systems operational!")
        print("=" * 70)
        print("\n🚀 To run the program:")
        print(f"   {sys.executable} face.py")
        print("\nOr:")
        print("   python face.py")
        print("\n" + "=" * 70)
        return 0
    else:
        print("❌ Installation incomplete - some packages failed!")
        print("=" * 70)
        print("\nTroubleshooting:")
        print("1. Try: pip install --upgrade --force-reinstall mediapipe")
        print("2. Try: pip install protobuf==3.20.0 before reinstalling mediapipe")
        print("3. Make sure you're NOT in a virtual environment conflict")
        print("\n" + "=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())