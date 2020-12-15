import os
from server.config import Config
import requests
import pickle

def store_session():
    if not Config.USE_CENTRAL_SERVER:
        return
    # get cookie by sending username & pass
    # TODO add a register server page
    # then redirect to the central server register page
    # save those here
    eml = Config.CENTRAL_SERVER_EMAIL
    passw = Config.CENTRAL_SERVER_PASSWORD
    auth = {
       "email" : eml,
       "password" : passw,
    }
    session = requests.Session()
    try:
        r = session.post(Config.CENTRAL_SERVER_TOKEN_URL, json=auth)
        print("[INFO][CENTRAL_SERVER]", r.status_code, r.json())
        with open(Config.SESSION_DUMP_FILE,"wb+") as sessf:
            pickle.dump(session, sessf)
    except Exception as e:
        print("[WARNING] Failed to reach central server")
    return session

def get_session():
    if not Config.USE_CENTRAL_SERVER:
        return None
    info = os.stat(Config.SESSION_DUMP_FILE)
    if os.path.exists(Config.SESSION_DUMP_FILE) and info.st_size > 0:
        with open(Config.SESSION_DUMP_FILE, 'rb') as sessf:
            return pickle.load(sessf)
    else:
        print("[INFO] Session doesn't exist creating")
        return store_session()
