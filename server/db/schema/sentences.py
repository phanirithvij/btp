SENTENCES_TABLE = "sentences"

# https://stackoverflow.com/a/4098026/8608146
# https://stackoverflow.com/questions/7905859/is-there-an-auto-increment-in-sqlite#comment104307818_7905936
CREATE_SENTENCES_TABLE = f"""\
CREATE TABLE IF NOT EXISTS {SENTENCES_TABLE} (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    sentence TEXT,
    added_at TEXT,
    langCat     VARCHAR(30),
    dataset_name VARCHAR(30)
);
"""


GET_ALL_SENTENCES_BY_DATASET = f"""\
SELECT * FROM {SENTENCES_TABLE} WHERE langCat = ? AND dataset_name = ?;
"""


GET_STARTING_INDEX_SENTENCES_BY_DATASET = f"""\
SELECT id FROM {SENTENCES_TABLE} WHERE langCat = ? AND dataset_name = ? ORDER BY id LIMIT 1;
"""


GET_RANDOM_CORPA_AFTER = f"""\
SELECT sentence, id FROM {SENTENCES_TABLE} WHERE langCat = ? AND dataset_name = ? AND id > ? LIMIT ?;
"""

GET_TOTAL_CORPA_LEN_FORDB = f"""\
SELECT COUNT(*) FROM {SENTENCES_TABLE} WHERE langCat = ? AND dataset_name = ?;
"""

INSERT_SENTENCE = f"""\
INSERT INTO {SENTENCES_TABLE} (sentence, added_at, langCat, dataset_name) VALUES (?,?,?,?);
"""

DELETE_SENTENCE = f"""\
DELETE FROM {SENTENCES_TABLE} WHERE id = ?;
"""

GET_SENTENCE = f"""\
SELECT * FROM {SENTENCES_TABLE} WHERE id = ?;
"""
