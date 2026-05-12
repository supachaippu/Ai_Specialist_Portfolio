
CREATE TABLE IF NOT EXISTS user_profiles (
    uid TEXT PRIMARY KEY,
    phone TEXT,
    name TEXT,
    points INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS point_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    amount INTEGER,
    action TEXT,
    staff_uid TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staff_access (
    uid TEXT PRIMARY KEY,
    name TEXT,
    role TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    amount INTEGER,
    owner_phone TEXT,
    owner_uid TEXT,
    image_key TEXT,
    status TEXT,
    staff_uid TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    withdrawn_at DATETIME,
    withdrawn_by TEXT
);
