import cv2
import numpy as np
from deepface import DeepFace
from load_faces import load_known_faces

THRESHOLD = 1  # cosine-normalized Euclidean — ปรับลงถ้ายัง false positive
SCALE = 0.25  # 50% ดีกว่า 25% สำหรับ accuracy

person_face_encodings, person_face_labels = load_known_faces()


def normalize(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def find_match(embedding, encodings, labels):
    if not encodings:
        return {"name": "UNKNOWN", "surname": "", "gender": ""}, 9999.0
    emb = normalize(np.array(embedding))
    min_dist = float("inf")
    match_label = None
    for known_enc, label in zip(encodings, labels):
        dist = np.linalg.norm(emb - normalize(np.array(known_enc)))
        name = f"{label['name']} {label['surname']}".strip()
        print(f"  dist to {name}: {dist:.4f}")
        if dist < min_dist:
            min_dist = dist
            match_label = label
    best_name = f"{match_label['name']} {match_label['surname']}".strip()
    print(f"  => best match: {best_name} (dist={min_dist:.4f}, threshold={THRESHOLD})")
    if min_dist < THRESHOLD:
        return match_label, min_dist
    return {"name": "UNKNOWN", "surname": "", "gender": ""}, min_dist


INPUT_VIDEO = "videos/test.mp4"
# INPUT_VIDEO = "videos/western.mp4"
input_stem = INPUT_VIDEO.rsplit("/", 1)[-1].rsplit(".", 1)[0]

cap = cv2.VideoCapture(INPUT_VIDEO)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(
    f"videos/{input_stem}_output_video.mp4", fourcc, fps, (width, height)
)

process_frame = True
data_locations, data_labels, data_distances = [], [], []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if process_frame:
        resized = cv2.resize(frame, (0, 0), fx=SCALE, fy=SCALE)

        results = DeepFace.represent(
            img_path=resized,
            model_name="VGG-Face",
            enforce_detection=False,
        )

        data_locations, data_labels, data_distances = [], [], []
        for face in results:
            r = face["facial_area"]
            x, y, w, h = r["x"] * 4, r["y"] * 4, r["w"] * 4, r["h"] * 4
            label, dist = find_match(
                face["embedding"], person_face_encodings, person_face_labels
            )
            data_locations.append((x, y, w, h))
            data_labels.append(label)
            data_distances.append(dist)

    process_frame = not process_frame

    for (x, y, w, h), label, dist in zip(data_locations, data_labels, data_distances):
        is_known = label["name"] != "UNKNOWN"
        color = (26, 174, 10) if is_known else (0, 0, 220)

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        cv2.rectangle(frame, (x, y + h - 55), (x + w, y + h), color, cv2.FILLED)

        full_name = f"{label['name']} {label['surname']}".strip()
        cv2.putText(
            frame,
            full_name,
            (x + 6, y + h - 35),
            cv2.FONT_HERSHEY_DUPLEX,
            0.65,
            (255, 255, 255),
            1,
        )

        info = f"{label['gender']}  dist:{dist:.1f}" if is_known else f"dist:{dist:.1f}"
        cv2.putText(
            frame,
            info,
            (x + 6, y + h - 10),
            cv2.FONT_HERSHEY_DUPLEX,
            0.45,
            (255, 255, 255),
            1,
        )

    out.write(frame)
    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
print("เสร็จแล้ว -> output_video.mp4")
