-- schema.sql

-- User credentials, only one row to ensure one person
CREATE TABLE account (
    id INTEGER PRIMARY KEY CHECK (id = 1), 
    utorid TEXT,
    password TEXT          
);

--  Bypass Codes
CREATE TABLE bypass_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL
);

-- Scheduled Activities
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id TEXT NOT NULL,
    scheduled_time DATETIME NOT NULL,
    status TEXT DEFAULT 'scheduled'          
);