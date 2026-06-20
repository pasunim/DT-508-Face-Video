import sqlite3
from deepface import DeepFace
import numpy as np


def load_known_faces():
    encodings = []
    labels = []
    conn = sqlite3.connect("face-video.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, surname, gender, image FROM persons")
    rows = cursor.fetchall()
    conn.close()

    for name, surname, gender, image_file in rows:
        try:
            result = DeepFace.represent(
                img_path=f"images/{image_file}",
                model_name="VGG-Face",
                enforce_detection=False,
            )
            encoding = result[0]["embedding"]
            label = {"name": name, "surname": surname, "gender": gender}
            encodings.append(encoding)
            labels.append(label)
            print(f" โหลดสำเร็จ: {name} {surname}")
        except Exception as e:
            print(f" โหลดไม่ได้: {name} -> {e}")
    return encodings, labels
