-- StoreFactory Master Schema V91
-- Use this file to initialize a new D1 database for the worker

-- 👤 User Profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    uid TEXT PRIMARY KEY,
    name TEXT,
    phone TEXT,
    points INTEGER DEFAULT 0,
    birthday TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🎒 Staff Access
CREATE TABLE IF NOT EXISTS staff_access (
    uid TEXT PRIMARY KEY,
    name TEXT,
    role TEXT DEFAULT 'staff',
    status TEXT DEFAULT 'pending'
);

-- 🍾 Deposits (Cabinet)
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    amount INTEGER,
    owner_phone TEXT,
    owner_uid TEXT,
    staff_uid TEXT,
    withdrawn_by TEXT,
    withdrawn_at TIMESTAMP,
    image_key TEXT,
    status TEXT DEFAULT 'active',
    expiry_date TEXT,
    deposit_code TEXT,
    depositor_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🎁 Point Logs
CREATE TABLE IF NOT EXISTS point_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    amount INTEGER,
    action TEXT,
    staff_uid TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🎫 Concert Tickets & Event
CREATE TABLE IF NOT EXISTS concert_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT,
    zone TEXT,
    qty INTEGER,
    total INTEGER,
    slip_key TEXT,
    status TEXT DEFAULT 'pending',
    signature TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📅 Bookings
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    date TEXT,
    time TEXT,
    pax INTEGER,
    status TEXT DEFAULT 'pending',
    uid TEXT,
    table_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📅 Closed Dates (NEW FEATURE)
CREATE TABLE IF NOT EXISTS closed_dates (
    date TEXT PRIMARY KEY
);

-- 🎁 Rewards & Redemptions
CREATE TABLE IF NOT EXISTS rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    points INTEGER,
    image_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT,
    reward_id INTEGER,
    reward_name TEXT,
    points INTEGER,
    status TEXT DEFAULT 'unused',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 📊 Stats tracking
CREATE TABLE IF NOT EXISTS stats (
    id TEXT PRIMARY KEY,
    value INTEGER DEFAULT 0
);
