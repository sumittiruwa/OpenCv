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
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Load Haar Cascade classifiers (built-in with OpenCV - NO EXTERNAL DEPENDENCY!)
print("Loading face detection model...")
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

print("✓ Face Detection: ACTIVE")
print("✓ HUD Overlay: ACTIVE")
print("✓ Threat Assessment: ACTIVE")

# Global variables
power_level = 100
energy_level = 85
system_status = "ONLINE"
threat_level = "GREEN"
arc_reactor_power = 100
frame_count = 0

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
    cv2.circle(frame, center, size // 3, (100, 255, 255), -1)
    
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
    """Draw professional corner brackets with animation"""
    corner_len = max(30, w // 8)
    
    # Animated glow
    glow_offset = int(2 * math.sin(frame_count * 0.05))
    
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
    
    # Multiple circles for targeting effect
    radii = [w//3, w//2, w//2 + 20]
    for radius in radii:
        cv2.circle(frame, (center_x, center_y), radius, color, 2)
    
    # Center crosshair
    crosshair_size = 15
    cv2.line(frame, (center_x - crosshair_size, center_y), 
             (center_x + crosshair_size, center_y), color, 2)
    cv2.line(frame, (center_x, center_y - crosshair_size), 
             (center_x, center_y + crosshair_size), color, 2)
    cv2.circle(frame, (center_x, center_y), 3, color, -1)

def draw_scan_lines(frame, x, y, w, h, color, alpha=0.2):
    """Draw animated scan lines effect"""
    overlay = frame.copy()
    line_height = 3
    for i in range(y, y + h, 15):
        cv2.line(overlay, (x, i), (x + w, i), color, line_height)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def draw_corner_dots(frame, x, y, w, h, color):
    """Draw glowing dots at face corners"""
    points = [
        (x, y),
        (x + w, y),
        (x, y + h),
        (x + w, y + h)
    ]
    for point in points:
        cv2.circle(frame, point, 6, color, -1)
        cv2.circle(frame, point, 8, color, 1)

def draw_pulse_effect(frame, x, y, w, h, color, frame_count):
    """Draw pulsing circle effect"""
    center_x = x + w // 2
    center_y = y + h // 2
    pulse_radius = int(w // 2.5 + 10 * math.sin(frame_count * 0.1))
    cv2.circle(frame, (center_x, center_y), pulse_radius, color, 1)

def draw_power_bar(frame, x, y, label, value, width=200, height=20, color=(0, 255, 100)):
    """Draw power/energy bar"""
    # Background
    cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
    
    # Fill based on value
    fill_width = int(width * (value / 100))
    cv2.rectangle(frame, (x, y), (x + fill_width, y + height), color, -1)
    
    # Label
    cv2.putText(frame, f"{label}: {int(value)}%", (x - 150, y + 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

def draw_threat_indicator(frame, frame_count, threat_level):
    """Draw threat level indicator"""
    h, w = frame.shape[:2]
    x, y = w - 250, h - 80
    
    threat_colors = {
        "GREEN": (0, 255, 0),
        "YELLOW": (0, 255, 255),
        "ORANGE": (0, 165, 255),
        "RED": (0, 0, 255)
    }
    
    color = threat_colors.get(threat_level, (0, 255, 0))
    
    # Draw threat box
    cv2.rectangle(frame, (x, y), (x + 200, y + 60), color, 2)
    
    # Flashing effect for RED
    if threat_level == "RED":
        if int(frame_count * 0.1) % 2:
            cv2.rectangle(frame, (x, y), (x + 200, y + 60), color, -1)
    
    cv2.putText(frame, "THREAT LEVEL", (x + 10, y + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.putText(frame, threat_level, (x + 30, y + 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def draw_holographic_grid(frame, frame_count):
    """Draw background holographic grid"""
    h, w = frame.shape[:2]
    alpha = 0.05 + 0.02 * math.sin(frame_count * 0.02)
    
    overlay = frame.copy()
    
    # Vertical lines
    for i in range(0, w, 100):
        cv2.line(overlay, (i, 0), (i, h), (0, 255, 100), 1)
    
    # Horizontal lines
    for i in range(0, h, 100):
        cv2.line(overlay, (0, i), (w, i), (0, 255, 100), 1)
    
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def draw_top_panel(frame, face_count, frame_count):
    """Draw professional top status panel"""
    h, w = frame.shape[:2]
    
    # Semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 70), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    
    # Border
    cv2.line(frame, (0, 70), (w, 70), (0, 255, 100), 2)
    
    # Status text
    font = cv2.FONT_HERSHEY_DUPLEX
    status_color = (0, 255, 0) if system_status == "ONLINE" else (0, 0, 255)
    
    cv2.putText(frame, "J.A.R.V.I.S. MULTI-SPECTRUM ANALYSIS SYSTEM", 
                (20, 30), font, 1, (0, 255, 100), 2)
    
    # Right side info
    time_str = datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, f"[{system_status}]", (w - 250, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    cv2.putText(frame, f"Targets: {face_count} | {time_str}", 
                (w - 500, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 1)

def draw_bottom_panel(frame, power_level, energy_level, arc_reactor_power):
    """Draw professional bottom status panel"""
    h, w = frame.shape[:2]
    panel_height = 120
    panel_y = h - panel_height
    
    # Semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, panel_y), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    
    # Border
    cv2.line(frame, (0, panel_y), (w, panel_y), (0, 255, 100), 2)
    
    # Power bars
    bar_y = panel_y + 20
    draw_power_bar(frame, 30, bar_y, "REPULSOR", power_level, 250, 15, (255, 0, 0))
    draw_power_bar(frame, 330, bar_y, "ENERGY", energy_level, 250, 15, (0, 255, 100))
    draw_power_bar(frame, 630, bar_y, "ARC REACTOR", arc_reactor_power, 250, 15, (0, 255, 200))
    
    # System info
    cv2.putText(frame, "SYSTEMS NOMINAL | ARMOR STATUS: 94% | FLIGHT CAPABLE", 
                (30, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 100), 1)

def draw_fun_elements(frame, faces, frame_count):
    """Add fun interactive elements"""
    if faces:
        # Draw iron man repulsor charging animation
        for (x, y, w, h) in faces:
            # Charging repulsor effect
            charge_size = int(20 + 15 * math.sin(frame_count * 0.08))
            cv2.circle(frame, (x + w + 30, y + 20), charge_size, (255, 0, 0), 2)
            cv2.circle(frame, (x + w + 30, y + 20), charge_size // 2, (255, 100, 0), -1)
            
            # "TARGETING" text with animation
            offset = int(5 * math.sin(frame_count * 0.05))
            cv2.putText(frame, "◆ TARGETING ◆", (x + offset, y - 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 2)

print("=" * 70)
print("✓ All systems initialized successfully!")
print("=" * 70)
print("Press 'q' to quit | Press 'r' to reset systems")
print("=" * 70)

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        frame_count += 1
        h, w, c = frame.shape
        
        # Draw background grid
        draw_holographic_grid(frame, frame_count)
        
        # Detect faces using Haar Cascade
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Update threat level based on detections
        if len(faces) > 2:
            threat_level = "ORANGE"
        elif len(faces) > 0:
            threat_level = "YELLOW"
        else:
            threat_level = "GREEN"
        
        # Draw face HUD
        colors = [(0, 255, 100), (100, 255, 0), (255, 0, 100), (0, 165, 255)]
        for idx, (x, y, w, h) in enumerate(faces):
            color = colors[idx % len(colors)]
            
            # Draw various HUD elements
            draw_corner_brackets(frame, x, y, w, h, color, frame_count, thickness=3)
            draw_hud_circles(frame, x, y, w, h, color, frame_count)
            draw_corner_dots(frame, x, y, w, h, color)
            draw_scan_lines(frame, x, y, w, h, color, alpha=0.2)
            draw_pulse_effect(frame, x, y, w, h, color, frame_count)
            
            # Face label
            cv2.putText(frame, f"FACE_{idx + 1}", (x + 10, y - 10), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, color, 2)
            
            # Arc reactor on face
            draw_arc_reactor(frame, x + w // 2, y + h // 2, 15, 
                           arc_reactor_power, frame_count)
            
            # Main face rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        
        # Draw top and bottom panels
        draw_top_panel(frame, len(faces), frame_count)
        draw_bottom_panel(frame, power_level, energy_level, arc_reactor_power)
        
        # Draw threat indicator
        draw_threat_indicator(frame, frame_count, threat_level)
        
        # Draw fun elements
        draw_fun_elements(frame, faces, frame_count)
        
        # Slow power drain
        power_level = max(0, power_level - 0.1)
        energy_level = max(0, energy_level - 0.05)
        arc_reactor_power = max(0, arc_reactor_power - 0.02)
        
        # Display frame
        cv2.imshow('J.A.R.V.I.S. - Iron Man Multi-Spectrum Analysis', frame)
        
        # Key handling
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nInitiating system shutdown sequence...")
            break
        elif key == ord('r'):
            print("Resetting all systems...")
            power_level = 100
            energy_level = 85
            arc_reactor_power = 100
            threat_level = "GREEN"

except KeyboardInterrupt:
    print("\nEmergency shutdown activated!")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("\n" + "=" * 70)
    print("J.A.R.V.I.S. OFFLINE - System shutdown complete")
    print("=" * 70)