Implement hand detection module------

# Hand Detection Module Explanation

## Overview
The `HandDetector` class in `src/hand_detector.py` uses **MediaPipe** to detect hands and track 21 landmarks for gesture recognition.

---

## Key Methods

| Method | Purpose |
|--------|---------|
| `find_hands()` | Detects hands and draws landmarks on frame |
| `find_position()` | Gets pixel coordinates of all 21 landmarks |
| `fingers_up()` | Returns which fingers are raised `[thumb, index, middle, ring, pinky]` |
| `get_finger_tip()` | Gets position of a specific fingertip |
| `count_fingers()` | Counts total raised fingers (0-5) |

---

## Gesture Recognition

```python
fingers = detector.fingers_up()

# Gestures:
[0, 1, 1, 0, 0]  # Index + Middle up → Selection mode
[0, 1, 0, 0, 0]  # Only Index up → Drawing mode  
[1, 1, 1, 1, 1]  # All fingers up → Clear canvas
```

---

## Hand Landmarks

```
       8   12  16  20   (Fingertips)
       |   |   |   |
   4   7   11  15  19
   |   |   |   |   |
   3   6   10  14  18
   |   |   |   |   |
   2   5   9   13  17
    \  |   |   |   /
       0  (Wrist)
```

---

## Usage in main.py

```python
detector = HandDetector(detection_con=0.7, max_hands=1)

frame = detector.find_hands(frame)
landmark_list = detector.find_position(frame)
fingers = detector.fingers_up()
index_tip = detector.get_finger_tip(1)  # Get index finger position
```

---

# Create Canvas Drawing Logic

## What Was Added

| Feature | Gesture | Description |
|---------|---------|-------------|
| Canvas Init | - | `np.zeros()` creates blank 1280x720 canvas |
| Draw Mode | `[0,1,0,0,0]` | Index finger draws lines |
| Selection | `[0,1,1,0,0]` | Index + Middle moves cursor |
| Clear | `[1,1,1,1,1]` | Open palm clears canvas |
| Overlay | - | Bitwise ops merge canvas with webcam |

---

# Add Color Palette Selection

## What Was Added

| Feature | Description |
|---------|-------------|
| `ColorPalette` class | New module in `src/color_palette.py` |
| Header bar | 6 color boxes at top (Purple, Blue, Green, Red, Yellow, Eraser) |
| Gesture selection | Hover with Index+Middle fingers to select color |
| Visual feedback | Selected color highlighted with white border |

---

# Implement Brush Size Controls

## What Was Added

| Feature | Description |
|---------|-------------|
| Keyboard `+`/`-` | Increase/decrease brush size by 5px |
| Size limits | Min: 5px, Max: 50px |
| UI indicator | Shows "Brush: Xpx" with preview circle (top-right) |

## Code Location

| Feature | File | Lines |
|---------|------|-------|
| Constants | `main.py` | 36-38 (`MIN_BRUSH_SIZE`, `MAX_BRUSH_SIZE`, `BRUSH_SIZE_STEP`) |
| UI display | `main.py` | 220-227 |
| Keyboard controls | `main.py` | 260-265 |

## Usage

Press `+` or `=` to increase, `-` to decrease brush thickness while drawing.

---

# Add Eraser Functionality

## What Was Added

| Feature | Description |
|---------|-------------|
| Fist gesture | `[0,0,0,0,0]` (all fingers down) activates eraser |
| Keyboard `e` | Toggle eraser mode on/off |
| Color palette | "Eraser" option in header bar |
| Larger size | Eraser uses 50px thickness |
| UI indicator | Shows "ERASER" text when active |

## Usage

- Press `e` to toggle eraser mode
- Make a fist gesture to temporarily erase
- Select "Eraser" from color palette header

---

# Add Gesture-Based Controls

## Complete Gesture Summary

| Gesture | Finger Pattern | Action |
|---------|----------------|--------|
| 👆 Index up | `[0,1,0,0,0]` | Draw on canvas |
| ✌️ Index + Middle | `[0,1,1,0,0]` | Selection/cursor mode |
| 👌 Thumb + Index | `[1,1,0,0,0]` | Adjust brush size (pinch) |
| 👍 Thumbs up | `[1,0,0,0,0]` | Save indicator |
| 🖐️ Open palm | `[1,1,1,1,1]` | Clear canvas |
| ✊ Fist | `[0,0,0,0,0]` | Eraser mode |
