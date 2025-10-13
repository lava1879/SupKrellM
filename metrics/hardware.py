from pathlib import Path

def _get_thermal_zones():
    """Retourne les températures des thermal zones si disponibles."""
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
            name = type_file.read_text().strip() if type_file.exists() else zone.name

            if temp_file.exists():
                raw = temp_file.read_text().strip()
                temperature = int(raw) / 1000 if raw.isdigit() else raw
                temps[name] = f"{temperature:.1f} °C" if isinstance(temperature, float) else str(temperature)
            else:
                temps[name] = "Température non disponible"
        except Exception as e:
            temps[zone.name] = f"Erreur de lecture : {e}"

    return temps if temps else None

def _get_cooling_devices():

    cooling = {}
    base = Path("/sys/class/thermal")

    if not base.exists():
        return {"Erreur": "Répertoire /sys/class/thermal inexistant"}

    devices = list(base.glob("cooling_device*"))
    if not devices:
        return {"Info": "Aucun dispositif de refroidissement détecté"}

    for dev in devices:
        try:
            type_file = dev / "type"
            cur_state_file = dev / "cur_state"
            max_state_file = dev / "max_state"

            type_name = type_file.read_text().strip() if type_file.exists() else dev.name
            cur_state = cur_state_file.read_text().strip() if cur_state_file.exists() else "?"
            max_state = max_state_file.read_text().strip() if max_state_file.exists() else "?"
            cooling[type_name] = f"État {cur_state}/{max_state}"
        except Exception as e:
            cooling[dev.name] = f"Erreur : {e}"

    return cooling

def _get_power_supply():
    """Retourne l’état d’alimentation (batterie, secteur, etc.)"""
    power = {}
    base = Path("/sys/class/power_supply")

    if not base.exists():
        return {"Info": "Aucune information d’alimentation détectée"}

    for supply in base.glob("*"):
        try:
            name = supply.name
            status = (supply / "status").read_text().strip() if (supply / "status").exists() else "Inconnu"
            capacity_path = supply / "capacity"
            capacity = capacity_path.read_text().strip() + "%" if capacity_path.exists() else "N/A"
            power[name] = f"{status} ({capacity})"
        except Exception as e:
            power[name] = f"Erreur : {e}"

    return power

def get_hardware_info():
    """Point d’entrée pour la collecte des infos matérielles."""
    data = {}

    thermal_data = _get_thermal_zones()
    if thermal_data:
        data["Températures"] = thermal_data
    else:
        data["Températures"] = {
            "Info": "Aucune zone thermique détectée, affichage des dispositifs de refroidissement"
        }
        data["Refroidissement"] = _get_cooling_devices()

    data["Alimentation"] = _get_power_supply()

    return data
