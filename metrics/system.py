from datetime import datetime
from pathlib import Path

def get_system_info():
    info = {}

    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info["date_heure"] = now
    except Exception as e:
        info["date_heure"] = f"Erreur : {e}"

    try:
        hostname = Path("/proc/sys/kernel/hostname").read_text().strip()
        info["hostname"] = hostname
    except Exception as e:
        info["hostname"] = f"Erreur : {e}"

    try:
        kernel = Path("/proc/version").read_text().strip()
        info["kernel_version"] = kernel
    except Exception as e:
        info["kernel_version"] = f"Erreur : {e}"

    try:
        uptime_data = Path("/proc/uptime").read_text().split()[0]
        total_seconds = float(uptime_data)
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        info["uptime"] = f"{days}j {hours}h {minutes}m"
    except Exception as e:
        info["uptime"] = f"Erreur : {e}"

    return info
