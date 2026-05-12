
CREATE TABLE IF NOT EXISTS attendance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_uid TEXT,
    line_name TEXT,
    extracted_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
