# ✋ VisionTouch — AI Hand-Gesture Shape Sandbox

Touch-free UI interaction using Python + OpenCV + MediaPipe  
Control shapes in the air — Pinch, Drag, Draw, Zoom!

---

## 🎥 Demo

Gesture-Controlled UI | Pinch-Zoom | Air Drawing | No Mouse, No Touchscreen  
*(Add demo GIF / YouTube link here when ready)*

---

## 🚀 Features

- ✅ Real-time hand tracking  
- ✅ Pinch to select & move shapes  
- ✅ Air-drawing mode (3-second hold countdown)  
- ✅ Two-hand pinch to zoom shapes  
- ✅ Snap to delete (bin area)  
- ✅ Multi-hand support (Left & Right hands)  
- ✅ Buttons to add shapes  
- ✅ Smooth smart UI & feedback  

---

## 🎯 Gestures Guide

| Action        | Gesture                         | Effect               |
|---------------|----------------------------------|----------------------|
| Select shape  | Pinch on shape                   | Locks selection      |
| Move shape    | Hold pinch & move                | Drag in space        |
| Add shape     | Pinch on UI button               | Shape appears        |
| Delete shape  | Drag to bin                      | Removed              |
| Draw mode     | Pinch on Draw icon (3s wait)     | Start drawing        |
| Stop drawing  | Release pinch                    | Ends drawing         |
| Zoom          | Both hands pinch same shape      | Scale size dynamically |

---

## 🧠 Why This Project?

This system simulates a Minority-Report UI for education & experimentation:

- Human-Computer Interaction  
- Computer Vision  
- Gesture UX Research  
- AR/VR Interaction Logic  
- Machine Learning + OpenCV hybrid workflow  

**Use cases:**

- 🖼️ Creative spaces — draw in air  
- 🧪 Research demos  
- 🤖 Robotics gesture control  
- 🎓 College / final-year project  

---

## 📦 Tech Stack

| Library         | Purpose                        |
|-----------------|--------------------------------|
| Python          | Core language                  |
| OpenCV          | Camera feed + rendering        |
| MediaPipe Hands | Hand landmarks detection       |
| Math + Logic    | Gesture recognition            |
| OOP Modules     | Shapes and UI                  |

---

## 📁 Folder Structure
```
📁 VisionTouch/
├── main.py
├── modules/
│   ├── hand_detector.py
│   ├── shape_utils.py
|   ├── draw_utils.py
|   ├── shape_3d.py
└── README.md
```

---

## 🧾 Installation

### ✅ Requirements

- Python 3.8+  
- Webcam  

### 🛠️ Install dependencies

```bash
pip install mediapipe opencv-python
```

### Run
```bash
python main.py
```

---

## 🏗️ Architecture
```
Webcam
  └──> OpenCV Frame
        └──> MediaPipe Hand Tracking
              └──> Gesture Logic
                    ├─ Pinch / Zoom / Move / Draw
                    └──> Shape Manager
                          ├─ UI Buttons
                          ├─ Shapes Array
                          └─ Render Engine
Display <────────────────────────────────────────────┘
```

## 📌 Key Concepts

| Concept           | Explanation                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| Pinch detection   | Measures Euclidean distance between finger tips (landmarks 4 & 8) to detect pinch gesture |
| Zoom              | Calculates dynamic scale ratio using two-hand pinch distances               |
| Drag              | Tracks movement by comparing centroid position across frames                |
| Drawing           | Records sequential fingertip positions while pinch is held, stops on release|
| Delete            | Removes shape when its bounding box overlaps with bin zone                  |

---

## 🎯 Roadmap

| Feature                        | Status   |
|--------------------------------|----------|
| ✅ Pinch, Drag, Draw, Zoom     | Ready    |
| 🚧 Rotate shapes via hand twist| Next     |
| 🚧 Swipe to delete             | Coming   |
| ❌ Voice-Gesture mix           | Future   |
| ❌ Save drawings               | Future   |

---

## 🧪 Viva Interview Points

| Topic              | You say                                      |
|--------------------|----------------------------------------------|
| Why MediaPipe?     | Fast GPU-ready real-time pose detection      |
| Why flip camera?   | Natural mirror interaction                   |
| How zoom works?    | Distance scaling formula                     |
| How pinch detected?| Euclidean distance threshold                |
| Optimizations?     | Lower draw calls, controlled confidence scores|

---

## 🔍 Keywords (for YouTube / SEO)

- Python gesture control  
- OpenCV hand tracking project  
- MediaPipe pinch zoom Python  
- Touchless UI demo  
- AI Computer Vision college project  
- Air drawing OpenCV  
- Minority Report UI Python  

---

## 🙌 Credits & License

- **MIT License** — Free to use / modify  
- **MediaPipe by Google**  
- **Computer Vision community ❤️**

---

## ⭐ Support

Star the repo if you like it 🌟  
Have ideas? Want AR version? DM me — let's build more!

---

## 🎁 Bonus Outputs Available

Reply with a number to generate:

1️⃣ Project poster image  
2️⃣ Portfolio description text  
3️⃣ LinkedIn announcement post  
4️⃣ Video voice-over script  
5️⃣ Final-year project IEEE report draft  
6️⃣ Unity version for AR/VR  
7️⃣ Rotation gesture update code