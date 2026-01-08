# 🎨 AI Air Canvas

An AI-powered virtual drawing application that allows you to draw in the air using hand gestures, leveraging computer vision and machine learning.

---

## ✨ Features

- **Hand Gesture Recognition** – Draw in real-time using your fingertip
- **Multiple Colors** – Switch between colors using gestures or on-screen buttons
- **Brush Size Control** – Adjust brush thickness dynamically
- **Eraser Mode** – Erase parts of your drawing with a gesture
- **Clear Canvas** – Reset the canvas with a simple gesture
- **Save Artwork** – Export your drawings as image files

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| **OpenCV** | Video capture and image processing |
| **MediaPipe** | Hand detection and tracking |
| **NumPy** | Array operations for canvas manipulation |

---

## 📁 Project Structure

```
AIR_canvas/
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── main.py                # Main application entry point
├── src/
│   ├── __init__.py
│   ├── hand_detector.py   # Hand detection module using MediaPipe
│   ├── canvas.py          # Canvas drawing logic
│   ├── color_palette.py   # Color selection functionality
│   └── utils.py           # Helper functions
├── assets/
│   └── icons/             # UI icons for color palette
├── output/                # Saved drawings
└── tests/
    └── test_hand_detector.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Webcam

### Step 1: Clone the Repository

```bash
git clone https://github.com/MilanVadhel01/AIR_canvas.git
cd AIR_canvas
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv

.\venv311\Scripts\python.exe main.py (recommended because it can only run on python 3.11)
or
venv\Scripts\activate 

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python main.py
```

---

## 🎮 Gesture Controls

| Gesture | Action |
|---------|--------|
| **Index finger up** | Draw on canvas |
| **Index + Middle finger up** | Move cursor (selection mode) |
| **Thumb + Index up** | Adjust brush size (spread/pinch) |
| **All fingers up (open palm)** | Clear canvas |
| **Fist** | Save drawing |

---

## 📦 Dependencies

Create a `requirements.txt` file with:

```
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
```

---

## 🗓️ Development Roadmap

- [x] Project setup and structure
- [x] Implement hand detection module
- [x] Create canvas drawing logic
- [x] Add color palette selection
- [x] Implement brush size controls
- [x] Add eraser functionality
- [x] Implement save/export feature
- [x] Add gesture-based controls
- [ ] Testing and optimization

---

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) by Google for hand tracking
- [OpenCV](https://opencv.org/) for computer vision capabilities

Input	              Action
👆 Index finger	     Draw
✌️ Index + Middle	Move cursor
� Thumb + Index	Adjust brush size
�🖐️ Open palm	     Clear canvas
q	                Quit
s	                Save drawing
c	                Clear canvas
1-5	                 Change color
+/-	                Brush size
