"""
Hand Detection Module for AI Air Canvas

This module provides hand detection and tracking functionality using MediaPipe.
It detects hand landmarks and determines which fingers are raised for gesture recognition.
"""

import cv2
import mediapipe as mp
import math


class HandDetector:
    """
    Hand Detector class using MediaPipe Hands.
    
    Detects hands, tracks 21 landmarks per hand, and provides methods
    for gesture recognition based on finger positions.
    """
    
    # Landmark IDs for fingertips
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
    
    # All tip IDs in order: [thumb, index, middle, ring, pinky]
    TIP_IDS = [4, 8, 12, 16, 20]
    
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        """
        Initialize the Hand Detector.
        
        Args:
            mode (bool): If False, treats input as video stream (faster).
                        If True, treats each image independently.
            max_hands (int): Maximum number of hands to detect (1 or 2).
            detection_con (float): Minimum detection confidence (0.0-1.0).
            track_con (float): Minimum tracking confidence (0.0-1.0).
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        
        # Drawing utilities for visualization
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Store landmark positions
        self.landmark_list = []
        self.results = None
    
    def find_hands(self, frame, draw=True):
        """
        Detect hands in the given frame.
        
        Args:
            frame: BGR image from webcam (OpenCV format).
            draw (bool): If True, draw hand landmarks on the frame.
            
        Returns:
            frame: The input frame with hand landmarks drawn (if draw=True).
        """
        # Convert BGR to RGB (MediaPipe requires RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame for hand detection
        self.results = self.hands.process(frame_rgb)
        
        # Draw landmarks if hands are detected
        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        return frame
    
    def find_position(self, frame, hand_no=0, draw=True):
        """
        Get the position of all 21 hand landmarks.
        
        Args:
            frame: BGR image from webcam.
            hand_no (int): Which hand to get landmarks for (0 or 1).
            draw (bool): If True, draw circles on fingertips.
            
        Returns:
            list: List of [id, x, y] for each of the 21 landmarks.
                  Returns empty list if no hand detected.
        """
        self.landmark_list = []
        
        if self.results and self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                hand = self.results.multi_hand_landmarks[hand_no]
                
                # Get frame dimensions for coordinate conversion
                h, w, _ = frame.shape
                
                for id, landmark in enumerate(hand.landmark):
                    # Convert normalized coordinates to pixel coordinates
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    self.landmark_list.append([id, cx, cy])
                    
                    # Draw circles on fingertips
                    if draw and id in self.TIP_IDS:
                        cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        
        return self.landmark_list
    
    def fingers_up(self):
        """
        Detect which fingers are raised/extended.
        
        Returns:
            list: [thumb, index, middle, ring, pinky]
                  1 = finger is up, 0 = finger is down.
                  Example: [0, 1, 1, 0, 0] means index and middle are up.
        """
        fingers = []
        
        if len(self.landmark_list) == 0:
            return [0, 0, 0, 0, 0]
        
        # Thumb - Check x-axis (horizontal movement)
        # Compare thumb tip (4) with thumb IP joint (3)
        # For right hand: tip is to the LEFT of joint when thumb is up
        # For left hand: tip is to the RIGHT of joint when thumb is up
        # Simple approach: compare tip x with base joint x
        if self.landmark_list[self.THUMB_TIP][1] < self.landmark_list[self.THUMB_TIP - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other 4 fingers - Check y-axis (vertical movement)
        # Finger is UP if the tip is ABOVE (lower y value) the PIP joint
        for tip_id in [self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]:
            # Compare tip y-position with PIP joint (tip_id - 2)
            if self.landmark_list[tip_id][2] < self.landmark_list[tip_id - 2][2]:
                fingers.append(1)  # Finger is up
            else:
                fingers.append(0)  # Finger is down
        
        return fingers
    
    def find_distance(self, p1, p2, frame, draw=True):
        """
        Calculate the distance between two landmarks.
        
        Args:
            p1 (int): First landmark ID.
            p2 (int): Second landmark ID.
            frame: BGR image from webcam.
            draw (bool): If True, draw line and circles on the points.
            
        Returns:
            tuple: (distance, frame, [x1, y1, x2, y2, cx, cy])
                   distance: Euclidean distance in pixels
                   cx, cy: Center point between the two landmarks
        """
        if len(self.landmark_list) < max(p1, p2) + 1:
            return 0, frame, []
        
        x1, y1 = self.landmark_list[p1][1], self.landmark_list[p1][2]
        x2, y2 = self.landmark_list[p2][1], self.landmark_list[p2][2]
        
        # Calculate center point
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        # Calculate Euclidean distance
        distance = math.hypot(x2 - x1, y2 - y1)
        
        if draw:
            # Draw circles on both points
            cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            # Draw line between points
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
            # Draw circle at center
            cv2.circle(frame, (cx, cy), 8, (0, 255, 0), cv2.FILLED)
        
        return distance, frame, [x1, y1, x2, y2, cx, cy]
    
    def get_finger_tip(self, finger_id):
        """
        Get the position of a specific fingertip.
        
        Args:
            finger_id (int): 0=thumb, 1=index, 2=middle, 3=ring, 4=pinky
            
        Returns:
            tuple: (x, y) pixel coordinates of the fingertip.
                   Returns None if not detected.
        """
        if len(self.landmark_list) == 0:
            return None
        
        tip_id = self.TIP_IDS[finger_id]
        return (self.landmark_list[tip_id][1], self.landmark_list[tip_id][2])
    
    def count_fingers(self):
        """
        Count the total number of raised fingers.
        
        Returns:
            int: Number of fingers that are up (0-5).
        """
        return sum(self.fingers_up())
