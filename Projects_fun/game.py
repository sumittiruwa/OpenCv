import cv2
import numpy as np
import math
from datetime import datetime
import random

print("=" * 70)
print(" " * 15 + "J.A.R.V.I.S. SYSTEM INITIALIZATION")
print("=" * 70)

# Try to import MediaPipe for hand detection
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    HAND_DETECTION_AVAILABLE = True
    print("✓ MediaPipe Hand Detection: ACTIVE")
except:
    HAND_DETECTION_AVAILABLE = False
    print("⚠ MediaPipe not available - hand gestures disabled")

# Initialize video capture
print("Loading camera...")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("✓ OpenCV Version: " + cv2.__version__)
print("✓ HUD Overlay: ACTIVE (BLUE THEME)")
print("✓ Face Detection: ACTIVE")
print("✓ Hand Gesture: ACTIVE" if HAND_DETECTION_AVAILABLE else "✓ Hand Gesture: DISABLED")

# Color theme - BLUE
BLUE_BRIGHT = (255, 100, 0)      # Bright cyan-blue (BGR)
BLUE_MEDIUM = (200, 150, 0)      # Medium blue
BLUE_DARK = (100, 50, 0)         # Dark blue
BLUE_NEON = (255, 200, 0)        # Neon blue
GRID_COLOR = (200, 150, 0)       # Grid color

# Game variables
game_mode = "BATTLE"  # BATTLE, FINGER_COUNT, ROCK_PAPER, GESTURE_MASTER
game_score = 0
game_messages = []
finger_count_target = 0
rock_paper_choice = None
last_gesture = ""

# Global variables
power_level = 100
energy_level = 85
system_status = "ONLINE"
threat_level = "GREEN"
arc_reactor_power = 100
frame_count = 0
previous_frame = None

fun_messages = [
    "SYSTEMS OPTIMAL!",
    "READY FOR ACTION!",
    "POWER SURGE DETECTED!",
    "TARGET ACQUIRED!",
    "WEAPONS HOT!",
    "ARMOR ENGAGED!",
    "FLIGHT MODE ACTIVE!",
    "REPULSORS CHARGED!",
    "AWESOME!",
    "YOU'RE AMAZING!"
]

