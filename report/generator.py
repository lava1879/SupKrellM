from pathlib import Path
import datetime
from metrics import system, hardware, disk, memory, process, network, webservices

def _dict_to_html(title, data):
    html = f"<h2>{title}</h2>\n<ul>"
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                html += f"<li><strong>{k}:</strong><ul>"
                for kk, vv in v.items():
                    html += f"<li>{kk} : {vv}</li>"
                html += "</ul></li>"
            elif isinstance(v, list):
                html += f"<li><strong>{k}:</strong><ul>"
                for item in v:
                    if isinstance(item, dict):
                        html += "<li>"
                        html += ", ".join(f"{ik}: {iv}" for ik, iv in item.items())
                        html += "</li>"
                    else:
                        html += f"<li>{item}</li>"
                html += "</ul></li>"
            else:
                html += f"<li>{k} : {v}</li>"
    else:
        html += f"<li>{data}</li>"
    html += "</ul>"
    return html

def generate_html_report(selected_metrics, output_path):
    data = {}

    try:
        if "system" in selected_metrics or "all" in selected_metrics:
            data["Système"] = system.get_system_info()
        if "hardware" in selected_metrics or "all" in selected_metrics:
            data["Matériel"] = hardware.get_hardware_info()
        if "disk" in selected_metrics or "all" in selected_metrics:
            data["Disques"] = disk.get_disk_info()
        if "memory" in selected_metrics or "all" in selected_metrics:
            data["Mémoire"] = memory.get_memory_info()
        if "process" in selected_metrics or "all" in selected_metrics:
            data["CPU"] = process.get_cpu_info()
            data["Processus"] = process.get_process_list()
        if "network" in selected_metrics or "all" in selected_metrics:
            data["Réseau"] = network.get_network_info()
            data["Passerelle par défaut"] = network.get_default_gateway()
    except Exception as e:
        data["Erreur générale"] = str(e)

    try:
        data["Web Services"] = webservices.get_web_services()
    except Exception as e:
        data["Web Services"] = {"Erreur": str(e)}

    template_path = Path(__file__).parent / "template.html"
    try:
        template = template_path.read_text(encoding="utf-8")
    except Exception:
        template = "<html><body><h1>Rapport système</h1>{content}</body></html>"

    html_sections = ""
    for key, value in data.items():
        html_sections += _dict_to_html(key, value)

    html_content = template.replace("{content}", html_sections)
    html_content = html_content.replace("{date}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    output_path = Path(output_path)
    output_path.write_text(html_content, encoding="utf-8")

    return output_path
