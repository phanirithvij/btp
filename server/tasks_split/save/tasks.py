from datetime import datetime
from server.db.schema.sentences import CREATE_SENTENCES_TABLE, INSERT_SENTENCE
from pathlib import Path
from timeit import default_timer as timer

from tqdm import tqdm

from server.db import Database
from server.tasks_split import ProgressTask, celery


@celery.task(bind=True, base=ProgressTask)
def split_corpora(
    self,
    file_path: str="",
    split_path: str="",
    langcode: str="",
    filename: str="",
):
    # TODO new database file separate from the main one
    # Also save sentences to db
    DB = Database("data/sentences.db")
    DB.execute(CREATE_SENTENCES_TABLE)
    DB.commit()

    with open(file_path, 'r') as txt:
        print("Starting adding sentences to db")
        linecount = 0
        added_at = str(datetime.now())
        for line in txt.readlines():
            DB.execute(INSERT_SENTENCE, (line.strip(), added_at, langcode, filename))
            linecount += 1
            if linecount%900 == 0:
                # commit every 100 lines
                print("Added", linecount, "sentences")
                DB.commit()
        # commit any remaining line at the end
        DB.commit()
        print("Done Adding", filename, "to DB")
