import cv2
import numpy as np
import math
from datetime import datetime

print("=" * 70)
print(" " * 15 + "J.A.R.V.I.S. SYSTEM INITIALIZATION")
print("=" * 70)

# Initialize video capture
print("Loading camera...")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,1080)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("✓ OpenCV Version: " + cv2.__version__)
print("✓ HUD Overlay: ACTIVE")
print("✓ Face Detection: ACTIVE (Motion-based)")

# Global variables
power_level = 100
energy_level = 85
system_status = "ONLINE"
threat_level = "GREEN"
arc_reactor_power = 100
frame_count = 0
previous_frame = None

def detect_motion_regions(frame, previous_frame):
    """Detect faces/regions based on motion and color"""
    if previous_frame is None:
        return []
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate difference
    diff = cv2.absdiff(gray, prev_gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Get bounding boxes of moving regions
    faces = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 3000:  # Filter small regions
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 50:  # Minimum face size
                faces.append((x, y, w, h))
    
    return faces

def detect_skin_regions(frame):
    """Detect skin-colored regions (face detection alternative)"""
    # Convert to HSV for better skin detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Skin color range in HSV
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    # Apply morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Get bounding boxes
    faces = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 5000:  # Filter small regions
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 50 and w < 500 and h < 500:  # Face size constraints
                faces.append((x, y, w, h))
    
    return faces

def draw_arc_reactor(frame, x, y, size, power_level, frame_count):
    """Draw glowing Arc Reactor core"""
    center = (x, y)
    
    # Outer glow
    glow_size = int(size + 10 * math.sin(frame_count * 0.05))
    cv2.circle(frame, center, glow_size, (0, 255, 200), 2)
    
    # Core circle
    color_intensity = int(200 + 55 * math.sin(frame_count * 0.08))
    cv2.circle(frame, center, size, (0, color_intensity, 255), -1)
    
    # Inner bright spot
    cv2.circle(frame, center, max(1, size // 3), (100, 255, 255), -1)
    
    # Power indicator lines
    angle_step = 360 // 8
    for i in range(8):
        angle = math.radians(i * angle_step + frame_count * 2)
        inner_x = int(x + (size * 0.6) * math.cos(angle))
        inner_y = int(y + (size * 0.6) * math.sin(angle))
        outer_x = int(x + (size * 1.1) * math.cos(angle))
        outer_y = int(y + (size * 1.1) * math.sin(angle))
        cv2.line(frame, (inner_x, inner_y), (outer_x, outer_y), (0, 255, 200), 2)

def draw_corner_brackets(frame, x, y, w, h, color, frame_count, thickness=3):
    """Draw professional corner brackets"""
    corner_len = max(30, w // 8)
    
    # Top-left
    cv2.line(frame, (x, y), (x + corner_len, y), color, thickness)
    cv2.line(frame, (x, y), (x, y + corner_len), color, thickness)
    
    # Top-right
    cv2.line(frame, (x + w, y), (x + w - corner_len, y), color, thickness)
    cv2.line(frame, (x + w, y), (x + w, y + corner_len), color, thickness)
    
    # Bottom-left
    cv2.line(frame, (x, y + h), (x + corner_len, y + h), color, thickness)
    cv2.line(frame, (x, y + h), (x, y + h - corner_len), color, thickness)
    
    # Bottom-right
    cv2.line(frame, (x + w, y + h), (x + w - corner_len, y + h), color, thickness)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_len), color, thickness)

def draw_hud_circles(frame, x, y, w, h, color, frame_count):
    """Draw circular HUD targeting elements"""
    center_x = x + w // 2
    center_y = y + h // 2
    
    # Multiple circles
    radii = [max(1, w//3), max(1, w//2), max(1, w//2 + 20)]
    for radius in radii:
        cv2.circle(frame, (center_x, center_y), radius, color, 2)
    
    # Crosshair
    crosshair_size = 15
    cv2.line(frame, (center_x - crosshair_size, center_y), 
             (center_x + crosshair_size, center_y), color, 2)
    cv2.line(frame, (center_x, center_y - crosshair_size), 
             (center_x, center_y + crosshair_size), color, 2)
    cv2.circle(frame, (center_x, center_y), 3, color, -1)

def draw_scan_lines(frame, x, y, w, h, color, alpha=0.2):
    """Draw animated scan lines"""
    overlay = frame.copy()
    for i in range(y, y + h, 15):
        cv2.line(overlay, (x, i), (x + w, i), color, 3)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def draw_pulse_effect(frame, x, y, w, h, color, frame_count):
    """Draw pulsing circle"""
    center_x = x + w // 2
    center_y = y + h // 2
    pulse_radius = int(w // 2.5 + 10 * math.sin(frame_count * 0.1))
    cv2.circle(frame, (center_x, center_y), max(1, pulse_radius), color, 1)

def draw_power_bar(frame, x, y, label, value, width=200, height=20, color=(0, 255, 100)):
    """Draw power bar"""
    cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
    
    fill_width = int(width * (value / 100))
    cv2.rectangle(frame, (x, y), (x + fill_width, y + height), color, -1)
    
    cv2.putText(frame, f"{label}: {int(value)}%", (x - 150, y + 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

def draw_threat_indicator(frame, frame_count, threat_level):
    """Draw threat level"""
    h, w = frame.shape[:2]
    x, y = w - 250, h - 80
    
    threat_colors = {
        "GREEN": (0, 255, 0),
        "YELLOW": (0, 255, 255),
        "ORANGE": (0, 165, 255),
        "RED": (0, 0, 255)
    }
    
    color = threat_colors.get(threat_level, (0, 255, 0))
    
    cv2.rectangle(frame, (x, y), (x + 200, y + 60), color, 2)
    
    if threat_level == "RED":
        if int(frame_count * 0.1) % 2:
            cv2.rectangle(frame, (x, y), (x + 200, y + 60), color, -1)
    
    cv2.putText(frame, "THREAT LEVEL", (x + 10, y + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.putText(frame, threat_level, (x + 30, y + 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def draw_holographic_grid(frame, frame_count):
    """Draw background grid"""
    h, w = frame.shape[:2]
    alpha = 0.05 + 0.02 * math.sin(frame_count * 0.02)
    
    overlay = frame.copy()
    
    for i in range(0, w, 100):
        cv2.line(overlay, (i, 0), (i, h), (0, 255, 100), 1)
    
    for i in range(0, h, 100):
        cv2.line(overlay, (0, i), (w, i), (0, 255, 100), 1)
    
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def draw_top_panel(frame, face_count, frame_count):
    """Draw top status panel"""
    h, w = frame.shape[:2]
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 70), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    
    cv2.line(frame, (0, 70), (w, 70), (0, 255, 100), 2)
    
    status_color = (0, 255, 0) if system_status == "ONLINE" else (0, 0, 255)
    
    cv2.putText(frame, "J.A.R.V.I.S. MULTI-SPECTRUM ANALYSIS SYSTEM", 
                (20, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 100), 2)
    
    time_str = datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, f"[{system_status}]", (w - 250, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    cv2.putText(frame, f"Targets: {face_count} | {time_str}", 
                (w - 500, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 1)

def draw_bottom_panel(frame, power_level, energy_level, arc_reactor_power):
    """Draw bottom status panel"""
    h, w = frame.shape[:2]
    panel_height = 120
    panel_y = h - panel_height
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, panel_y), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    
    cv2.line(frame, (0, panel_y), (w, panel_y), (0, 255, 100), 2)
    
    bar_y = panel_y + 20
    draw_power_bar(frame, 30, bar_y, "REPULSOR", power_level, 250, 15, (255, 0, 0))
    draw_power_bar(frame, 330, bar_y, "ENERGY", energy_level, 250, 15, (0, 255, 100))
    draw_power_bar(frame, 630, bar_y, "ARC REACTOR", arc_reactor_power, 250, 15, (0, 255, 200))
    
    cv2.putText(frame, "SYSTEMS NOMINAL | ARMOR STATUS: 94% | FLIGHT CAPABLE", 
                (30, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 100), 1)

print("=" * 70)
print("✓ All systems initialized!")
print("=" * 70)
print("Press 'q' to quit | Press 'r' to reset | Press 's' for skin detection")
print("=" * 70)

detection_mode = "MOTION"  # Can be MOTION or SKIN

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        frame_count += 1
        h, w, c = frame.shape
        
        # Draw background grid
        draw_holographic_grid(frame, frame_count)
        
        # Detect faces
        if detection_mode == "MOTION" and previous_frame is not None:
            faces = detect_motion_regions(frame, previous_frame)
        else:
            faces = detect_skin_regions(frame)
        
        # Update threat level
        if len(faces) > 2:
            threat_level = "ORANGE"
        elif len(faces) > 0:
            threat_level = "YELLOW"
        else:
            threat_level = "GREEN"
        
        # Draw HUD for detected faces
        colors = [(0, 255, 100), (100, 255, 0), (255, 0, 100), (0, 165, 255)]
        for idx, (x, y, fw, fh) in enumerate(faces):
            color = colors[idx % len(colors)]
            
            draw_corner_brackets(frame, x, y, fw, fh, color, frame_count, thickness=3)
            draw_hud_circles(frame, x, y, fw, fh, color, frame_count)
            draw_scan_lines(frame, x, y, fw, fh, color, alpha=0.2)
            draw_pulse_effect(frame, x, y, fw, fh, color, frame_count)
            
            cv2.putText(frame, f"FACE_{idx + 1}", (x + 10, y - 10), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, color, 2)
            
            draw_arc_reactor(frame, x + fw // 2, y + fh // 2, 15, 
                           arc_reactor_power, frame_count)
            
            cv2.rectangle(frame, (x, y), (x + fw, y + fh), color, 2)
        
        # Draw panels
        draw_top_panel(frame, len(faces), frame_count)
        draw_bottom_panel(frame, power_level, energy_level, arc_reactor_power)
        draw_threat_indicator(frame, frame_count, threat_level)
        
        # Power drain
        power_level = max(0, power_level - 0.1)
        energy_level = max(0, energy_level - 0.05)
        arc_reactor_power = max(0, arc_reactor_power - 0.02)
        
        # Display mode text
        cv2.putText(frame, f"Detection: {detection_mode}", (20, h - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 1)
        
        cv2.imshow('J.A.R.V.I.S. - Iron Man Multi-Spectrum Analysis', frame)
        
        previous_frame = frame.copy()
        
        # Key handling
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nShutting down system...")
            break
        elif key == ord('r'):
            print("Resetting systems...")
            power_level = 100
            energy_level = 85
            arc_reactor_power = 100
        elif key == ord('s'):
            detection_mode = "SKIN" if detection_mode == "MOTION" else "MOTION"
            print(f"Switched to {detection_mode} detection mode")

except KeyboardInterrupt:
    print("\nEmergency shutdown!")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("\n" + "=" * 70)
    print("J.A.R.V.I.S. OFFLINE - Shutdown complete")
    print("=" * 70)