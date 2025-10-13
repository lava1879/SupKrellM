from pathlib import Path
import datetime
import json

from metrics import system, hardware, disk, process, network, webservices

def generate_html_report(selected_metrics, output_path):
    data = {}

    try:
        if "system" in selected_metrics:
            data["Système"] = system.get_system_info()
        if "hardware" in selected_metrics:
            data["Matériel"] = hardware.get_hardware_info()
        if "disk" in selected_metrics:
            data["Disques"] = disk.get_disk_info()
        if "process" in selected_metrics:
            data["CPU"] = process.get_cpu_info()
            data["Processus"] = process.get_process_list()
        if "network" in selected_metrics:
            data["Réseau"] = network.get_network_info()
            data["Passerelle par défaut"] = network.get_default_gateway()
        if "web" in selected_metrics:
            data["Web Services"] = webservices.get_web_services()

    except Exception as e:
        data["Erreur générale"] = str(e)

    template_path = Path(__file__).parent / "template.html"
    try:
        template = template_path.read_text(encoding="utf-8")
    except Exception:
        template = "<html><body><h1>Rapport système</h1>{content}</body></html>"

    json_content = json.dumps(data, indent=4, ensure_ascii=False)

    html_content = template.replace("{content}", f"<pre>{json_content}</pre>")
    html_content = html_content.replace("{date}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    output_path = Path(output_path)
    output_path.write_text(html_content, encoding="utf-8")

    return output_path
