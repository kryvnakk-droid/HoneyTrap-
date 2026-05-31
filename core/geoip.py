import requests
from config import GEOIP_API_URL
from core.logger import log

def get_geo(ip):
    try:
        url = GEOIP_API_URL.format(ip=ip)
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("status") == "success":
            return {
                "country": data.get("country", "Unknown"),
                "city":    data.get("city",    "Unknown"),
                "isp":     data.get("isp",     "Unknown")
            }
        else:
            return {
                "country": "Unknown",
                "city":    "Unknown",
                "isp":     "Unknown"
            }

    except Exception as e:
        log.warning(f"GeoIP lookup failed for {ip}: {e}")
        return {
            "country": "Unknown",
            "city":    "Unknown",
            "isp":     "Unknown"
        }
