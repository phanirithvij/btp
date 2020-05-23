# https://stackoverflow.com/a/4098026/8608146
CREATE_USER_TABLE = """\
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(30) PRIMARY KEY NOT NULL,
    age INTEGER NOT NULL,
    gender BIT DEFAULT 1,
    password VARCHAR(40) NOT NULL
);
"""

MALE = 1
FEMALE = 0

GET_ALL_USERS = """\
SELECT * FROM users;
"""

INSERT_USER = """\
INSERT INTO users (username, age, gender, password) VALUES (?, ?, ?, ?);
"""

# https://stackoverflow.com/a/2128593/8608146
GET_LAST_ID = """\
SELECT last_insert_rowid();
"""

DELETE_USER = """\
DELETE FROM users WHERE username = ?;
"""

GET_USER = """\
SELECT * FROM users WHERE username = ?;
"""
