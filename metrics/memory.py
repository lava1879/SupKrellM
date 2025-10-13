from pathlib import Path

def _parse_meminfo():
    meminfo = {}
    path = Path("/proc/meminfo")

    if not path.exists():
        return {"Erreur": "/proc/meminfo introuvable"}

    try:
        for line in path.read_text().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meminfo[key.strip()] = value.strip()
    except Exception as e:
        return {"Erreur": f"Impossible de lire /proc/meminfo : {e}"}

    return meminfo

def _to_mib(value_kb):
    try:
        return round(int(value_kb) / 1024, 2)
    except Exception:
        return 0.0

def get_memory_info():
    meminfo = _parse_meminfo()

    if "Erreur" in meminfo:
        return meminfo

    try:
        total = _to_mib(meminfo.get("MemTotal", "0 kB").split()[0])
        free = _to_mib(meminfo.get("MemFree", "0 kB").split()[0])
        available = _to_mib(meminfo.get("MemAvailable", "0 kB").split()[0])
        used = total - available
        used_percent = round((used / total) * 100, 1) if total > 0 else 0

        swap_total = _to_mib(meminfo.get("SwapTotal", "0 kB").split()[0])
        swap_free = _to_mib(meminfo.get("SwapFree", "0 kB").split()[0])
        swap_used = swap_total - swap_free
        swap_percent = round((swap_used / swap_total) * 100, 1) if swap_total > 0 else 0

        return {
            "Mémoire totale": f"{total} MiB",
            "Mémoire utilisée": f"{used} MiB ({used_percent}%)",
            "Mémoire libre": f"{free} MiB",
            "Mémoire disponible": f"{available} MiB",
            "Swap total": f"{swap_total} MiB",
            "Swap utilisé": f"{swap_used} MiB ({swap_percent}%)",
            "Swap libre": f"{swap_free} MiB",
        }
    except Exception as e:
        return {"Erreur": f"Échec du calcul de la mémoire : {e}"}
