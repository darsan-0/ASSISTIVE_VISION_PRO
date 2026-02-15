
import tkinter as tk
from tkinter import Frame, Label, Button
import cv2
from PIL import Image, ImageTk
from detector import detect_objects
from speaker import speak, beep_fast, beep_slow
import time


class AssistiveProUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Assistive Vision PRO")
        self.root.geometry("1100x700")
        self.root.configure(bg="#121212")

        self.cap = None
        self.running = False
        self.last_alert = None
        self.prev_time = 0

        header = Label(root,
                       text="ASSISTIVE VISION PRO",
                       font=("Segoe UI", 22, "bold"),
                       fg="#00FFD1",
                       bg="#121212")
        header.pack(pady=10)

        main_frame = Frame(root, bg="#121212")
        main_frame.pack(fill="both", expand=True)

        self.camera_frame = Frame(main_frame,
                                  bg="#1e1e1e",
                                  bd=2,
                                  relief="ridge")
        self.camera_frame.pack(side="left",
                               padx=20,
                               pady=10)

        self.video_label = Label(self.camera_frame, bg="#1e1e1e")
        self.video_label.pack()

        self.side_panel = Frame(main_frame,
                                bg="#1e1e1e",
                                width=300)
        self.side_panel.pack(side="right",
                             fill="y",
                             padx=20,
                             pady=10)

        Label(self.side_panel,
              text="SYSTEM STATUS",
              font=("Segoe UI", 14, "bold"),
              fg="white",
              bg="#1e1e1e").pack(pady=10)

        self.alert_label = Label(self.side_panel,
                                 text="Idle",
                                 font=("Segoe UI", 16, "bold"),
                                 fg="yellow",
                                 bg="#1e1e1e")
        self.alert_label.pack(pady=10)

        self.distance_label = Label(self.side_panel,
                                    text="Distance: --",
                                    font=("Segoe UI", 13),
                                    fg="#00BFFF",
                                    bg="#1e1e1e")
        self.distance_label.pack(pady=5)

        self.fps_label = Label(self.side_panel,
                               text="FPS: --",
                               font=("Segoe UI", 13),
                               fg="#AAAAAA",
                               bg="#1e1e1e")
        self.fps_label.pack(pady=5)

        button_frame = Frame(root, bg="#121212")
        button_frame.pack(pady=10)

        Button(button_frame,
               text="START",
               command=self.start,
               bg="#00C853",
               fg="white",
               width=12,
               font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)

        Button(button_frame,
               text="STOP",
               command=self.stop,
               bg="#D50000",
               fg="white",
               width=12,
               font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)

        Button(button_frame,
               text="EXIT",
               command=root.quit,
               bg="#424242",
               fg="white",
               width=12,
               font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)

    def start(self):
        if not self.running:
            self.cap = cv2.VideoCapture(0)
            self.running = True
            self.update_frame()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.alert_label.config(text="Stopped", fg="orange")

    def update_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                danger = detect_objects(frame)

                current_time = time.time()
                fps = 1 / (current_time - self.prev_time + 0.0001)
                self.prev_time = current_time
                self.fps_label.config(text=f"FPS: {int(fps)}")

                if danger:
                    label, distance, box = danger
                    x1, y1, x2, y2 = box

                    cv2.rectangle(frame, (x1, y1), (x2, y2),
                                  (0, 0, 255), 2)

                    cv2.putText(frame,
                                f"{label} {distance}m",
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 0, 255),
                                2)

                    self.distance_label.config(
                        text=f"Distance: {distance} m"
                    )

                    if distance < 1:
                        self.alert_label.config(
                            text=f"⚠ VERY CLOSE: {label}",
                            fg="red"
                        )
                        beep_fast()
                        if self.last_alert != "close":
                            speak(f"Warning {label} very close")
                            self.last_alert = "close"

                    elif distance < 3:
                        self.alert_label.config(
                            text=f"Nearby: {label}",
                            fg="orange"
                        )
                        beep_slow()
                        if self.last_alert != "near":
                            speak(f"{label} nearby")
                            self.last_alert = "near"

                    else:
                        self.alert_label.config(
                            text=f"Detected: {label}",
                            fg="yellow"
                        )

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)

                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            self.root.after(10, self.update_frame)


root = tk.Tk()
app = AssistiveProUI(root)
root.mainloop()
