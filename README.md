# face-video

ระบบจดจำใบหน้าในไฟล์วิดีโอ โดยใช้ DeepFace และ OpenCV ประมวลผลแบบ Frame by Frame และบันทึกผลลัพธ์เป็นไฟล์วิดีโอใหม่

---

## โครงสร้างโปรเจค

```
face-video/
├── main.py           # โปรแกรมหลัก — อ่านวิดีโอ, detect และ recognize ใบหน้า
├── load_faces.py     # โหลด embedding ของบุคคลที่รู้จักจากฐานข้อมูล
├── setup_db.py       # สร้าง SQLite database และ insert ข้อมูลตัวอย่าง
├── face-video.db     # SQLite database เก็บข้อมูลบุคคล
├── images/           # รูปภาพอ้างอิงของแต่ละบุคคล
│   ├── pasu.jpg
│   ├── siwakorn.jpg
│   ├── elon.jpg
│   └── anutin.jpg
├── videos/
│   ├── test.mp4          # วิดีโอ input (ต้องเตรียมเอง)
│   └── output_video.mp4  # วิดีโอผลลัพธ์ (สร้างอัตโนมัติหลังรัน)
└── pyproject.toml    # dependencies
```

---

## การทำงานของระบบ

```
videos/test.mp4
      │
      ▼
  cap.read()  ← อ่านทีละเฟรม
      │
      ├─ (ทุก 2 เฟรม) ──▶ resize ×0.25 ──▶ DeepFace.represent()
      │                                           │
      │                                    facial_area + embedding
      │                                           │
      │                                     find_match()
      │                                    (Euclidean distance)
      │                                           │
      │                                    label + distance
      │
      ▼
  draw bounding box + ชื่อ + เพศ + dist บน frame
      │
      ├──▶ cv2.imshow()         แสดงผลแบบ real-time
      └──▶ out.write(frame)     บันทึกเป็น output_video.mp4
```

---

## Dependencies

| Package | Version | หน้าที่ |
|---|---|---|
| `opencv-python` | ≥ 4.13 | อ่าน/เขียนวิดีโอ, วาดกรอบใบหน้า |
| `deepface` | ≥ 0.0.100 | detect และ embed ใบหน้าด้วยโมเดล VGG-Face |
| `numpy` | ≥ 2.4 | คำนวณ Euclidean distance |
| `tf-keras` | ≥ 2.21 | backend ของ DeepFace |

ต้องใช้ Python ≥ 3.12

---

## การติดตั้ง

```bash
# ติดตั้ง dependencies ด้วย uv
uv sync
```

---

## การใช้งาน

### 1. สร้างฐานข้อมูล

```bash
uv run python setup_db.py
```

สร้างไฟล์ `face-video.db` พร้อม table `persons` และ insert ข้อมูลตัวอย่าง 4 คน

### 2. เตรียมรูปภาพอ้างอิง

วางรูปภาพใบหน้าของแต่ละคนในโฟลเดอร์ `images/` ชื่อไฟล์ต้องตรงกับ column `image` ในฐานข้อมูล เช่น `pasu.jpg`

### 3. เตรียมวิดีโอ input

วางไฟล์วิดีโอที่ต้องการประมวลผลในโฟลเดอร์ `videos/` โดยใช้ชื่อ `test.mp4`

### 4. รันโปรแกรม

```bash
uv run python main.py
```

- หน้าต่าง **Face Recognition** จะเปิดขึ้นแสดงวิดีโอพร้อมกรอบใบหน้า
- กด `q` เพื่อหยุดก่อนวิดีโอจบ
- ผลลัพธ์ถูกบันทึกไว้ที่ `videos/output_video.mp4`

---

## ฐานข้อมูล (SQLite)

**Table: `persons`**

| Column | Type | คำอธิบาย |
|---|---|---|
| `id` | INTEGER | Primary key (auto increment) |
| `name` | TEXT | ชื่อภาษาอังกฤษ |
| `surname` | TEXT | นามสกุล |
| `gender` | TEXT | เพศ |
| `image` | TEXT | ชื่อไฟล์รูปภาพใน `images/` |

ข้อมูลตัวอย่างที่ insert ไว้:

| name | surname | gender | image |
|---|---|---|---|
| Pasu | Nimsuwan | Male | pasu.jpg |
| Siwakorn | Banluesapy | Male | siwakorn.jpg |
| Elon | Musk | Male | elon.jpg |
| Anutin | Error | Male | anutin.jpg |

---

## การเพิ่มบุคคลใหม่

1. เพิ่มรูปภาพใบหน้าลงใน `images/` เช่น `newperson.jpg`
2. Insert ข้อมูลลงฐานข้อมูล:

```python
import sqlite3
conn = sqlite3.connect("face-video.db")
conn.execute("INSERT INTO persons (name, surname, gender, image) VALUES (?, ?, ?, ?)",
             ("Name", "Surname", "Male", "newperson.jpg"))
conn.commit()
conn.close()
```

---

## พารามิเตอร์ที่ปรับได้

| ตัวแปร | ค่าปัจจุบัน | ผล |
|---|---|---|
| `THRESHOLD` | `300` | ระยะห่างสูงสุดที่ถือว่า "รู้จัก" — ลดลงถ้าต้องการความแม่นยำสูงขึ้น |
| `SCALE` | `0.25` | ย่อขนาดเฟรมก่อน detect — ลดลงเพื่อความเร็ว, เพิ่มขึ้นเพื่อความแม่นยำ |

---

## การแสดงผลบนวิดีโอ

- **กรอบสีเขียว** — ตรวจพบและจดจำใบหน้าได้
- **กรอบสีแดง** — ตรวจพบใบหน้าแต่ไม่รู้จัก (UNKNOWN)
- แถบด้านล่างกรอบแสดง: `ชื่อ นามสกุล` และ `เพศ  dist:ค่าระยะห่าง`

---

## Output ใน Terminal

ระหว่างรันจะพิมพ์ระยะห่างระหว่าง embedding ของใบหน้าที่ detect ได้กับทุกคนในฐานข้อมูล:

```
  dist to Pasu Nimsuwan: 0.3102
  dist to Elon Musk: 0.8234
  dist to Siwakorn Banluesapy: 0.9541
  dist to Anutin Error: 1.0231
  => best match: Pasu Nimsuwan (dist=0.3102, threshold=300)
```

---

## License

MIT License — Copyright (c) 2026 **Pasu Nimsuwan**

See [LICENSE](LICENSE) for full details.
