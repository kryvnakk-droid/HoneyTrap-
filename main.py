import threading
import time
from core.logger import log, init_db
from core.pipe_reader import start_pipe_reader
from servers.ssh_honeypot import start_ssh_honeypot
from servers.http_honeypot import start_http_honeypot
from config import SSH_PORT, HTTP_PORT, DASHBOARD_PORT
from dashboard.app import start_dashboard

# ─── Banner ──────────────────────────────────────────
def print_banner():
    print("""
    ██╗  ██╗ ██████╗ ███╗   ██╗███████╗██╗   ██╗████████╗██████╗  █████╗ ██████╗ 
    ██║  ██║██╔═══██╗████╗  ██║██╔════╝╚██╗ ██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗
    ███████║██║   ██║██╔██╗ ██║█████╗   ╚████╔╝    ██║   ██████╔╝███████║██████╔╝
    ██╔══██║██║   ██║██║╚██╗██║██╔══╝    ╚██╔╝     ██║   ██╔══██╗██╔══██║██╔═══╝ 
    ██║  ██║╚██████╔╝██║ ╚████║███████╗   ██║      ██║   ██║  ██║██║  ██║██║     
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     
    """)
    print(f"  SSH  honeypot  → port {SSH_PORT}")
    print(f"  HTTP honeypot  → port {HTTP_PORT}")
    print(f"  Dashboard      → http://localhost:{DASHBOARD_PORT}")
    print(f"  Press Ctrl+C to stop\n")

# ─── Main ────────────────────────────────────────────
def main():
    print_banner()

    # инициализируем базу данных
    init_db()

    # запускаем все модули в отдельных потоках
    modules = [
        ("SSH honeypot",  start_ssh_honeypot),
        ("HTTP honeypot", start_http_honeypot),
        ("Pipe reader",   start_pipe_reader),
        ("Dashboard",     start_dashboard),
    ]

    for name, func in modules:
        t = threading.Thread(target=func, daemon=True, name=name)
        t.start()
        log.info(f"{name} started")
        time.sleep(0.5)

    # держим главный поток живым
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("HoneyTrap stopped by user")
        print("\n  Goodbye!")

if __name__ == "__main__":
    main()
