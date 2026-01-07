"""
AI Air Canvas - Main Application

A virtual drawing application that allows you to draw in the air
using hand gestures detected via webcam.

Usage:
    python main.py

Controls:
    - Index finger up: Draw mode
    - Index + Middle finger up: Selection mode (move cursor)
    - All fingers up: Clear canvas
    - Press 'q' to quit
    - Press 's' to save drawing
    - Press 'c' to clear canvas
"""

import cv2
import numpy as np
from src.hand_detector import HandDetector
from src.color_palette import ColorPalette


def main():
    """Main function to run the AI Air Canvas application."""
    
    # =====================
    # Configuration
    # =====================
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    BRUSH_THICKNESS = 15
    ERASER_THICKNESS = 50
    
    # Colors (BGR format)
    COLORS = {
        'purple': (255, 0, 255),
        'blue': (255, 0, 0),
        'green': (0, 255, 0),
        'red': (0, 0, 255),
        'yellow': (0, 255, 255),
        'white': (255, 255, 255),
    }
    
    # Current drawing settings
    draw_color = COLORS['purple']
    brush_thickness = BRUSH_THICKNESS
    
    # =====================
    # Initialize Components
    # =====================
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    
    if not cap.isOpened():
        print("Error: Could not open webcam!")
        return
    
    # Initialize hand detector
    detector = HandDetector(detection_con=0.7, track_con=0.7, max_hands=1)
    
    # Initialize color palette
    palette = ColorPalette(CAMERA_WIDTH)
    
    # Create blank canvas (same size as camera frame)
    canvas = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), np.uint8)
    
    # Previous point for drawing lines
    prev_x, prev_y = 0, 0
    
    print("=" * 50)
    print("🎨 AI Air Canvas Started!")
    print("=" * 50)
    print("\n📋 Controls:")
    print("  • Index finger up → Draw")
    print("  • Index + Middle fingers up → Move cursor")
    print("  • All fingers up → Clear canvas")
    print("  • Press 'q' → Quit")
    print("  • Press 's' → Save drawing")
    print("  • Press 'c' → Clear canvas")
    print("\n" + "=" * 50)
    
    # =====================
    # Main Loop
    # =====================
    while True:
        # Read frame from webcam
        success, frame = cap.read()
        if not success:
            print("Error: Failed to read from webcam!")
            break
        
        # Flip frame horizontally (mirror effect)
        frame = cv2.flip(frame, 1)
        
        # Detect hands
        frame = detector.find_hands(frame)
        landmark_list = detector.find_position(frame, draw=False)
        
        if len(landmark_list) != 0:
            # Get fingertip positions
            index_tip = detector.get_finger_tip(1)  # Index finger
            
            # Check which fingers are up
            fingers = detector.fingers_up()
            finger_count = detector.count_fingers()
            
            # Display finger count
            cv2.putText(frame, f'Fingers: {finger_count}', (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # =====================
            # Gesture Recognition
            # =====================
            
            # SELECTION MODE: Index + Middle finger up
            if fingers == [0, 1, 1, 0, 0]:
                prev_x, prev_y = 0, 0  # Reset drawing
                cv2.putText(frame, "SELECTION MODE", (50, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                # Check for color selection in palette
                if index_tip:
                    selected = palette.check_selection(index_tip[0], index_tip[1])
                    if selected is not None:
                        draw_color = selected
                    
                    # Draw rectangle at cursor position
                    cv2.rectangle(frame, 
                                 (index_tip[0] - 20, index_tip[1] - 20),
                                 (index_tip[0] + 20, index_tip[1] + 20),
                                 draw_color, 3)
            
            # DRAWING MODE: Only index finger up
            elif fingers == [0, 1, 0, 0, 0]:
                cv2.putText(frame, "DRAWING MODE", (50, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                if index_tip:
                    x, y = index_tip
                    
                    # Draw circle at fingertip
                    cv2.circle(frame, (x, y), 15, draw_color, cv2.FILLED)
                    
                    # Draw line from previous point to current point
                    if prev_x == 0 and prev_y == 0:
                        prev_x, prev_y = x, y
                    
                    # Draw on canvas
                    cv2.line(canvas, (prev_x, prev_y), (x, y), draw_color, brush_thickness)
                    
                    # Update previous point
                    prev_x, prev_y = x, y
            
            # CLEAR CANVAS: All fingers up (open palm)
            elif fingers == [1, 1, 1, 1, 1]:
                cv2.putText(frame, "CLEAR CANVAS", (50, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                canvas = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), np.uint8)
                prev_x, prev_y = 0, 0
            
            else:
                prev_x, prev_y = 0, 0  # Reset when not drawing
        
        # =====================
        # Merge Canvas with Frame
        # =====================
        
        # Convert canvas to grayscale to create mask
        canvas_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, canvas_inv = cv2.threshold(canvas_gray, 20, 255, cv2.THRESH_BINARY_INV)
        canvas_inv = cv2.cvtColor(canvas_inv, cv2.COLOR_GRAY2BGR)
        
        # Apply mask to frame and add canvas
        frame = cv2.bitwise_and(frame, canvas_inv)
        frame = cv2.bitwise_or(frame, canvas)
        
        # =====================
        # Display UI Elements
        # =====================
        
        # Draw color palette
        frame = palette.draw(frame, draw_color)
        
        # Show the frame
        cv2.imshow("AI Air Canvas", frame)
        
        # =====================
        # Keyboard Controls
        # =====================
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n👋 Exiting AI Air Canvas...")
            break
        elif key == ord('c'):
            canvas = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), np.uint8)
            print("🗑️  Canvas cleared!")
        elif key == ord('s'):
            filename = f"output/drawing_{cv2.getTickCount()}.png"
            try:
                cv2.imwrite(filename, canvas)
                print(f"💾 Drawing saved to: {filename}")
            except:
                print("⚠️  Error saving. Make sure 'output' folder exists!")
        elif key == ord('1'):
            draw_color = COLORS['purple']
        elif key == ord('2'):
            draw_color = COLORS['blue']
        elif key == ord('3'):
            draw_color = COLORS['green']
        elif key == ord('4'):
            draw_color = COLORS['red']
        elif key == ord('5'):
            draw_color = COLORS['yellow']
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
