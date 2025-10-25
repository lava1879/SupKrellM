from pathlib import Path
import time
import pwd


def _read_cpu_times():
    try:
        line = Path("/proc/stat").read_text().splitlines()[0]
        if line.startswith("cpu "):
            parts = list(map(int, line.split()[1:]))
            user, nice, system = parts[0], parts[1], parts[2]
            total = sum(parts)
            return user + nice + system, total
    except Exception:
        pass
    return 0, 0


def get_cpu_usage(interval=0.5):
    try:
        active1, total1 = _read_cpu_times()
        time.sleep(interval)
        active2, total2 = _read_cpu_times()
        delta_active = active2 - active1
        delta_total = total2 - total1
        usage = (delta_active / delta_total) * 100 if delta_total > 0 else 0
        return round(usage, 1)
    except Exception:
        return None


def get_cpu_info():
    info = {}
    try:
        lines = Path("/proc/cpuinfo").read_text().splitlines()
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                if key.strip() == "model name":
                    info["Modèle"] = value.strip()
                elif key.strip() == "cpu cores":
                    info["Cœurs"] = value.strip()
        info["Utilisation (%)"] = get_cpu_usage()
    except Exception as e:
        info["Erreur"] = str(e)
    return info


def _read_process_stat(pid):
    try:
        stat_path = Path(f"/proc/{pid}/stat")
        if not stat_path.exists():
            return None

        values = stat_path.read_text().split()
        name = Path(f"/proc/{pid}/comm").read_text().strip()
        utime = int(values[13])
        stime = int(values[14])
        rss = int(values[23]) * 4096 / (1024**2)
        rss_str = f"{rss:.2f} Mio"
        uid = Path(f"/proc/{pid}/status").read_text().split("Uid:")[1].split()[0]
        user = pwd.getpwuid(int(uid)).pw_name
        return {
            "PID": pid,
            "Utilisateur": user,
            "Nom": name,
            "Utilisation mémoire": rss_str,
            "CPU": utime + stime,
        }
    except Exception:
        return None


def get_process_list(limit=5):
    processes = []
    for pid_path in Path("/proc").iterdir():
        if pid_path.name.isdigit():
            pinfo = _read_process_stat(pid_path.name)
            if pinfo:
                processes.append(pinfo)

    processes.sort(key=lambda p: p["CPU"], reverse=True)

    result = {}
    for i, proc in enumerate(processes[:limit], 1):
        proc_dict = {}
        for key, value in proc.items():
            if key != "CPU":
                proc_dict[key] = value
        result[f"Processus {i}"] = proc_dict

    return result if result else {"Erreur": "Aucun processus lisible"}
