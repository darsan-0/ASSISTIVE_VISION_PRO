import tkinter as tk
from tkinter import Frame, Label, Button, Canvas
import cv2
from PIL import Image, ImageTk
from detector import detect_objects
from speaker import speak, beep_fast, beep_slow
import time


class AssistiveProUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Assistive Vision PRO")
        self.root.geometry("1200x720")
        self.root.configure(bg="#121212")

        self.cap = None
        self.running = False
        self.last_voice = ""
        self.prev_distances = {}
        self.camera_mode = "shoulder"

        header = Label(root, text="ASSISTIVE VISION PRO",
                       font=("Segoe UI", 22, "bold"),
                       fg="#00FFD1", bg="#121212")
        header.pack(pady=10)

        main = Frame(root, bg="#121212")
        main.pack(fill="both", expand=True)

        self.video_label = Label(main, bg="#1e1e1e")
        self.video_label.pack(side="left", padx=20)

        side = Frame(main, bg="#1e1e1e", width=300)
        side.pack(side="right", fill="y", padx=20)

        self.alert_label = Label(side, text="Idle",
                                 font=("Segoe UI", 14, "bold"),
                                 fg="yellow", bg="#1e1e1e", wraplength=260)
        self.alert_label.pack(pady=10)

        self.radar = Canvas(side, width=250, height=250,
                            bg="#0a0a0a", highlightthickness=0)
        self.radar.pack(pady=20)

        btn = Frame(root, bg="#121212")
        btn.pack(pady=10)

        Button(btn, text="START", command=self.start,
               bg="#00C853", fg="white", width=12).pack(side="left", padx=10)

        Button(btn, text="STOP", command=self.stop,
               bg="#D50000", fg="white", width=12).pack(side="left", padx=10)

        Button(btn, text="EXIT", command=root.quit,
               bg="#424242", fg="white", width=12).pack(side="left", padx=10)

    def start(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        speak("Assistive Vision Pro Activated")
        self.update_frame()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

    # -------- AI SAFE PATH --------
    def get_safe_path(self, detections):
        blocked = {"LEFT": False, "RIGHT": False, "FRONT": False}

        for d in detections:
            if d["distance"] < 3:
                blocked[d["direction"]] = True

        if not blocked["FRONT"]:
            return "Walk straight"
        if not blocked["LEFT"]:
            return "Move left"
        if not blocked["RIGHT"]:
            return "Move right"
        return "Stop"

    # -------- RADAR DRAW --------
    def draw_radar(self, detections):
        self.radar.delete("all")
        cx, cy = 125, 125
        self.radar.create_oval(10, 10, 240, 240, outline="#00FFD1")

        for d in detections:
            dist = d["distance"]
            direction = d["direction"]

            r = max(20, 120 - int(dist * 20))

            if direction == "LEFT":
                x = cx - r
            elif direction == "RIGHT":
                x = cx + r
            else:
                x = cx

            y = cy - r

            self.radar.create_oval(x-5, y-5, x+5, y+5, fill="red")

    # -------- SPEED PREDICTION --------
    def check_speed(self, label, distance):
        if label in self.prev_distances:
            diff = self.prev_distances[label] - distance
            self.prev_distances[label] = distance
            if diff > 0.5:
                return True
        else:
            self.prev_distances[label] = distance
        return False

    def generate_guidance(self, detections):

        if not detections:
            return "Path clear"

        nearest = min(detections, key=lambda x: x["distance"])
        label = nearest["label"]
        dist = nearest["distance"]
        direction = nearest["direction"]
        steps = nearest["steps"]

        safe_path = self.get_safe_path(detections)

        if self.check_speed(label, dist):
            return f"{label} approaching fast. {safe_path}"

        if dist < 1:
            beep_fast()
            return f"{label} very close. Stop immediately"

        elif dist < 3:
            beep_slow()
            return f"{label} nearby from {direction}. {safe_path}"

        else:
            return f"{label} detected {steps} steps ahead. {safe_path}"

    def update_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                detections = detect_objects(frame)

                for d in detections:
                    x1, y1, x2, y2 = d["box"]
                    cv2.rectangle(frame, (x1, y1), (x2, y2),
                                  (0, 0, 255), 2)
                    cv2.putText(frame,
                                f'{d["label"]} {d["distance"]}m',
                                (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 0, 255),
                                2)

                guidance = self.generate_guidance(detections)
                self.alert_label.config(text=guidance)

                if guidance != self.last_voice:
                    speak(guidance)
                    self.last_voice = guidance

                self.draw_radar(detections)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)

                self.video_label.imgtk = imgtk

                
                self.video_label.configure(image=imgtk)

            self.root.after(10, self.update_frame)


root = tk.Tk()
app = AssistiveProUI(root)
root.mainloop()
