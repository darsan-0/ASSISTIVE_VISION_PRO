"""
Assistive Vision PRO — Dashboard Backend
=========================================
Architecture:
  - Flask + Flask-SocketIO serve the HTML UI and relay live data
  - OpenCV camera loop runs in a background thread
  - Frames are JPEG-encoded and emitted as base64 over SocketIO
  - Detection data (objects, guidance, status) emitted as JSON
  - VoiceCommandListener listens for spoken commands (start/stop/front/left/right…)
  - speaker.py handles all TTS / beep calls (Windows SAPI5)
  - pywebview opens the HTML UI in a native desktop window

Run:  python dashboard.py
"""

import base64
import threading
import time
import os

import cv2
from flask import Flask, send_from_directory
from flask_socketio import SocketIO

from detector import detect_objects
from speaker import speak, beep_fast, beep_slow
from voice_commands import VoiceCommandListener, HELP_TEXT, SR_AVAILABLE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR)
app.config["SECRET_KEY"] = "assistive-vision-pro"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

state = {
    "running":          False,
    "audio_on":         True,
    "sensitivity":      0.5,
    "voice_rate":       160,
    "mode":             "outdoor",
    "language":         "en",
    "beep_on":          True,
    "cap":              None,
    "last_voice":       "",
    "last_guidance":    "System idle.",
    "last_detections":  [],
    "prev_distances":   {},
    "last_spoken_time": 0,
}

lock = threading.Lock()

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "ui.html")

@socketio.on("start")
def handle_start():
    _start_detection()

@socketio.on("stop")
def handle_stop():
    _stop_detection()

@socketio.on("settings")
def handle_settings(data):
    with lock:
        if "sensitivity" in data:
            state["sensitivity"] = float(data["sensitivity"]) / 100.0
        if "voice_rate" in data:
            rate = int(float(data["voice_rate"]) * 160)
            state["voice_rate"] = rate
            try:
                from speaker import set_rate
                set_rate(rate)
            except Exception:
                pass
        if "audio_on"  in data: state["audio_on"]  = bool(data["audio_on"])
        if "beep_on"   in data: state["beep_on"]   = bool(data["beep_on"])
        if "mode"      in data: state["mode"]       = data["mode"]
        if "language"  in data: state["language"]   = data["language"]

def _start_detection():
    with lock:
        if state["running"]:
            return
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            socketio.emit("error", {"msg": "Camera not found"})
            _speak_safe("Camera not found. Please connect a camera.")
            return
        state["cap"]            = cap
        state["running"]        = True
        state["prev_distances"] = {}
        state["last_voice"]     = ""
    socketio.emit("status_update", {"running": True})
    socketio.emit("voice_command_event", {"action": "start", "text": "Detection started"})
    _speak_safe("Assistive Vision Pro activated. Detection started.")

def _stop_detection():
    with lock:
        state["running"] = False
        if state["cap"]:
            state["cap"].release()
            state["cap"] = None
    socketio.emit("status_update", {"running": False})
    socketio.emit("guidance_update", {"text": "Detection stopped.", "status": "idle", "detections": [], "nearest_dist": None})
    socketio.emit("voice_command_event", {"action": "stop", "text": "Detection stopped"})
    _speak_safe("Detection stopped.")

def _describe_direction(direction):
    with lock:
        detections = state["last_detections"]
    if not detections:
        msg = "No objects detected."
    else:
        filtered = [d for d in detections if d["direction"] == direction.upper()]
        if not filtered:
            msg = f"Nothing detected on the {direction}."
        else:
            parts = [f"{d['label']} at {d['distance']} meters" for d in filtered]
            msg = f"On the {direction}: " + ", ".join(parts) + "."
    _speak_safe(msg, cooldown=0)
    socketio.emit("voice_command_event", {"action": direction, "text": msg})

def _full_status():
    with lock:
        detections = state["last_detections"]
        guidance   = state["last_guidance"]
    if not detections:
        msg = "Path is clear. No obstacles detected."
    else:
        parts = [f"{d['label']} {d['distance']} meters on the {d['direction']}" for d in detections]
        msg = f"I see: {', '.join(parts)}. {guidance}"
    _speak_safe(msg, cooldown=0)
    socketio.emit("voice_command_event", {"action": "status", "text": msg})

def on_voice_command(action, raw_text):
    print(f"[VoiceCmd] Action: {action}  |  Heard: '{raw_text}'")
    socketio.emit("voice_command_event", {"action": action, "text": raw_text})
    if   action == "start":  _start_detection()
    elif action == "stop":   _stop_detection()
    elif action == "front":  _describe_direction("FRONT")
    elif action == "back":   _describe_direction("BACK")
    elif action == "left":   _describe_direction("LEFT")
    elif action == "right":  _describe_direction("RIGHT")
    elif action == "status": _full_status()
    elif action == "repeat":
        with lock:
            msg = state["last_guidance"]
        _speak_safe(msg, cooldown=0)
        socketio.emit("voice_command_event", {"action": "repeat", "text": msg})
    elif action == "mute":
        with lock:
            state["audio_on"] = False
        socketio.emit("settings_update", {"audio_on": False})
        speak("Voice muted.", cooldown=0)
    elif action == "unmute":
        with lock:
            state["audio_on"] = True
        socketio.emit("settings_update", {"audio_on": True})
        speak("Voice unmuted.", cooldown=0)
    elif action == "help":
        _speak_safe(HELP_TEXT, cooldown=0)
        socketio.emit("voice_command_event", {"action": "help", "text": HELP_TEXT})
    elif action == "exit":
        _speak_safe("Closing Assistive Vision Pro. Goodbye.", cooldown=0)
        time.sleep(2)
        os._exit(0)

