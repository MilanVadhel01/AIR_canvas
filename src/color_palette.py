"""
Color Palette Module for AI Air Canvas

Provides a visual color palette header bar with gesture-based selection.
"""

import cv2


class ColorPalette:
    """
    Visual color palette for selecting drawing colors.
    
    Displays color boxes at the top of the frame and detects
    when the user's finger hovers over a color to select it.
    """
    
    def __init__(self, frame_width, header_height=100):
        """
        Initialize the color palette.
        
        Args:
            frame_width (int): Width of the video frame.
            header_height (int): Height of the palette header area.
        """
        self.frame_width = frame_width
        self.header_height = header_height
        
        # Define colors (BGR format) with names
        self.colors = [
            {'name': 'Purple', 'bgr': (255, 0, 255)},
            {'name': 'Blue', 'bgr': (255, 0, 0)},
            {'name': 'Green', 'bgr': (0, 255, 0)},
            {'name': 'Red', 'bgr': (0, 0, 255)},
            {'name': 'Yellow', 'bgr': (0, 255, 255)},
            {'name': 'Eraser', 'bgr': (0, 0, 0)},
        ]
        
        # Calculate box dimensions
        self.num_colors = len(self.colors)
        self.box_width = frame_width // self.num_colors
        
        # Create color box regions
        self.color_boxes = []
        for i, color in enumerate(self.colors):
            x1 = i * self.box_width
            x2 = (i + 1) * self.box_width
            self.color_boxes.append({
                'x1': x1,
                'x2': x2,
                'y1': 0,
                'y2': self.header_height,
                'color': color['bgr'],
                'name': color['name']
            })
    
    def draw(self, frame, selected_color=None):
        """
        Draw the color palette on the frame.
        
        Args:
            frame: The video frame to draw on.
            selected_color: Currently selected color (BGR tuple).
            
        Returns:
            frame: Frame with palette drawn.
        """
        for box in self.color_boxes:
            # Draw filled color box
            cv2.rectangle(frame, 
                         (box['x1'], box['y1']), 
                         (box['x2'], box['y2']),
                         box['color'], cv2.FILLED)
            
            # Draw border (white for visibility)
            cv2.rectangle(frame,
                         (box['x1'], box['y1']),
                         (box['x2'], box['y2']),
                         (255, 255, 255), 2)
            
            # Highlight selected color with thicker border
            if selected_color == box['color']:
                cv2.rectangle(frame,
                             (box['x1'] + 5, box['y1'] + 5),
                             (box['x2'] - 5, box['y2'] - 5),
                             (255, 255, 255), 4)
            
            # Draw color name
            text_color = (0, 0, 0) if box['name'] != 'Eraser' else (255, 255, 255)
            cv2.putText(frame, box['name'],
                       (box['x1'] + 10, box['y1'] + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        
        return frame
    
    def check_selection(self, x, y):
        """
        Check if a point (finger position) is over a color box.
        
        Args:
            x (int): X coordinate of the finger.
            y (int): Y coordinate of the finger.
            
        Returns:
            tuple or None: BGR color tuple if over a box, None otherwise.
        """
        if y > self.header_height:
            return None
        
        for box in self.color_boxes:
            if box['x1'] <= x <= box['x2'] and box['y1'] <= y <= box['y2']:
                return box['color']
        
        return None
    
    def is_in_header(self, y):
        """Check if y coordinate is in the header area."""
        return y < self.header_height
