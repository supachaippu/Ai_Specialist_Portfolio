CREATE TABLE IF NOT EXISTS staff_access (user_id TEXT PRIMARY KEY, name TEXT, status TEXT DEFAULT 'pending', role TEXT DEFAULT 'staff', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, deposit_code TEXT, staff_name TEXT, item_name TEXT, item_type TEXT, amount TEXT, remarks TEXT, image_key TEXT, status TEXT, expiry_date TEXT, owner_uid TEXT, owner_name TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, staff_name TEXT, details TEXT, image_key TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_deposit_code ON deposits(deposit_code);
CREATE INDEX IF NOT EXISTS idx_owner_uid ON deposits(owner_uid);
CREATE INDEX IF NOT EXISTS idx_status ON deposits(status);