def on_listening_state(is_listening):
    socketio.emit("mic_state", {"listening": is_listening})

def _speak_safe(text, cooldown=2):
    if not state["audio_on"]:
        return
    now = time.time()
    if cooldown > 0 and now - state["last_spoken_time"] < cooldown:
        return
    state["last_spoken_time"] = now
    try:
        speak(text, cooldown=0)
    except Exception as e:
        print("TTS error:", e)

def get_safe_path(detections):
    blocked = {"LEFT": False, "RIGHT": False, "FRONT": False}
    for d in detections:
        if d["distance"] < 3:
            blocked[d["direction"]] = True
    if not blocked["FRONT"]:  return "Walk straight"
    if not blocked["LEFT"]:   return "Move left"
    if not blocked["RIGHT"]:  return "Move right"
    return "Stop"

def check_speed(label, distance):
    prev = state["prev_distances"]
    if label in prev:
        diff = prev[label] - distance
        prev[label] = distance
        return diff > 0.5
    prev[label] = distance
    return False

def generate_guidance(detections):
    if not detections:
        return "Path clear", "safe"
    nearest   = min(detections, key=lambda x: x["distance"])
    label     = nearest["label"]
    dist      = nearest["distance"]
    direction = nearest["direction"]
    steps     = nearest["steps"]
    safe_path = get_safe_path(detections)
    if check_speed(label, dist):
        return f"{label} approaching fast. {safe_path}", "danger"
    if dist < 1:
        if state["beep_on"]:
            threading.Thread(target=beep_fast, daemon=True).start()
        return f"{label} very close. Stop immediately", "danger"
    elif dist < 3:
        if state["beep_on"]:
            threading.Thread(target=beep_slow, daemon=True).start()
        return f"{label} nearby from {direction}. {safe_path}", "warn"
    else:
        return f"{label} detected {steps} steps ahead. {safe_path}", "safe"

FRAME_INTERVAL = 1 / 24
ICONS = {"person": "👤", "car": "🚗", "motorbike": "🏍️", "bus": "🚌", "truck": "🚛"}
STATUS_ICON   = {"safe": "✅", "warn": "⚠️", "danger": "🚨", "idle": "💤"}
STATUS_COLORS = {"danger": (60, 56, 255), "warn": (0, 184, 255), "safe": (160, 240, 0)}

def camera_loop():
    while True:
        time.sleep(FRAME_INTERVAL)
        with lock:
            if not state["running"] or state["cap"] is None:
                continue
            cap = state["cap"]
        ret, frame = cap.read()
        if not ret:
            socketio.emit("error", {"msg": "Camera read failed"})
            with lock:
                state["running"] = False
            continue
        try:
            detections = detect_objects(frame)
        except Exception as e:
            print("Detection error:", e)
            detections = []
        guidance, status = generate_guidance(detections)
        with lock:
            state["last_guidance"]   = guidance
            state["last_detections"] = detections
        for d in detections:
            x1, y1, x2, y2 = d["box"]
            dist       = d["distance"]
            obj_status = "danger" if dist < 1 else ("warn" if dist < 3 else "safe")
            color      = STATUS_COLORS[obj_status]
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            tag = f'{d["label"]}  {d["distance"]}m  {d["direction"]}'
            (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
            cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 8, y1), color, -1)
            cv2.putText(frame, tag, (x1 + 4, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 1, cv2.LINE_AA)
        _, buf    = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 72])
        frame_b64 = base64.b64encode(buf).decode("utf-8")
        det_cards = []
        for d in detections:
            dist       = d["distance"]
            obj_status = "danger" if dist < 1 else ("warn" if dist < 3 else "safe")
            det_cards.append({"label": d["label"], "icon": ICONS.get(d["label"], "⬜"), "distance": d["distance"], "direction": d["direction"], "steps": d["steps"], "status": obj_status})
        nearest_dist = min((d["distance"] for d in detections), default=None)
        socketio.emit("frame", {"img": frame_b64})
        socketio.emit("guidance_update", {"text": f"{STATUS_ICON.get(status, '')} {guidance}", "status": status, "detections": det_cards, "nearest_dist": nearest_dist})
        if guidance != state["last_voice"]:
            state["last_voice"] = guidance
            threading.Thread(target=_speak_safe, args=(guidance,), daemon=True).start()

def main():
    PORT = 5050
    threading.Thread(target=camera_loop, daemon=True).start()
    if SR_AVAILABLE:
        vc = VoiceCommandListener(on_command=on_voice_command, on_listening=on_listening_state, language="en-US")
        vc.start()
        print("[VoiceCmd] Voice commands ACTIVE — speak: start, stop, front, left, right, status, repeat, mute, help, exit")
    else:
        print("[VoiceCmd] DISABLED — run: pip install SpeechRecognition pyaudio")
    try:
        import webview
        def start_server():
            socketio.run(app, host="127.0.0.1", port=PORT, use_reloader=False, log_output=False)
        threading.Thread(target=start_server, daemon=True).start()
        time.sleep(1.2)
        webview.create_window("Assistive Vision PRO", f"http://127.0.0.1:{PORT}", width=1280, height=760, resizable=True, min_size=(900, 600))
        webview.start()
    except ImportError:
        print(f"\n[INFO] Opening in browser → http://127.0.0.1:{PORT}\n")
        import webbrowser
        threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
        socketio.run(app, host="127.0.0.1", port=PORT, use_reloader=False)

if __name__ == "__main__":
    main()
