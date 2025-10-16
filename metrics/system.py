from datetime import datetime
from pathlib import Path

def get_system_info():
    info = {}

    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info["Date et heure"] = now
    except Exception as e:
        info["Date et heure"] = f"Erreur : {e}"

    try:
        hostname = Path("/proc/sys/kernel/hostname").read_text().strip()
        info["Nom d'hôte"] = hostname
    except Exception as e:
        info["Nom d'hôte"] = f"Erreur : {e}"

    try:
        kernel = Path("/proc/version").read_text().strip()
        info["Version du noyau"] = kernel
    except Exception as e:
        info["Version du noyau"] = f"Erreur : {e}"

    try:
        uptime_data = Path("/proc/uptime").read_text().split()[0]
        total_seconds = float(uptime_data)
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        info["Durée de fonctionnement"] = f"{days}j {hours}h {minutes}m"
    except Exception as e:
        info["Durée de fonctionnement"] = f"Erreur : {e}"

    return info
