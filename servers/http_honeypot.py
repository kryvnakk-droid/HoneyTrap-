import socket
import threading
from core.logger import log, log_event
from core.geoip import get_geo
from config import HTTP_PORT

# ─── Fake HTTP responses ─────────────────────────────
RESPONSES = {
    "/wp-admin":   "WordPress Login",
    "/phpmyadmin": "phpMyAdmin",
    "/admin":      "Admin Panel",
    "/.env":       "Environment File",
    "/config.php": "Config File",
}

HTML_TEMPLATE = """HTTP/1.1 200 OK\r
Content-Type: text/html\r
\r
<html><body><h1>{title}</h1>
<form method='post'>
Username: <input name='user'><br>
Password: <input name='pass' type='password'><br>
<input type='submit' value='Login'>
</form></body></html>"""

NOT_FOUND = """HTTP/1.1 404 Not Found\r
Content-Type: text/html\r
\r
<html><body><h1>404 Not Found</h1></body></html>"""

# ─── Parse HTTP request ──────────────────────────────
def parse_request(raw):
    try:
        lines  = raw.split("\r\n")
        method, path, _ = lines[0].split(" ")

        headers = {}
        for line in lines[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
                headers[k] = v

        body = raw.split("\r\n\r\n", 1)[-1] if "\r\n\r\n" in raw else ""

        return method, path, headers, body
    except:
        return None, None, {}, ""

# ─── Handle one connection ───────────────────────────
def handle_connection(client_sock, client_addr):
    ip   = client_addr[0]
    port = client_addr[1]

    try:
        raw = client_sock.recv(4096).decode("utf-8", errors="ignore")
        if not raw:
            return

        method, path, headers, body = parse_request(raw)
        if not path:
            return

        log.info(f"HTTP {method} {path} from {ip}")

        geo = get_geo(ip)

        # парсим credentials если POST
        username = None
        password = None
        if method == "POST" and body:
            params = {}
            for pair in body.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = v
            username = params.get("user")
            password = params.get("pass")

        log_event(
            event_type = "HTTP",
            ip         = ip,
            port       = port,
            path       = path,
            username   = username,
            password   = password,
            country    = geo["country"],
            city       = geo["city"],
            isp        = geo["isp"]
        )

        # отвечаем
        if path in RESPONSES:
            response = HTML_TEMPLATE.format(title=RESPONSES[path])
        else:
            response = NOT_FOUND

        client_sock.sendall(response.encode())

    except Exception as e:
        log.warning(f"HTTP handler error {ip}: {e}")
    finally:
        try:
            client_sock.close()
        except:
            pass

# ─── Start HTTP honeypot ─────────────────────────────
def start_http_honeypot():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", HTTP_PORT))
    sock.listen(100)

    log.info(f"HTTP honeypot listening on port {HTTP_PORT}")

    while True:
        try:
            client_sock, client_addr = sock.accept()
            t = threading.Thread(
                target=handle_connection,
                args=(client_sock, client_addr),
                daemon=True
            )
            t.start()
        except Exception as e:
            log.error(f"HTTP accept error: {e}")