def detect_motion_regions(frame, previous_frame):
    """Detect faces/regions based on motion"""
    if previous_frame is None:
        return []
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
    
    diff = cv2.absdiff(gray, prev_gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    faces = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 3000:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 50:
                faces.append((x, y, w, h))
    
    return faces

def detect_skin_regions(frame):
    """Detect skin-colored regions"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    faces = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 5000:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 50 and w < 500 and h < 500:
                faces.append((x, y, w, h))
    
    return faces

def detect_hand_gestures(frame):
    """Detect hand gestures and draw skeleton"""
    if not HAND_DETECTION_AVAILABLE:
        return []
    
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    hand_info = []
    
    if results.multi_hand_landmarks:
        h, w, c = frame.shape
        
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Get hand center
            hand_center_x = int(hand_landmarks[9].x * w)
            hand_center_y = int(hand_landmarks[9].y * h)
            
            # Detect gesture
            gesture = detect_gesture(hand_landmarks)
            
            # Store hand info
            hand_info.append({
                'landmarks': hand_landmarks,
                'center': (hand_center_x, hand_center_y),
                'gesture': gesture,
                'handedness': handedness.classification[0].label,
                'confidence': handedness.classification[0].score
            })
            
            # Draw hand skeleton
            draw_hand_skeleton(frame, hand_landmarks, h, w, gesture)
    
    return hand_info

def detect_gesture(hand_landmarks):
    """Detect hand gesture"""
    # Get finger states
    fingers_up = []
    
    # Check fingers (excluding thumb initially)
    for i in [8, 12, 16, 20]:  # Index, middle, ring, pinky
        if hand_landmarks[i].y < hand_landmarks[i-2].y:
            fingers_up.append(True)
        else:
            fingers_up.append(False)
    
    # Count raised fingers
    count = sum(fingers_up)
    
    if count == 0:
        return "FIST"
    elif count == 1:
        return "ONE_FINGER"
    elif count == 2:
        return "PEACE_SIGN"
    elif count == 3:
        return "THREE_FINGERS"
    elif count == 4:
        return "OPEN_HAND"
    else:
        return "UNKNOWN"

def draw_hand_skeleton(frame, landmarks, h, w, gesture):
    """Draw hand skeleton with blue theme"""
    # Connection pairs for hand skeleton
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),  # Index
        (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
        (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
        (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    ]
    
    # Draw connections
    for start, end in connections:
        start_pos = (int(landmarks[start].x * w), int(landmarks[start].y * h))
        end_pos = (int(landmarks[end].x * w), int(landmarks[end].y * h))
        cv2.line(frame, start_pos, end_pos, BLUE_NEON, 3)
    
    # Draw joints
    for landmark in landmarks:
        x = int(landmark.x * w)
        y = int(landmark.y * h)
        cv2.circle(frame, (x, y), 5, BLUE_BRIGHT, -1)
        cv2.circle(frame, (x, y), 7, BLUE_NEON, 2)
    
    # Draw gesture label
    hand_center = (int(landmarks[9].x * w), int(landmarks[9].y * h))
    cv2.putText(frame, f"GESTURE: {gesture}", 
                (hand_center[0] - 50, hand_center[1] - 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLUE_NEON, 2)

def draw_arc_reactor(frame, x, y, size, power_level, frame_count):
    """Draw glowing Arc Reactor core in blue"""
    center = (x, y)
    
    glow_size = int(size + 10 * math.sin(frame_count * 0.05))
    cv2.circle(frame, center, glow_size, BLUE_NEON, 2)
    
    color_intensity = int(200 + 55 * math.sin(frame_count * 0.08))
    cv2.circle(frame, center, size, (color_intensity, 150, 0), -1)
    
    cv2.circle(frame, center, max(1, size // 3), BLUE_NEON, -1)
    
    angle_step = 360 // 8
    for i in range(8):
        angle = math.radians(i * angle_step + frame_count * 2)
        inner_x = int(x + (size * 0.6) * math.cos(angle))
        inner_y = int(y + (size * 0.6) * math.sin(angle))
        outer_x = int(x + (size * 1.1) * math.cos(angle))
        outer_y = int(y + (size * 1.1) * math.sin(angle))
        cv2.line(frame, (inner_x, inner_y), (outer_x, outer_y), BLUE_NEON, 2)

def draw_corner_brackets(frame, x, y, w, h, color, frame_count, thickness=3):
    """Draw professional corner brackets"""
    corner_len = max(30, w // 8)
    
    cv2.line(frame, (x, y), (x + corner_len, y), color, thickness)
    cv2.line(frame, (x, y), (x, y + corner_len), color, thickness)
    
    cv2.line(frame, (x + w, y), (x + w - corner_len, y), color, thickness)
    cv2.line(frame, (x + w, y), (x + w, y + corner_len), color, thickness)
    
    cv2.line(frame, (x, y + h), (x + corner_len, y + h), color, thickness)
    cv2.line(frame, (x, y + h), (x, y + h - corner_len), color, thickness)
    
    cv2.line(frame, (x + w, y + h), (x + w - corner_len, y + h), color, thickness)
    cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_len), color, thickness)

def draw_hud_circles(frame, x, y, w, h, color, frame_count):
    """Draw circular HUD targeting elements"""
    center_x = x + w // 2
    center_y = y + h // 2
    
    radii = [max(1, w//3), max(1, w//2), max(1, w//2 + 20)]
    for radius in radii:
        cv2.circle(frame, (center_x, center_y), radius, color, 2)
    
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

def draw_power_bar(frame, x, y, label, value, width=200, height=20, color=None):
    """Draw power bar in blue theme"""
    if color is None:
        color = BLUE_BRIGHT
    
    cv2.rectangle(frame, (x, y), (x + width, y + height), (30, 30, 30), -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
    
    fill_width = int(width * (value / 100))
    cv2.rectangle(frame, (x, y), (x + fill_width, y + height), color, -1)
    
    cv2.putText(frame, f"{label}: {int(value)}%", (x - 150, y + 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

def draw_threat_indicator(frame, frame_count, threat_level):
    """Draw threat level in blue theme"""
    h, w = frame.shape[:2]
    x, y = w - 250, h - 80
    
    threat_colors = {
        "GREEN": (0, 200, 0),
        "YELLOW": (0, 200, 200),
        "ORANGE": (0, 165, 255),
        "RED": (0, 0, 255)
    }
    
    color = threat_colors.get(threat_level, (0, 200, 0))
    
    cv2.rectangle(frame, (x, y), (x + 200, y + 60), color, 2)
    
    if threat_level == "RED":
        if int(frame_count * 0.1) % 2:
            cv2.rectangle(frame, (x, y), (x + 200, y + 60), color, -1)
    
    cv2.putText(frame, "THREAT LEVEL", (x + 10, y + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.putText(frame, threat_level, (x + 30, y + 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def draw_holographic_grid(frame, frame_count):
    """Draw background grid in blue theme"""
    h, w = frame.shape[:2]
    alpha = 0.05 + 0.02 * math.sin(frame_count * 0.02)
    
    overlay = frame.copy()
    
    for i in range(0, w, 100):
        cv2.line(overlay, (i, 0), (i, h), GRID_COLOR, 1)
    
    for i in range(0, h, 100):
        cv2.line(overlay, (0, i), (w, i), GRID_COLOR, 1)
    
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def draw_top_panel(frame, face_count, hand_count, frame_count):
    """Draw top status panel in blue theme"""
    h, w = frame.shape[:2]
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 70), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    
    cv2.line(frame, (0, 70), (w, 70), BLUE_BRIGHT, 2)
    
    status_color = (0, 200, 0) if system_status == "ONLINE" else (0, 0, 255)
    
    cv2.putText(frame, "J.A.R.V.I.S. MULTI-SPECTRUM ANALYSIS SYSTEM", 
                (20, 30), cv2.FONT_HERSHEY_DUPLEX, 1, BLUE_BRIGHT, 2)
    
    time_str = datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, f"[{system_status}]", (w - 250, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    cv2.putText(frame, f"Faces: {face_count} | Hands: {hand_count} | {time_str}", 
                (w - 600, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLUE_BRIGHT, 1)

def draw_bottom_panel(frame, power_level, energy_level, arc_reactor_power):
    """Draw bottom status panel in blue theme"""
    h, w = frame.shape[:2]
    panel_height = 120
    panel_y = h - panel_height
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, panel_y), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    
    cv2.line(frame, (0, panel_y), (w, panel_y), BLUE_BRIGHT, 2)
    
    bar_y = panel_y + 20
    draw_power_bar(frame, 30, bar_y, "REPULSOR", power_level, 250, 15, BLUE_BRIGHT)
    draw_power_bar(frame, 330, bar_y, "ENERGY", energy_level, 250, 15, (150, 200, 255))
    draw_power_bar(frame, 630, bar_y, "ARC REACTOR", arc_reactor_power, 250, 15, BLUE_NEON)
    
    cv2.putText(frame, "SYSTEMS NOMINAL | ARMOR STATUS: 94% | FLIGHT CAPABLE", 
                (30, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE_BRIGHT, 1)

def draw_game_panel(frame, game_mode, hand_info):
    """Draw interactive game panel"""
    h, w = frame.shape[:2]
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 90), (400, 200), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    
    cv2.rectangle(frame, (10, 90), (400, 200), BLUE_NEON, 2)
    
    cv2.putText(frame, f"GAME MODE: {game_mode}", (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, BLUE_NEON, 2)
    
    if game_mode == "FINGER_COUNT" and hand_info:
        gesture = hand_info[0]['gesture']
        cv2.putText(frame, f"Gesture: {gesture}", (20, 145),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLUE_BRIGHT, 1)
        cv2.putText(frame, f"Score: {game_score}", (20, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLUE_BRIGHT, 1)
    
    elif game_mode == "BATTLE":
        if game_messages:
            cv2.putText(frame, game_messages[0], (20, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

def draw_floating_messages(frame):
    """Draw floating fun messages"""
    if game_messages:
        msg = game_messages[0]
        h, w = frame.shape[:2]
        text_size = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        x = (w - text_size[0]) // 2
        y = h // 2
        
        cv2.putText(frame, msg, (x, y),
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, BLUE_NEON, 3)

print("=" * 70)
print("✓ All systems initialized!")
print("=" * 70)
print("Controls:")
print("  'q' - Quit | 'r' - Reset | 's' - Switch detection | 'g' - Change game")
print("=" * 70)

detection_mode = "MOTION"

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
        
        # Detect hands
        hand_info = detect_hand_gestures(frame)
        
        # Update threat level
        if len(faces) > 2 or len(hand_info) > 1:
            threat_level = "ORANGE"
        elif len(faces) > 0 or len(hand_info) > 0:
            threat_level = "YELLOW"
        else:
            threat_level = "GREEN"
        
        # Game logic
        if game_mode == "BATTLE" and (frame_count % 30 == 0):
            game_messages = [random.choice(fun_messages)]
        
        if len(hand_info) > 0:
            gesture = hand_info[0]['gesture']
            if game_mode == "FINGER_COUNT":
                if gesture == "FIST":
                    game_score += 1
        
        # Draw HUD for detected faces
        face_colors = [BLUE_BRIGHT, (100, 200, 255), (255, 150, 0), (0, 200, 255)]
        for idx, (x, y, fw, fh) in enumerate(faces):
            color = face_colors[idx % len(face_colors)]
            
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
        draw_top_panel(frame, len(faces), len(hand_info), frame_count)
        draw_bottom_panel(frame, power_level, energy_level, arc_reactor_power)
        draw_threat_indicator(frame, frame_count, threat_level)
        draw_game_panel(frame, game_mode, hand_info)
        
        # Draw floating messages
        if game_messages:
            draw_floating_messages(frame)
            if frame_count % 60 == 0:
                game_messages = []
        
        # Power drain
        power_level = max(0, power_level - 0.1)
        energy_level = max(0, energy_level - 0.05)
        arc_reactor_power = max(0, arc_reactor_power - 0.02)
        
        cv2.putText(frame, f"Detection: {detection_mode}", (20, h - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLUE_BRIGHT, 1)
        
        cv2.imshow('J.A.R.V.I.S. - Iron Man Multi-Spectrum Analysis', frame)
        
        previous_frame = frame.copy()
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nShutting down system...")
            break
        elif key == ord('r'):
            print("Resetting systems...")
            power_level = 100
            energy_level = 85
            arc_reactor_power = 100
            game_score = 0
        elif key == ord('s'):
            detection_mode = "SKIN" if detection_mode == "MOTION" else "MOTION"
            print(f"Switched to {detection_mode} detection mode")
        elif key == ord('g'):
            modes = ["BATTLE", "FINGER_COUNT", "ROCK_PAPER", "GESTURE_MASTER"]
            idx = modes.index(game_mode)
            game_mode = modes[(idx + 1) % len(modes)]
            print(f"Game mode: {game_mode}")

except KeyboardInterrupt:
    print("\nEmergency shutdown!")

finally:
    cap.release()
    cv2.destroyAllWindows()
    if HAND_DETECTION_AVAILABLE:
        hands.close()
    print("\n" + "=" * 70)
    print("J.A.R.V.I.S. OFFLINE - Shutdown complete")
    print("=" * 70)