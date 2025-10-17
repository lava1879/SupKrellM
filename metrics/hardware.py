from pathlib import Path


def _get_thermal_zones():
    temps = {}
    base = Path("/sys/class/thermal")

    if not base.exists():
        return None

    zones = list(base.glob("thermal_zone*"))
    if not zones:
        return None

    for zone in zones:
        try:
            type_file = zone / "type"
            temp_file = zone / "temp"
            name = type_file.read_text().strip() if type_file.exists(
            ) else zone.name

            if temp_file.exists():
                raw = temp_file.read_text().strip()
                temperature = int(raw) / 1000 if raw.isdigit() else raw
                temps[name] = (f"{temperature:.1f} °C" if isinstance(
                    temperature, float) else str(temperature))
            else:
                temps[name] = "Température non disponible"
        except Exception as e:
            temps[zone.name] = f"Erreur de lecture : {e}"

    return temps if temps else None


def _get_power_supply():
    power = {}
    base = Path("/sys/class/power_supply")

    if not base.exists():
        return {"Info": "Aucune information d’alimentation détectée"}

    for supply in base.glob("*"):
        if supply.name.lower().startswith("ac"):
            continue
        try:
            name = supply.name
            status = ((supply / "status").read_text().strip() if
                      (supply / "status").exists() else "Inconnu")
            capacity_path = supply / "capacity"
            capacity = (capacity_path.read_text().strip() +
                        "%" if capacity_path.exists() else "N/A")
            power[name] = f"{status} ({capacity})"
        except Exception as e:
            power[name] = f"Erreur : {e}"

    return power


def get_hardware_info():
    data = {}

    thermal_data = _get_thermal_zones()
    if thermal_data:
        data["Températures"] = thermal_data

    data["Alimentation"] = _get_power_supply()

    return data