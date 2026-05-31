import subprocess
import threading
from core.logger import log, log_event
from core.geoip import get_geo
from config import INTERFACE

# ─── Parse one line from sniffer ────────────────────
def parse_line(line):
    # формат: timestamp | src_ip | dst_ip | proto | port | flags
    try:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            return None

        return {
            "timestamp": parts[0],
            "src_ip":    parts[1],
            "dst_ip":    parts[2],
            "proto":     parts[3],
            "port":      int(parts[4]) if parts[4].isdigit() else None,
            "flags":     parts[5]
        }
    except Exception:
        return None

# ─── Process parsed packet ───────────────────────────
def process_packet(packet):
    if not packet:
        return

    ip    = packet["src_ip"]
    port  = packet["port"]
    proto = packet["proto"]
    flags = packet["flags"]

    # логируем только SYN — это новые подключения
    if "SYN" not in flags:
        return

    # пропускаем локальные адреса
    if ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10."):
        return

    geo = get_geo(ip)

    log_event(
        event_type = f"SCAN_{proto}",
        ip         = ip,
        port       = port,
        country    = geo["country"],
        city       = geo["city"],
        isp        = geo["isp"]
    )

    log.info(f"SCAN {proto} from {ip}:{port} [{geo['country']}]")

# ─── Read sniffer output in background ───────────────
def start_pipe_reader():
    def run():
        try:
            proc = subprocess.Popen(
                ["./cpp/sniffer"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            log.info("Pipe reader connected to sniffer")

            for line in proc.stdout:
                line = line.strip()
                if line:
                    packet = parse_line(line)
                    process_packet(packet)

        except FileNotFoundError:
            log.error("sniffer binary not found — run: g++ -o cpp/sniffer cpp/sniffer.cpp")
        except Exception as e:
            log.error(f"Pipe reader error: {e}")

    t = threading.Thread(target=run, daemon=True)
    t.start()
