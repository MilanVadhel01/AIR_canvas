"""
AI Air Canvas - Streamlit Web Application

A web-based virtual drawing application using hand gestures.
Uses streamlit-webrtc for browser webcam access.

Run with: streamlit run app.py
"""

import streamlit as st
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av

from src.hand_detector import HandDetector
from src.color_palette import ColorPalette


# Page configuration
st.set_page_config(
    page_title="AI Air Canvas",
    page_icon="🎨",
    layout="wide"
)


class AirCanvasProcessor(VideoProcessorBase):
    """Video processor for AI Air Canvas with hand gesture recognition."""
    
    def __init__(self):
        # Configuration
        self.CAMERA_WIDTH = 640
        self.CAMERA_HEIGHT = 480
        self.BRUSH_THICKNESS = 15
        self.ERASER_THICKNESS = 50
        self.MIN_BRUSH_SIZE = 5
        self.MAX_BRUSH_SIZE = 50
        
        # Colors (BGR format)
        self.COLORS = {
            'purple': (255, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'red': (0, 0, 255),
            'yellow': (0, 255, 255),
        }
        self.ERASER_COLOR = (0, 0, 0)
        
        # Drawing state
        self.draw_color = self.COLORS['purple']
        self.brush_thickness = self.BRUSH_THICKNESS
        self.is_eraser_mode = False
        self.previous_color = self.draw_color
        
        # Previous point for drawing lines
        self.prev_x = 0
        self.prev_y = 0
        
        # Initialize components
        self.detector = HandDetector(detection_con=0.7, track_con=0.7, max_hands=1)
        self.palette = ColorPalette(self.CAMERA_WIDTH, header_height=80)
        
        # Create blank canvas
        self.canvas = np.zeros((self.CAMERA_HEIGHT, self.CAMERA_WIDTH, 3), np.uint8)
    
    def recv(self, frame):
        """Process each video frame."""
        img = frame.to_ndarray(format="bgr24")
        
        # Resize frame if needed
        img = cv2.resize(img, (self.CAMERA_WIDTH, self.CAMERA_HEIGHT))
        
        # Flip horizontally for mirror effect
        img = cv2.flip(img, 1)
        
        # Detect hands
        img = self.detector.find_hands(img)
        landmark_list = self.detector.find_position(img, draw=False)
        
        if len(landmark_list) != 0:
            # Get fingertip positions
            index_tip = self.detector.get_finger_tip(1)
            
            # Check which fingers are up
            fingers = self.detector.fingers_up()
            
            # Display finger count
            finger_count = self.detector.count_fingers()
            cv2.putText(img, f'Fingers: {finger_count}', (50, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # SELECTION MODE: Index + Middle finger up
            if fingers == [0, 1, 1, 0, 0]:
                self.prev_x, self.prev_y = 0, 0
                cv2.putText(img, "SELECTION", (50, 135),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                if index_tip:
                    selected = self.palette.check_selection(index_tip[0], index_tip[1])
                    if selected is not None:
                        self.draw_color = selected
                        if selected == self.ERASER_COLOR:
                            self.is_eraser_mode = True
                            self.brush_thickness = self.ERASER_THICKNESS
                        else:
                            self.is_eraser_mode = False
                            self.brush_thickness = self.BRUSH_THICKNESS
                    
                    cv2.rectangle(img, 
                                 (index_tip[0] - 15, index_tip[1] - 15),
                                 (index_tip[0] + 15, index_tip[1] + 15),
                                 self.draw_color, 2)
            
            # DRAWING MODE: Only index finger up
            elif fingers == [0, 1, 0, 0, 0]:
                cv2.putText(img, "DRAWING", (50, 135),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if index_tip:
                    x, y = index_tip
                    cv2.circle(img, (x, y), 10, self.draw_color, cv2.FILLED)
                    
                    if self.prev_x == 0 and self.prev_y == 0:
                        self.prev_x, self.prev_y = x, y
                    
                    cv2.line(self.canvas, (self.prev_x, self.prev_y), (x, y), 
                            self.draw_color, self.brush_thickness)
                    self.prev_x, self.prev_y = x, y
            
            # CLEAR CANVAS: All fingers up
            elif fingers == [1, 1, 1, 1, 1]:
                cv2.putText(img, "CLEAR", (50, 135),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                self.canvas = np.zeros((self.CAMERA_HEIGHT, self.CAMERA_WIDTH, 3), np.uint8)
                self.prev_x, self.prev_y = 0, 0
            
            # ERASER MODE: Fist gesture
            elif fingers == [0, 0, 0, 0, 0]:
                cv2.putText(img, "ERASER", (50, 135),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
                self.is_eraser_mode = True
                self.draw_color = self.ERASER_COLOR
                self.brush_thickness = self.ERASER_THICKNESS
                self.prev_x, self.prev_y = 0, 0
            
            else:
                self.prev_x, self.prev_y = 0, 0
        
        # Merge canvas with frame
        canvas_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, canvas_inv = cv2.threshold(canvas_gray, 20, 255, cv2.THRESH_BINARY_INV)
        canvas_inv = cv2.cvtColor(canvas_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, canvas_inv)
        img = cv2.bitwise_or(img, self.canvas)
        
        # Draw color palette
        img = self.palette.draw(img, self.draw_color)
        
        # Display brush size
        cv2.putText(img, f'Size: {self.brush_thickness}px', (self.CAMERA_WIDTH - 150, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")
    
    def clear_canvas(self):
        """Clear the canvas."""
        self.canvas = np.zeros((self.CAMERA_HEIGHT, self.CAMERA_WIDTH, 3), np.uint8)
    
    def set_color(self, color_name):
        """Set the drawing color."""
        if color_name in self.COLORS:
            self.draw_color = self.COLORS[color_name]
            self.is_eraser_mode = False
            self.brush_thickness = self.BRUSH_THICKNESS
    
    def set_brush_size(self, size):
        """Set the brush size."""
        self.brush_thickness = max(self.MIN_BRUSH_SIZE, min(self.MAX_BRUSH_SIZE, size))


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🎨 AI Air Canvas")
    st.markdown("Draw in the air using hand gestures!")
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎮 Controls")
        
        st.markdown("""
        **Gestures:**
        - ☝️ Index finger → Draw
        - ✌️ Index + Middle → Select color
        - 🖐️ Open palm → Clear canvas
        - ✊ Fist → Eraser
        """)
        
        st.divider()
        
        st.subheader("🎨 Colors")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.color_picker("Purple", "#FF00FF", disabled=True)
            st.color_picker("Red", "#FF0000", disabled=True)
        with col2:
            st.color_picker("Blue", "#0000FF", disabled=True)
            st.color_picker("Yellow", "#FFFF00", disabled=True)
        with col3:
            st.color_picker("Green", "#00FF00", disabled=True)
        
        st.divider()
        st.info("💡 Select colors using gestures in the video header bar!")
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # WebRTC streamer
        ctx = webrtc_streamer(
            key="air-canvas",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=AirCanvasProcessor,
            media_stream_constraints={
                "video": {"width": 640, "height": 480},
                "audio": False
            },
            async_processing=True,
        )
    
    with col2:
        st.markdown("### 📋 Quick Guide")
        st.markdown("""
        1. **Allow camera** access
        2. **Point index finger** to draw
        3. **Two fingers up** to select colors
        4. **Open palm** to clear
        5. **Make fist** to erase
        """)
        
        if st.button("🗑️ Clear Canvas", use_container_width=True):
            st.info("Use open palm gesture to clear!")
    
    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Built with ❤️ using Streamlit, MediaPipe & OpenCV"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
