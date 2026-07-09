#!/usr/bin/env python3
"""
J.A.R.V.I.S. Diagnostic Tool
Check if all dependencies are properly installed
"""

import sys
import subprocess

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def check_version(module_name):
    """Get and print module version"""
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"  ✓ {module_name.upper()}: {version}")
        return True
    except ImportError as e:
        print(f"  ✗ {module_name.upper()}: NOT INSTALLED")
        print(f"     Error: {e}")
        return False

def test_mediapipe_hands():
    """Test if MediaPipe hands module works"""
    try:
        import mediapipe as mp
        hands = mp.solutions.hands.Hands()
        print("  ✓ MediaPipe Hands: WORKING")
        return True
    except Exception as e:
        print(f"  ✗ MediaPipe Hands: FAILED")
        print(f"     Error: {str(e)[:100]}")
        return False

def test_mediapipe_face():
    """Test if MediaPipe face detection works"""
    try:
        import mediapipe as mp
        face = mp.solutions.face_detection.FaceDetection()
        print("  ✓ MediaPipe Face Detection: WORKING")
        return True
    except Exception as e:
        print(f"  ✗ MediaPipe Face Detection: FAILED")
        print(f"     Error: {str(e)[:100]}")
        return False

def test_opencv_webcam():
    """Test if OpenCV can access webcam"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            print("  ✓ OpenCV Webcam: WORKING")
            return True
        else:
            print("  ✗ OpenCV Webcam: NOT ACCESSIBLE")
            print("     Make sure no other app is using the camera")
            return False
    except Exception as e:
        print(f"  ✗ OpenCV Webcam: ERROR - {e}")
        return False

def get_pip_list():
    """Show installed packages"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True, timeout=10)
        packages = result.stdout.split('\n')
        relevant = [p for p in packages if any(x in p.lower() for x in ['opencv', 'mediapipe', 'numpy', 'protobuf'])]
        return relevant
    except:
        return []

def main():
    print_header("J.A.R.V.I.S. SYSTEM DIAGNOSTIC")
    
    # Python version
    print(f"\nPython Version: {sys.version}")
    print(f"Executable: {sys.executable}")
    
    # Check modules
    print_header("CHECKING CORE MODULES")
    
    modules_ok = True
    modules_ok &= check_version('cv2')
    modules_ok &= check_version('mediapipe')
    modules_ok &= check_version('numpy')
    
    # Check MediaPipe functionality
    print_header("TESTING MEDIAPIPE COMPONENTS")
    
    mp_ok = True
    mp_ok &= test_mediapipe_hands()
    mp_ok &= test_mediapipe_face()
    
    # Check OpenCV
    print_header("TESTING OPENCV FUNCTIONS")
    
    opencv_ok = test_opencv_webcam()
    
    # Show installed packages
    print_header("INSTALLED PACKAGES")
    packages = get_pip_list()
    if packages:
        for pkg in packages:
            if pkg.strip():
                print(f"  {pkg}")
    
    # Recommendations
    print_header("RECOMMENDATIONS")
    
    if not modules_ok or not mp_ok:
        print("\n⚠️  INSTALLATION ISSUES DETECTED")
        print("\nQuick Fix:")
        print("  1. python -m pip install --upgrade pip")
        print("  2. pip uninstall mediapipe -y")
        print("  3. pip install mediapipe --no-cache-dir")
        print("  4. python setup.py")
        
        if not mp_ok:
            print("\nAlternative Fix for MediaPipe:")
            print("  pip install protobuf==3.20.0")
            print("  pip install mediapipe")
    
    if not opencv_ok:
        print("\n⚠️  WEBCAM ISSUE")
        print("  • Check if another app is using the camera")
        print("  • Try plugging in a different USB camera")
        print("  • Check Windows camera permissions")
    
    if modules_ok and mp_ok and opencv_ok:
        print("\n✅ ALL SYSTEMS OPERATIONAL!")
        print("\nReady to run:")
        print("  python face.py")
    else:
        print("\n❌ ISSUES FOUND - SEE ABOVE")
    
    print_header("END DIAGNOSTIC")
    
    return 0 if (modules_ok and mp_ok and opencv_ok) else 1

if __name__ == "__main__":
    sys.exit(main())