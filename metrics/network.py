from pathlib import Path

def get_network_info():
    info = {}
    try:
        lines = Path("/proc/net/dev").read_text().splitlines()[2:]
        for line in lines:
            if ":" not in line:
                continue
            iface, data = line.split(":", 1)
            iface = iface.strip()
            fields = data.split()
            rx_bytes = int(fields[0])
            tx_bytes = int(fields[8])
            info[iface] = {
                "Reçus (Mio)": f"{rx_bytes / (1024**2):.2f}",
                "Envoyés (Mio)": f"{tx_bytes / (1024**2):.2f}"
            }
    except Exception as e:
        info["Erreur"] = str(e)
    return info


def get_default_gateway():
    try:
        lines = Path("/proc/net/route").read_text().splitlines()[1:]
        for line in lines:
            parts = line.split()
            if parts[1] == "00000000":
                return parts[0]
    except Exception:
        pass
    return None
