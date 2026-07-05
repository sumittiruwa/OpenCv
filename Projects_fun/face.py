import cv2
import numpy as np
import math
from datetime import datetime

print("Loading J.A.R.V.I.S. Libraries...")

# Import MediaPipe
import mediapipe as mp

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
face_detector = mp_face.FaceDetection(min_detection_confidence=0.7)

print("✓ MediaPipe loaded successfully")

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Global variables
power_level = 100
energy_level = 85
system_status = "ONLINE"
threat_level = "GREEN"
arc_reactor_power = 100
frame_count = 0
recorded_gestures = []

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

def draw_advanced_hud_box(frame, x, y, w, h, color, frame_count, label=""):
    """Draw professional Iron Man style HUD box"""
    thickness = 2
    corner_len = max(30, w // 8)
    
    # Animated border glow
    glow_color = tuple([min(255, c + 50) for c in color])
    offset = int(3 * math.sin(frame_count * 0.05))
    
    # Corner brackets with glow effect
    corners = [
        (x, y), (x + w, y), (x, y + h), (x + w, y + h)
    ]
    
    for corner_x, corner_y in [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]:
        # Determine direction
        dx = 1 if corner_x == x else -1
        dy = 1 if corner_y == y else -1
        
        # Horizontal and vertical lines
        cv2.line(frame, (corner_x, corner_y), 
                (corner_x + dx * corner_len, corner_y), glow_color, thickness)
        cv2.line(frame, (corner_x, corner_y), 
                (corner_x, corner_y + dy * corner_len), glow_color, thickness)

def detect_hand_gesture(hand_landmarks, frame_shape):
    """Detect hand gestures"""
    if hand_landmarks is None:
        return "NONE"
    
    # Get key points
    thumb = hand_landmarks[4]
    index = hand_landmarks[8]
    middle = hand_landmarks[12]
    ring = hand_landmarks[16]
    pinky = hand_landmarks[20]
    palm = hand_landmarks[0]
    
    # Calculate distances
    thumb_up = thumb.y < hand_landmarks[3].y
    index_up = index.y < hand_landmarks[7].y
    middle_up = middle.y < hand_landmarks[11].y
    ring_up = ring.y < hand_landmarks[15].y
    pinky_up = pinky.y < hand_landmarks[19].y
    
    fingers_up = [index_up, middle_up, ring_up, pinky_up]
    fingers_count = sum(fingers_up)
    
    # Recognize gestures
    if not thumb_up and fingers_count == 0:
        return "FIST"
    elif thumb_up and fingers_count == 4:
        return "OPEN_HAND"
    elif thumb_up and fingers_count == 1 and index_up:
        return "PEACE"
    elif fingers_count == 1 and index_up:
        return "POINT"
    elif fingers_count == 2 and index_up and middle_up:
        return "PEACE"
    else:
        return f"{fingers_count}_FINGERS"

def draw_hand_hud(frame, hand_landmarks, handedness, frame_count):
    """Draw professional HUD around detected hand"""
    if hand_landmarks is None:
        return "NONE"
    
    h, w, c = frame.shape
    
    # Get hand center
    hand_x = int(hand_landmarks[9].x * w)
    hand_y = int(hand_landmarks[9].y * h)
    
    # Color based on hand (left/right)
    color = (255, 0, 0) if handedness == "Right" else (0, 255, 255)
    
    # Detect gesture
    gesture = detect_hand_gesture(hand_landmarks, frame.shape)
    
    # Draw circular HUD around hand
    radius = 60
    cv2.circle(frame, (hand_x, hand_y), radius, color, 2)
    cv2.circle(frame, (hand_x, hand_y), radius + 15, color, 1)
    cv2.circle(frame, (hand_x, hand_y), radius - 15, color, 1)
    
    # Draw crosshair
    cv2.line(frame, (hand_x - 20, hand_y), (hand_x + 20, hand_y), color, 2)
    cv2.line(frame, (hand_x, hand_y - 20), (hand_x, hand_y + 20), color, 2)
    cv2.circle(frame, (hand_x, hand_y), 5, color, -1)
    
    # Draw gesture label
    cv2.putText(frame, f"GESTURE: {gesture}", (hand_x - 50, hand_y - 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Draw hand joints
    for idx, lm in enumerate(hand_landmarks):
        lx, ly = int(lm.x * w), int(lm.y * h)
        cv2.circle(frame, (lx, ly), 4, color, -1)
        if idx in [4, 8, 12, 16, 20]:  # Finger tips
            cv2.circle(frame, (lx, ly), 6, color, 2)
    
    return gesture

def draw_power_bar(frame, x, y, label, value, width=200, height=20, color=(0, 255, 100)):
    """Draw power/energy bar"""
    # Background
    cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
    
    # Fill based on value
    fill_width = int(width * (value / 100))
    cv2.rectangle(frame, (x, y), (x + fill_width, y + height), color, -1)
    
    # Label and percentage
    cv2.putText(frame, f"{label}: {value}%", (x - 150, y + 15), 
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
    
    # Flashing effect for critical
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

def draw_top_panel(frame, face_count, hand_count, frame_count):
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
    cv2.putText(frame, f"Targets: {face_count} | Hands: {hand_count} | {time_str}", 
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

def draw_fun_elements(frame, faces, hands_detected, frame_count):
    """Add fun interactive elements"""
    if faces:
        # Draw iron man repulsor charging animation
        for (x, y, w, h) in faces:
            cx, cy = x + w // 2, y + h // 2
            
            # Charging repulsor effect
            charge_size = int(20 + 15 * math.sin(frame_count * 0.08))
            cv2.circle(frame, (x + w + 30, y + 20), charge_size, (255, 0, 0), 2)
            cv2.circle(frame, (x + w + 30, y + 20), charge_size // 2, (255, 100, 0), -1)
            
            # "TARGETING" text with animation
            offset = int(5 * math.sin(frame_count * 0.05))
            cv2.putText(frame, "◆ TARGETING ◆", (x + offset, y - 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 2)
    
    if hands_detected > 0:
        # Floating particles effect
        h, w = frame.shape[:2]
        for i in range(5):
            particle_x = int(100 + 80 * math.sin(frame_count * 0.02 + i))
            particle_y = int(50 + 30 * math.cos(frame_count * 0.03 + i))
            cv2.circle(frame, (particle_x, particle_y), 2, (0, 255, 200), -1)

def draw_warning_text(frame, text, frame_count):
    """Draw blinking warning text"""
    if int(frame_count * 0.1) % 2:
        h, w = frame.shape[:2]
        cv2.putText(frame, text, (w // 2 - 150, h // 2), 
                    cv2.FONT_HERSHEY_BOLD, 1.2, (0, 0, 255), 3)

# Main loop
print("=" * 70)
print(" " * 15 + "J.A.R.V.I.S. MULTI-SPECTRUM ANALYSIS SYSTEM")
print("=" * 70)
print("INITIALIZING PROTOCOLS...")
print("✓ Face Detection: ACTIVE")
print("✓ Hand Gesture Recognition: ACTIVE")
print("✓ HUD Overlay: ACTIVE")
print("✓ Threat Assessment: ACTIVE")
print("=" * 70)
print("Press 'q' to shutdown | Press 'r' to reset systems")
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
        
        # Detect faces
        results_face = face_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        faces = []
        if results_face.detections:
            for detection in results_face.detections:
                bboxC = detection.location_data.relative_bounding_box
                x = int(bboxC.xmin * w)
                y = int(bboxC.ymin * h)
                width = int(bboxC.width * w)
                height = int(bboxC.height * h)
                faces.append((x, y, width, height))
        
        # Detect hands
        results_hands = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        hand_count = 0
        hand_gestures = []
        
        if results_hands.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results_hands.multi_hand_landmarks, 
                                                   results_hands.multi_handedness):
                hand_count += 1
                hand_label = handedness.classification[0].label
                gesture = draw_hand_hud(frame, hand_landmarks, hand_label, frame_count)
                hand_gestures.append(gesture)
        
        # Update threat level based on detections
        if len(faces) > 2 or hand_count > 1:
            threat_level = "ORANGE"
        elif len(faces) > 0 or hand_count > 0:
            threat_level = "YELLOW"
        else:
            threat_level = "GREEN"
        
        # Draw face HUD
        colors = [(0, 255, 100), (100, 255, 0), (255, 0, 100), (0, 165, 255)]
        for idx, (x, y, width, height) in enumerate(faces):
            color = colors[idx % len(colors)]
            
            # Advanced HUD box
            draw_advanced_hud_box(frame, x, y, width, height, color, frame_count)
            
            # Face label
            cv2.putText(frame, f"FACE_{idx + 1}", (x + 10, y - 10), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, color, 2)
            
            # Arc reactor on face
            draw_arc_reactor(frame, x + width // 2, y + height // 2, 15, 
                           arc_reactor_power, frame_count)
        
        # Draw top and bottom panels
        draw_top_panel(frame, len(faces), hand_count, frame_count)
        draw_bottom_panel(frame, power_level, energy_level, arc_reactor_power)
        
        # Draw threat indicator
        draw_threat_indicator(frame, frame_count, threat_level)
        
        # Draw fun elements
        draw_fun_elements(frame, faces, hand_count, frame_count)
        
        # Fun gesture-based messages
        if "PEACE" in hand_gestures:
            draw_warning_text(frame, "PEACE SIGN DETECTED", frame_count)
            power_level = min(100, power_level + 1)
        
        if "FIST" in hand_gestures:
            threat_level = "RED"
            power_level = max(0, power_level - 2)
        
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
    hands.close()
    face_detector.close()
    print("\n" + "=" * 70)
    print("J.A.R.V.I.S. OFFLINE - System shutdown complete")
    print("=" * 70)