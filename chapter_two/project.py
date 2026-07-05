import cv2
import mediapipe as mp
import numpy as np
import math
from collections import deque
from enum import Enum
import time

class Gesture(Enum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2
    NONE = 3

class GestureGame:
    def __init__(self, width=1280, height=720, target_fps=30):
        """Initialize the gesture game with optimized settings"""
        self.width = width
        self.height = height
        self.target_fps = target_fps
        self.frame_time = 1 / target_fps
        
        # MediaPipe setup (optimized)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=0  # Use lite model for better performance
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Game state
        self.gesture_history = deque(maxlen=5)  # Store recent gestures
        self.scores = {"player": 0, "computer": 0, "draws": 0}
        self.current_gesture = Gesture.NONE
        self.game_state = "waiting"  # waiting, showing, result
        self.state_timer = 0
        self.state_duration = 1.5
        
        # Performance tracking
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()
        self.frame_times = deque(maxlen=30)
        
        # Gesture confidence
        self.gesture_confidence = 0
        
    def detect_gesture(self, hand_landmarks, handedness):
        """Detect gesture from hand landmarks (optimized)"""
        if hand_landmarks is None:
            return Gesture.NONE, 0
        
        # Get key points
        landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
        
        # Calculate finger states efficiently
        thumb_open = self._is_finger_open(landmarks, 2, 3, 4)
        index_open = self._is_finger_open(landmarks, 6, 7, 8)
        middle_open = self._is_finger_open(landmarks, 10, 11, 12)
        ring_open = self._is_finger_open(landmarks, 14, 15, 16)
        pinky_open = self._is_finger_open(landmarks, 18, 19, 20)
        
        fingers_open = sum([thumb_open, index_open, middle_open, ring_open, pinky_open])
        
        # Determine gesture based on finger states
        if fingers_open == 0:
            return Gesture.ROCK, 0.9
        elif fingers_open == 2:
            # Check if it's scissors (index and middle open)
            if index_open and middle_open:
                return Gesture.SCISSORS, 0.85
        elif fingers_open >= 4:
            return Gesture.PAPER, 0.9
        
        return Gesture.NONE, 0.5
    
    @staticmethod
    def _is_finger_open(landmarks, pip_idx, dip_idx, tip_idx):
        """Check if a finger is open using PIP and TIP positions"""
        pip = landmarks[pip_idx]
        dip = landmarks[dip_idx]
        tip = landmarks[tip_idx]
        
        # If tip is above PIP, finger is open
        return tip[1] < pip[1]
    
    def get_computer_choice(self):
        """Get random computer choice"""
        return np.random.choice([Gesture.ROCK, Gesture.PAPER, Gesture.SCISSORS])
    
    def determine_winner(self, player, computer):
        """Determine winner of RPS"""
        if player == computer:
            return "draw"
        
        wins = {
            (Gesture.ROCK, Gesture.SCISSORS): "player",
            (Gesture.SCISSORS, Gesture.PAPER): "player",
            (Gesture.PAPER, Gesture.ROCK): "player",
        }
        
        return wins.get((player, computer), "computer")
    
    def update_game_state(self, frame_time):
        """Update game state timing"""
        self.state_timer += frame_time
        
        if self.state_timer >= self.state_duration:
            if self.game_state == "waiting":
                self.game_state = "showing"
            elif self.game_state == "showing":
                self.game_state = "result"
            elif self.game_state == "result":
                self.game_state = "waiting"
                self.current_gesture = Gesture.NONE
            
            self.state_timer = 0
    
    def draw_info(self, frame):
        """Draw game info on frame (optimized drawing)"""
        # Draw scores
        score_text = f"Player: {self.scores['player']} | Computer: {self.scores['computer']} | Draws: {self.scores['draws']}"
        cv2.putText(frame, score_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (self.width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw current gesture
        gesture_text = self.current_gesture.name if self.current_gesture != Gesture.NONE else "Waiting..."
        cv2.putText(frame, f"Your gesture: {gesture_text}", (10, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw instructions
        if self.game_state == "waiting":
            cv2.putText(frame, "Show your gesture!", (self.width // 2 - 200, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    def run(self):
        """Main game loop (optimized)"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for lower latency
        
        clock = cv2.getTickFrequency()
        last_process_time = time.time()
        
        while True:
            frame_start = time.time()
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Flip frame for selfie view
            frame = cv2.flip(frame, 1)
            
            # Process frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)
            
            # Detect gesture
            if results.multi_hand_landmarks and results.multi_handedness:
                hand_landmarks = results.multi_hand_landmarks[0]
                handedness = results.multi_handedness[0].classification[0].label
                
                gesture, confidence = self.detect_gesture(hand_landmarks, handedness)
                
                if gesture != Gesture.NONE:
                    self.current_gesture = gesture
                    self.gesture_confidence = confidence
                
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
            
            # Update game state
            current_time = time.time()
            frame_time = current_time - last_process_time
            last_process_time = current_time
            self.update_game_state(frame_time)
            
            # Process game logic
            if self.game_state == "showing":
                computer_choice = self.get_computer_choice()
                result = self.determine_winner(self.current_gesture, computer_choice)
                
                if result == "player":
                    self.scores["player"] += 1
                elif result == "computer":
                    self.scores["computer"] += 1
                else:
                    self.scores["draws"] += 1
                
                self.game_state = "result"
            
            # Draw UI
            self.draw_info(frame)
            
            # Update FPS
            self.frame_count += 1
            frame_end = time.time()
            self.frame_times.append(frame_end - frame_start)
            
            if self.frame_count % 10 == 0:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                self.fps = 1 / avg_frame_time if avg_frame_time > 0 else 0
            
            # Display frame
            cv2.imshow("Gesture Game", frame)
            
            # Frame rate control
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
            # FPS limiting
            elapsed = time.time() - frame_start
            if elapsed < self.frame_time:
                time.sleep(self.frame_time - elapsed)
        
        cap.release()
        cv2.destroyAllWindows()
        self.hands.close()

if __name__ == "__main__":
    game = GestureGame(width=1280, height=720, target_fps=30)
    game.run()