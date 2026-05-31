import sqlite3
import logging
import os
from datetime import datetime
from config import DB_PATH, LOG_PATH

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("honeytrap")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            ip        TEXT,
            port      INTEGER,
            username  TEXT,
            password  TEXT,
            path      TEXT,
            country   TEXT,
            city      TEXT,
            isp       TEXT
        )
    """)

    conn.commit()
    conn.close()
    log.info("Database initialized")


def log_event(event_type, ip, port=None, username=None,
              password=None, path=None, country=None,
              city=None, isp=None):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO events
        (timestamp, event_type, ip, port, username, password, path, country, city, isp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, event_type, ip, port, username, password, path, country, city, isp))

    conn.commit()
    conn.close()

    log.info(f"[{event_type}] {ip}:{port} user={username} pass={password} path={path}")
