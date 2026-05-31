import socket
import threading
import paramiko
from core.logger import log, log_event
from core.geoip import get_geo
from config import SSH_PORT

# ─── Fake SSH server interface ───────────────────────
class FakeSSHServer(paramiko.ServerInterface):

    def check_auth_password(self, username, password):
        # логируем но никогда не пускаем
        log.info(f"SSH auth attempt: {username}:{password}")
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password"

# ─── Handle one connection ───────────────────────────
def handle_connection(client_sock, client_addr):
    ip   = client_addr[0]
    port = client_addr[1]

    log.info(f"SSH connection from {ip}:{port}")

    try:
        transport = paramiko.Transport(client_sock)
        transport.local_version = "SSH-2.0-OpenSSH_8.9p1"  # притворяемся реальным SSH

        host_key = paramiko.RSAKey.generate(2048)
        transport.add_server_key(host_key)

        server = FakeSSHServer()

        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            return

        chan = transport.accept(30)

        # получаем credentials из transport
        username = getattr(server, "_username", None)
        password = getattr(server, "_password", None)

        geo = get_geo(ip)

        log_event(
            event_type = "SSH",
            ip         = ip,
            port       = port,
            username   = username,
            password   = password,
            country    = geo["country"],
            city       = geo["city"],
            isp        = geo["isp"]
        )

    except Exception as e:
        log.warning(f"SSH handler error {ip}: {e}")
    finally:
        try:
            client_sock.close()
        except:
            pass

# ─── Start SSH honeypot ──────────────────────────────
def start_ssh_honeypot():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", SSH_PORT))
    sock.listen(100)

    log.info(f"SSH honeypot listening on port {SSH_PORT}")

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
            log.error(f"SSH accept error: {e}")
