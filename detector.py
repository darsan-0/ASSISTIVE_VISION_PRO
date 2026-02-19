from ultralytics import YOLO

model = YOLO("yolov8n.pt")

DANGER_CLASSES = ["person", "car", "motorbike", "bus", "truck"]

REAL_WIDTHS = {
    "person": 0.5,
    "car": 1.8,
    "motorbike": 0.8,
    "bus": 2.5,
    "truck": 2.5
}

FOCAL_LENGTH = 600
STEP_SIZE_METERS = 0.6


def estimate_distance(pixel_width, real_width):
    if pixel_width == 0:
        return None
    return (real_width * FOCAL_LENGTH) / pixel_width


def get_direction(center_x, frame_width):
    if center_x < frame_width / 3:
        return "LEFT"
    elif center_x > frame_width * 2 / 3:
        return "RIGHT"
    else:
        return "FRONT"


def estimate_steps(distance):
    if distance is None:
        return 0
    return int(distance / STEP_SIZE_METERS)


def detect_objects(frame):
    results = model(frame)[0]
    detections = []

    h, w, _ = frame.shape

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        if label in DANGER_CLASSES:
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            pixel_width = x2 - x1
            real_width = REAL_WIDTHS.get(label, 1.0)
            distance = estimate_distance(pixel_width, real_width)

            if distance:
                center_x = (x1 + x2) // 2
                direction = get_direction(center_x, w)
                steps = estimate_steps(distance)

                detections.append({
                    "label": label,
                    "distance": round(distance, 2),
                    "box": (x1, y1, x2, y2),
                    "direction": direction,
                    "steps": steps
                })

    return detections
