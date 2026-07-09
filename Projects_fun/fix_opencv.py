#!/usr/bin/env python3
"""
OpenCV Installation Fixer - Diagnose and fix OpenCV issues
"""

import subprocess
import sys

print("=" * 70)
print("OpenCV Installation Diagnostic & Fixer")
print("=" * 70)

# Step 1: Check if cv2 can be imported
print("\n[1/4] Checking if OpenCV can be imported...")
try:
    import cv2
    print(f"  ✓ OpenCV {cv2.__version__} imported successfully")
except ImportError as e:
    print(f"  ✗ OpenCV import failed: {e}")
    print("\n  Fixing: Installing OpenCV...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "opencv-python"], check=True)
    import cv2
    print(f"  ✓ OpenCV {cv2.__version__} installed!")

# Step 2: Check for CascadeClassifier
print("\n[2/4] Checking for CascadeClassifier function...")
try:
    if hasattr(cv2, 'CascadeClassifier'):
        print("  ✓ CascadeClassifier available")
    else:
        print("  ✗ CascadeClassifier not found!")
        print("\n  This means OpenCV is corrupted. Reinstalling...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"], check=False)
        subprocess.run([sys.executable, "-m", "pip", "install", "opencv-python"], check=True)
        import cv2
        if hasattr(cv2, 'CascadeClassifier'):
            print("  ✓ CascadeClassifier now available!")
        else:
            print("  ✗ Still not working. Try: pip install opencv-contrib-python")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Step 3: Check for haarcascades data
print("\n[3/4] Checking for Haar Cascade data files...")
try:
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    print(f"  Looking for: {cascade_path}")
    
    import os
    if os.path.exists(cascade_path):
        print(f"  ✓ Cascade file found!")
    else:
        print(f"  ✗ Cascade file not found at: {cascade_path}")
        print("  This is a serious OpenCV installation issue.")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Step 4: Test OpenCV functions
print("\n[4/4] Testing OpenCV functions...")
try:
    # Test basic functions
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Test if we can create a CascadeClassifier
    cascade = cv2.CascadeClassifier()
    print("  ✓ Can create CascadeClassifier object")
    
    # Test VideoCapture
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.release()
        print("  ✓ Webcam accessible")
    else:
        print("  ⚠ Webcam not accessible (this is OK - camera might be busy)")
    
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
print("RECOMMENDATIONS:")
print("=" * 70)

try:
    import cv2
    if hasattr(cv2, 'CascadeClassifier'):
        print("\n✅ OpenCV appears to be working correctly!")
        print("\nYou can now run:")
        print("  python face_working.py")
    else:
        print("\n⚠️  OpenCV has issues. Try this:")
        print("\n1. pip uninstall opencv-python -y")
        print("2. pip install opencv-python")
        print("3. python fix_opencv.py  (run this script again)")
except:
    print("\n❌ Critical OpenCV installation issue!")
    print("\nFix with:")
    print("1. pip uninstall opencv-python opencv-contrib-python -y")
    print("2. pip install opencv-python")
    print("3. python fix_opencv.py")

print("\n" + "=" * 70)