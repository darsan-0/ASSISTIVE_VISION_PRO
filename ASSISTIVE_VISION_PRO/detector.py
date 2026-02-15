
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

DANGER_CLASSES = ["person", "car", "motorbike", "bus", "truck", "cell phone"]

REAL_WIDTHS = {
    "person": 0.5,
    "car": 1.8,
    "motorbike": 0.8,
    "bus": 2.5,
    "truck": 2.5,
    "cell phone": 0.07 
}

FOCAL_LENGTH = 600


def estimate_distance(pixel_width, real_width):
    if pixel_width == 0:
        return None
    return (real_width * FOCAL_LENGTH) / pixel_width


def detect_objects(frame):
    results = model(frame)[0]
    nearest = None
    min_distance = float("inf")

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        if label in DANGER_CLASSES:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            pixel_width = x2 - x1
            real_width = REAL_WIDTHS.get(label, 1.0)

            distance = estimate_distance(pixel_width, real_width)

            if distance and distance < min_distance:
                min_distance = distance
                nearest = (label, round(distance, 2), (x1, y1, x2, y2))

    return nearest
