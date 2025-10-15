from pathlib import Path
import subprocess

def _get_mount_points():
    mounts = []
    try:
        lines = Path("/proc/mounts").read_text().splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                device, mountpoint = parts[0], parts[1]
                if not device.startswith("tmpfs") and not device.startswith("proc") and not device.startswith("sys") and not mountpoint.startswith("/run/user"):
                    mounts.append((device, mountpoint))
    except Exception:
        pass
    return mounts

def _get_disk_usage(path):
    try:
        result = subprocess.run(["df", "-B1", path], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        if len(lines) >= 2:
            parts = lines[1].split()
            total = int(parts[1])
            used = int(parts[2])
            free = int(parts[3])
            percent = parts[4]
            return {
                "total": f"{total / (1024**3):.2f} Go",
                "utilisé": f"{used / (1024**3):.2f} Go",
                "libre": f"{free / (1024**3):.2f} Go",
                "utilisation": percent
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
