import sqlite3


def create_database():
    conn = sqlite3.connect("face-video.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- ชื่อภาษาอังกฤษ
    surname TEXT, -- นามสกุล
    gender TEXT, -- เพศ
    image TEXT -- ชื่อไฟล์รูปภาพอ้างอิง
    )
    """)

    sample_data = [
        ("Anutin", "Error", "Male", "anutin.jpg"),
        ("Siwakorn", "Banluesapy", "Male", "siwakorn.jpg"),
        ("Elon", "Musk", "Male", "elon.jpg"),
        ("Pasu", "Nimsuwan", "Male", "pasu.jpg"),
    ]
    cursor.executemany(
        """
    INSERT OR IGNORE INTO persons
    (name, surname, gender, image)
    VALUES (?, ?, ?, ?)
    """,
        sample_data,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
