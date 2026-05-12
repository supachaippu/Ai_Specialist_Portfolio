CREATE TABLE IF NOT EXISTS employees (
    uid TEXT PRIMARY KEY,
    nickname TEXT NOT NULL,
    thai_name TEXT,
    role TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_key TEXT,
    is_suspicious INTEGER DEFAULT 0,
    check_note TEXT,
    FOREIGN KEY(uid) REFERENCES employees(uid)
);