from pathlib import Path

def _get_mount_points():
    mounts = []
    try:
        lines = Path("/proc/mounts").read_text().splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                device, mountpoint = parts[0], parts[1]
                # On ignore les systèmes virtuels type tmpfs, proc, sysfs
                if not device.startswith("tmpfs") and not device.startswith("proc") and not device.startswith("sys"):
                    mounts.append((device, mountpoint))
    except Exception:
        pass
    return mounts

def _get_disk_usage(path):
    try:
        stat = Path(path).statvfs()
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bfree * stat.f_frsize
        used = total - free
        percent = (used / total) * 100 if total > 0 else 0
        return {
            "total": f"{total / (1024**3):.2f} Go",
            "utilisé": f"{used / (1024**3):.2f} Go",
            "libre": f"{free / (1024**3):.2f} Go",
            "utilisation": f"{percent:.1f}%",
        }
    except Exception as e:
        return {"Erreur": str(e)}

def get_disk_info():
    info = {}
    mounts = _get_mount_points()

    if not mounts:
        return {"Erreur": "Aucun point de montage détecté"}

    for device, mountpoint in mounts:
        info[mountpoint] = _get_disk_usage(mountpoint)

    return info
