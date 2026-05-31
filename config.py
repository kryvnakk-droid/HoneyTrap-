import os

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(BASE_DIR, "data", "honeytrap.db")
LOG_PATH    = os.path.join(BASE_DIR, "logs", "honeytrap.log")

SSH_PORT        = 2222
HTTP_PORT       = 8080
DASHBOARD_PORT  = 5000

INTERFACE = "wlp3s0"

GEOIP_API_URL = "http://ip-api.com/json/{ip}"

DASHBOARD_HOST  = "0.0.0.0"
DEBUG_MODE      = False
