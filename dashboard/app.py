import sqlite3
from flask import Flask, render_template
from config import DB_PATH, DASHBOARD_HOST, DASHBOARD_PORT, DEBUG_MODE

app = Flask(__name__)

# ─── Helper ──────────────────────────────────────────
def query(sql, args=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, args)
    rows = cur.fetchall()
    conn.close()
    return rows

# ─── Routes ──────────────────────────────────────────
@app.route("/")
def index():
    total      = query("SELECT COUNT(*) as c FROM events")[0]["c"]
    ssh_count  = query("SELECT COUNT(*) as c FROM events WHERE event_type='SSH'")[0]["c"]
    http_count = query("SELECT COUNT(*) as c FROM events WHERE event_type='HTTP'")[0]["c"]
    scan_count = query("SELECT COUNT(*) as c FROM events WHERE event_type LIKE 'SCAN%'")[0]["c"]

    top_ips = query("""
        SELECT ip, COUNT(*) as cnt
        FROM events
        GROUP BY ip
        ORDER BY cnt DESC
        LIMIT 10
    """)

    top_passwords = query("""
        SELECT password, COUNT(*) as cnt
        FROM events
        WHERE password IS NOT NULL
        GROUP BY password
        ORDER BY cnt DESC
        LIMIT 10
    """)

    top_countries = query("""
        SELECT country, COUNT(*) as cnt
        FROM events
        WHERE country IS NOT NULL
        GROUP BY country
        ORDER BY cnt DESC
        LIMIT 10
    """)

    return render_template("index.html",
        total         = total,
        ssh_count     = ssh_count,
        http_count    = http_count,
        scan_count    = scan_count,
        top_ips       = top_ips,
        top_passwords = top_passwords,
        top_countries = top_countries,
    )

@app.route("/events")
def events():
    rows = query("""
        SELECT * FROM events
        ORDER BY id DESC
        LIMIT 100
    """)
    return render_template("events.html", events=rows)

# ─── Start dashboard ─────────────────────────────────
def start_dashboard():
    app.run(
        host  = DASHBOARD_HOST,
        port  = DASHBOARD_PORT,
        debug = DEBUG_MODE,
        use_reloader = False
        )
