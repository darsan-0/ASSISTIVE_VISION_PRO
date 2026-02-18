---

# 👁️ ASSISTIVE VISION PRO

> 🧠 **AI-Powered Real-Time Assistive Vision System for Visually Impaired Users**
> Built with Computer Vision, Deep Learning, and Intelligent Audio Guidance.

<p align="center">
🚀 Real-Time Detection • 🔊 Smart Voice Guidance • 🧭 AI Safe Path Navigation • 🎯 Accessibility Focused
</p>

---

## 🧩 Project Vision

**ASSISTIVE VISION PRO** is an intelligent assistive technology designed to enhance independence and safety for visually impaired individuals.

Using **YOLOv8 object detection**, the system analyzes live camera feeds, estimates distance, predicts movement risk, and provides **real-time spoken guidance** to help users navigate safely.

This project combines:

* Computer Vision
* Human-Centered AI
* Accessibility Engineering
* Real-Time Processing

---

## ⚡ Key Highlights

✨ AI Safe Path Recommendation
✨ Distance Estimation + Step Prediction
✨ Direction Awareness (LEFT / FRONT / RIGHT)
✨ Radar-Style Visualization System
✨ Voice Feedback + Smart Beep Alerts
✨ Fast Lightweight YOLOv8 Model
✨ Designed for Real-World Assistive Use

---

## 🎥 System Architecture

```
Camera Input
     │
     ▼
YOLOv8 Detection Engine
     │
     ├── Distance Estimation
     ├── Direction Prediction
     ├── Speed Analysis
     │
     ▼
AI Guidance Engine
     │
     ├── Voice Output (TTS)
     ├── Safety Alerts
     └── Radar Visualization
```

---

## 🧠 AI Pipeline Explained

### 1️⃣ Detection Engine

Objects are detected using **YOLOv8 Nano** for real-time performance.

### 2️⃣ Distance Estimation

Approximate distance is calculated using focal length estimation and bounding box width.

### 3️⃣ Direction Analysis

Objects are classified into:

* LEFT
* FRONT
* RIGHT

based on screen position.

### 4️⃣ Smart Guidance System

AI evaluates obstacles and suggests:

✔ Walk straight
✔ Move left/right
✔ Stop immediately

### 5️⃣ Audio Assistance

Text-to-Speech provides real-time feedback while beep alerts warn about nearby danger.

---

## ✨ Features

| Feature                 | Description                         |
| ----------------------- | ----------------------------------- |
| 🧠 AI Detection         | Real-time object recognition        |
| 📏 Distance Awareness   | Calculates estimated meters + steps |
| 🔊 Voice Navigation     | Real-time spoken instructions       |
| 🚨 Danger Alerts        | Fast & slow beep warnings           |
| 📡 Radar UI             | Visual obstacle map                 |
| 🎯 Accessibility Design | Built for assistive use cases       |

---

## 🛠️ Tech Stack

**Language**

* Python 🐍

**AI & Vision**

* Ultralytics YOLOv8
* OpenCV

**Interface**

* Tkinter GUI
* Pillow Imaging

**Audio**

* pyttsx3 (Offline TTS)
* Windows Sound Alerts

---

## 📂 Project Structure

```
ASSISTIVE_VISION_PRO/
├── dashboard.py     # Main UI + AI Guidance
├── detector.py      # Object Detection Engine
├── speaker.py       # Voice + Alert System
├── yolov8n.pt       # AI Model
└── requirements.txt
```

---

## ⚙️ Installation

Clone repository:

```bash
git clone https://github.com/darsan-0/ASSISTIVE_VISION_PRO.git
cd ASSISTIVE_VISION_PRO
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Application

```bash
python dashboard.py
```

Make sure:

✔ Webcam connected
✔ Python 3.9+ installed
✔ Windows OS recommended (for audio alerts)

---

## 🧪 Example AI Guidance Output

```
Person nearby from LEFT. Move right
Car detected 5 steps ahead. Walk straight
Bus very close. Stop immediately
```

---

## 🎯 Real-World Applications

* 👁️ Assistive technology for visually impaired users
* 🧭 Smart wearable research
* 🚶 AI mobility assistance
* 🧪 Computer vision learning projects
* 🤖 Accessibility-focused AI systems

---

## 🚀 Future Roadmap

* 📱 Android Mobile Version
* 🌍 Multi-Language Voice Support
* 🎧 Smart Glasses Integration
* ☁️ Cloud AI Enhancements
* 🧭 Indoor Navigation Intelligence
* 🔋 Edge AI Optimization

---

## 📊 Performance Goals

| Metric           | Target    |
| ---------------- | --------- |
| Detection Speed  | Real-Time |
| Model            | YOLOv8n   |
| CPU Support      | ✅ Yes     |
| GPU Acceleration | Optional  |

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Commit changes
4. Open Pull Request

---

## 📜 License

MIT License — Open source and free to use.

---

## 👨‍💻 Author

**Darsan**
🎓 AIML Engineering Student
🔗 [https://github.com/darsan-0](https://github.com/darsan-0)

---

## ⭐ Support This Project

If this project helped you or inspired you:

⭐ Star the repository
🍴 Fork and build your own AI assistive tools

---


