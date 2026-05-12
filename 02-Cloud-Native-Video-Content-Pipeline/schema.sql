-- BLC Check Slide Database Schema
CREATE TABLE IF NOT EXISTS slides (
    id TEXT PRIMARY KEY,
    subject TEXT,
    caption TEXT,
    video_url TEXT,
    thumbnail_url TEXT,
    score INTEGER,
    status TEXT DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slide_id TEXT,
    sender TEXT,
    recipient TEXT,
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(slide_id) REFERENCES slides(id)
);
