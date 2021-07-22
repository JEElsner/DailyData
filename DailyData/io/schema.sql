CREATE TABLE IF NOT EXISTS metadata (version TEXT);
CREATE TABLE IF NOT EXISTS user (username TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS activity (
    name TEXT PRIMARY KEY,
    parent TEXT,
    alias INT,
    FOREIGN KEY (parent) REFERENCES activity (name)
);
CREATE TABLE IF NOT EXISTS timelog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TIMESTAMP NOT NULL,
    timezone_offset FLOAT,
    timezone_name TEXT,
    activity TEXT NOT NULL,
    user TEXT,
    backdated BOOLEAN,
    FOREIGN KEY (user) REFERENCES user (username) FOREIGN KEY (activity) REFERENCES activity (name)
);
ALTER TABLE timelog
ADD device_name TEXT;