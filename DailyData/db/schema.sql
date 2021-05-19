DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS activity;
DROP TABLE IF EXISTS timelog;
CREATE TABLE user (username TEXT PRIMARY KEY);
CREATE TABLE activity (
    name TEXT PRIMARY KEY,
    parent TEXT,
    alias INT,
    FOREIGN KEY (parent) REFERENCES activity (name)
);
CREATE TABLE timelog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time FLOAT NOT NULL,
    utc_offset INTEGER,
    activity TEXT NOT NULL,
    user INTEGER NOT NULL,
    FOREIGN KEY (user) REFERENCES user (username) FOREIGN KEY (activity) REFERENCES activity (name)
);