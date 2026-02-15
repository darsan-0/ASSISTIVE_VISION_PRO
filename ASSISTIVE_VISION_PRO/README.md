
ASSISTIVE VISION PRO - Laptop Version

===============================
HOW TO RUN
===============================

1. Install Python 3.8 - 3.10 (Recommended: Python 3.10)

2. Open terminal inside this folder.

3. Install dependencies:

   pip install ultralytics opencv-python pyttsx3 pillow numpy

4. Run the application:

   python dashboard.py

First run will automatically download YOLO model (approx 6MB).

Press START to begin detection.

Press STOP to stop camera.

===============================
HOW TO HOST / DEPLOY
===============================

This is a local desktop AI application.

OPTION 1: Run locally
Just execute: python dashboard.py

OPTION 2: Convert to EXE (Windows)

Install PyInstaller:

   pip install pyinstaller

Then run:

   pyinstaller --onefile --windowed dashboard.py

Your .exe file will appear inside the 'dist' folder.

You can now distribute the EXE as a desktop application.

===============================
SYSTEM REQUIREMENTS
===============================

- Windows 10/11
- Webcam
- 8GB RAM recommended
- Python 3.8–3.10

===============================
FEATURES
===============================

- YOLOv8 real-time object detection
- Distance estimation
- Nearest danger alert
- Voice alerts
- Beep vibration simulation
- Professional dashboard UI

