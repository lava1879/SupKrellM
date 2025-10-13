import sys
import argparse
from pathlib import Path

from report.generator import generate_html_report
from gui.dashboard import launch_gui
from metrics import system, hardware, memory, disk, process, network, webservices


def collect_metrics(selected_metrics):
    all_data = {}

    try:
        if "system" in selected_metrics or "all" in selected_metrics:
            all_data["system"] = system.get_system_info()
    except Exception as e:
        all_data["system"] = {"Erreur": str(e)}

    try:
        if "hardware" in selected_metrics or "all" in selected_metrics:
            all_data["hardware"] = hardware.get_hardware_info()
    except Exception as e:
        all_data["hardware"] = {"Erreur": str(e)}

    try:
        if "memory" in selected_metrics or "all" in selected_metrics:
            all_data["memory"] = memory.get_memory_info()
    except Exception as e:
        all_data["memory"] = {"Erreur": str(e)}

    try:
        if "disk" in selected_metrics or "all" in selected_metrics:
            all_data["disk"] = disk.get_disk_info()
    except Exception as e:
        all_data["disk"] = {"Erreur": str(e)}

    try:
        if "process" in selected_metrics or "all" in selected_metrics:
            all_data["process"] = process.get_process_info()
    except Exception as e:
        all_data["process"] = {"Erreur": str(e)}

    try:
        if "network" in selected_metrics or "all" in selected_metrics:
            all_data["network"] = network.get_network_info()
    except Exception as e:
        all_data["network"] = {"Erreur": str(e)}

    try:
        if "webservices" in selected_metrics or "all" in selected_metrics:
            all_data["webservices"] = webservices.get_web_services_info()
    except Exception as e:
        all_data["webservices"] = {"Erreur": str(e)}

    return all_data


def parse_arguments():
    """Analyse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Générateur de rapport système Linux"
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=["all"],
        help="Liste des métriques à inclure (system, hardware, memory, disk, process, network, webservices ou all).",
    )
    parser.add_argument(
        "--output",
        default="rapport.html",
        help="Nom du fichier HTML de sortie (par défaut : rapport.html)",
    )
    parser.add_argument(
        "--dest",
        default=".",
        help="Dossier de destination (par défaut : répertoire courant)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Lance le mode interface graphique en temps réel",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.gui:
        print("Lancement de l’interface graphique en temps réel...")
        try:
            launch_gui()
        except Exception as e:
            print(f"Erreur lors du lancement de l’interface graphique : {e}")
        return

    print("Génération du rapport HTML...")

    metrics_data = collect_metrics(args.metrics)
    output_path = Path(args.dest) / args.output

    try:
        generate_html_report(metrics_data, output_path)
        print(f"Rapport généré avec succès : {output_path}")
    except Exception as e:
        print(f"Erreur lors de la génération du rapport : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()