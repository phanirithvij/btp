ADMIN_TABLE = "admins"

# https://stackoverflow.com/a/4098026/8608146
CREATE_ADMIN_TABLE = f"""\
CREATE TABLE IF NOT EXISTS {ADMIN_TABLE} (
    username VARCHAR(30) PRIMARY KEY NOT NULL
);
"""

CREATE_ROLES_TABLE = """\
CREATE TABLE IF NOT EXISTS roles (
    role INTEGER NOT NULL,
    name VARCHAR(20) NOT NULL,
    username VARCHAR(30) NOT NULL
);
"""

GET_ALL_ADMINS = f"""\
SELECT * FROM {ADMIN_TABLE};
"""

INSERT_ADMIN_USER = f"""\
INSERT INTO {ADMIN_TABLE} (username) VALUES (?);
"""

DELETE_ADMIN = f"""\
DELETE FROM {ADMIN_TABLE} WHERE username = ?;
"""

GET_ADMIN = f"""\
SELECT * FROM {ADMIN_TABLE} WHERE username = ?;
"""
