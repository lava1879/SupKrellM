import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from metrics import system, hardware, memory, disk, process, network, webservices


class SystemDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Rapport Système")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f4f6f8")
        self.running = True
        self.setup_styles()
        self.create_widgets()
        self.refresh_thread = threading.Thread(target=self.refresh_loop, daemon=True)
        self.refresh_thread.start()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Section.TLabel",
            background="#CD2C58",
            foreground="#ffffff",
            font=("Epunda Sans", 12, "bold"),
            padding=5,
        )

    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg="#333333", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Rapport Système - Temps Réel",
            bg="#333333",
            fg="#ffffff",
            font=("Epunda Sans", 18, "bold"),
        )
        header_label.pack(pady=15)

        self.time_label = tk.Label(
            self.root,
            text="",
            bg="#f4f6f8",
            fg="#333333",
            font=("Epunda Sans", 11),
        )
        self.time_label.pack(pady=5)

        main_frame = tk.Frame(self.root, bg="#f4f6f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas = tk.Canvas(main_frame, bg="#f4f6f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f4f6f8")

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        self.create_metric_sections()

        self.update_display()

    def create_metric_sections(self):
        self.sections = {}
        section_names = [
            "system",
            "hardware",
            "disk",
            "memory",
            "cpu",
            "process",
            "network",
            "passerelle",
            "webservices",
        ]
        section_titles = [
            "Système",
            "Matériel",
            "Disques",
            "Mémoire",
            "CPU",
            "Processus (Top 5)",
            "Réseau",
            "Passerelle par défaut",
            "Web Services",
        ]

        for name, title in zip(section_names, section_titles):
            self.sections[name] = self.create_section(title)

    def create_section(self, title):
        section_frame = tk.Frame(
            self.scrollable_frame, bg="#ffffff", relief=tk.RAISED, borderwidth=1
        )
        section_frame.pack(fill=tk.X, padx=10, pady=10)

        header = tk.Label(
            section_frame,
            text=title,
            bg="#CD2C58",
            fg="#ffffff",
            font=("Epunda Sans", 12, "bold"),
            anchor="center",
        )
        header.pack(fill=tk.X, pady=(0, 5))

        content = tk.Frame(section_frame, bg="#ffffff")
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        return {"content": content, "widgets": {}, "last_data": None}

    def _data_changed(self, old_data, new_data):
        return old_data != new_data

    def update_section(self, section_name, data):
        section = self.sections[section_name]

        if not self._data_changed(section["last_data"], data):
            return

        section["last_data"] = data
        content_frame = section["content"]

        existing_keys = set(section["widgets"].keys())
        new_keys = set()

        if isinstance(data, dict):
            for key, value in data.items():
                new_keys.add(key)
                is_error = "Erreur" in key or "erreur" in str(value).lower()

                if isinstance(value, dict):

                    if key in section["widgets"]:
                        sub_frame = section["widgets"][key]["frame"]
                        self._update_dict_content(
                            sub_frame, value, section["widgets"][key]
                        )
                    else:
                        sub_frame = tk.Frame(
                            content_frame, bg="#f9f9f9", relief=tk.GROOVE, borderwidth=1
                        )
                        sub_frame.pack(fill=tk.X, pady=5)

                        sub_header = tk.Label(
                            sub_frame,
                            text=key,
                            bg="#e8f5f2",
                            fg="#CD2C58",
                            font=("Epunda Sans", 10, "bold"),
                        )
                        sub_header.pack(fill=tk.X, padx=5, pady=2)

                        section["widgets"][key] = {
                            "frame": sub_frame,
                            "header": sub_header,
                            "items": {},
                        }
                        self._update_dict_content(
                            sub_frame, value, section["widgets"][key]
                        )

                elif isinstance(value, list):

                    if key in section["widgets"]:
                        sub_frame = section["widgets"][key]["frame"]
                        self._update_list_content(
                            sub_frame, value, section["widgets"][key]
                        )
                    else:
                        sub_frame = tk.Frame(
                            content_frame, bg="#f9f9f9", relief=tk.GROOVE, borderwidth=1
                        )
                        sub_frame.pack(fill=tk.X, pady=5)

                        sub_header = tk.Label(
                            sub_frame,
                            text=key,
                            bg="#e8f5f2",
                            fg="#CD2C58",
                            font=("Epunda Sans", 10, "bold"),
                        )
                        sub_header.pack(fill=tk.X, padx=5, pady=2)

                        section["widgets"][key] = {
                            "frame": sub_frame,
                            "header": sub_header,
                            "items": [],
                        }
                        self._update_list_content(
                            sub_frame, value, section["widgets"][key]
                        )

                else:

                    if key in section["widgets"]:
                        widget_info = section["widgets"][key]
                        widget_info["value_label"].config(text=str(value))

                        bg_color = "#ffecec" if is_error else "#ffffff"
                        fg_color = "#c0392b" if is_error else "#333333"
                        key_color = "#c0392b" if is_error else "#CD2C58"

                        widget_info["frame"].config(bg=bg_color)
                        if widget_info["key_label"]:
                            widget_info["key_label"].config(bg=bg_color, fg=key_color)
                        widget_info["value_label"].config(bg=bg_color, fg=fg_color)
                    else:
                        line_frame = self._create_info_line(
                            content_frame, key, value, is_error
                        )
                        section["widgets"][key] = line_frame

            for key in existing_keys - new_keys:
                if key in section["widgets"]:
                    widget_info = section["widgets"][key]
                    if "frame" in widget_info:
                        widget_info["frame"].destroy()
                    del section["widgets"][key]

        else:

            simple_key = "_simple_value_"
            new_keys.add(simple_key)

            if simple_key in section["widgets"]:

                section["widgets"][simple_key]["value_label"].config(
                    text=str(data) if data else "N/A"
                )
            else:

                label = tk.Label(
                    content_frame,
                    text=str(data) if data else "N/A",
                    bg="#ffffff",
                    fg="#333333",
                    font=("Epunda Sans", 10),
                    wraplength=800,
                )
                label.pack(fill=tk.X, pady=2)
                section["widgets"][simple_key] = {
                    "frame": label,
                    "value_label": label,
                    "key_label": None,
                }

            for key in existing_keys - new_keys:
                if key in section["widgets"]:
                    widget_info = section["widgets"][key]
                    if "frame" in widget_info:
                        widget_info["frame"].destroy()
                    del section["widgets"][key]

    def _update_dict_content(self, parent_frame, data_dict, widget_info):
        existing_keys = set(widget_info["items"].keys())
        new_keys = set(data_dict.keys())

        for k, v in data_dict.items():
            is_error = "Erreur" in k
            if k in widget_info["items"]:
                item = widget_info["items"][k]
                item["value_label"].config(text=str(v))

                bg_color = "#ffecec" if is_error else "#f9f9f9"
                fg_color = "#c0392b" if is_error else "#333333"
                key_color = "#c0392b" if is_error else "#CD2C58"

                item["frame"].config(bg=bg_color)
                if item["key_label"]:
                    item["key_label"].config(bg=bg_color, fg=key_color)
                item["value_label"].config(bg=bg_color, fg=fg_color)
            else:
                line_frame = self._create_info_line(parent_frame, k, v, is_error)
                widget_info["items"][k] = line_frame

        for k in existing_keys - new_keys:
            widget_info["items"][k]["frame"].destroy()
            del widget_info["items"][k]

    def _update_list_content(self, parent_frame, data_list, widget_info):

        existing_count = len(widget_info["items"])
        new_count = len(data_list)

        if existing_count != new_count:

            for item in widget_info["items"]:
                if "frame" in item:
                    item["frame"].destroy()
            widget_info["items"].clear()

            for item in data_list:
                if isinstance(item, dict):
                    item_frame = tk.Frame(
                        parent_frame, bg="#ffffff", relief=tk.SOLID, borderwidth=1
                    )
                    item_frame.pack(fill=tk.X, padx=5, pady=2)

                    item_widgets = {}
                    for k, v in item.items():
                        if k != "CPU":
                            line = self._create_info_line(item_frame, k, v, False)
                            item_widgets[k] = line

                    widget_info["items"].append(
                        {"frame": item_frame, "widgets": item_widgets}
                    )
                else:
                    line = self._create_info_line(parent_frame, "", item, False)
                    widget_info["items"].append(line)
        else:

            for i, item in enumerate(data_list):
                if isinstance(item, dict) and i < len(widget_info["items"]):
                    item_info = widget_info["items"][i]
                    if "widgets" in item_info:
                        for k, v in item.items():
                            if k != "CPU" and k in item_info["widgets"]:
                                item_info["widgets"][k]["value_label"].config(
                                    text=str(v)
                                )

    def _create_info_line(self, parent, key, value, is_error=False):
        bg_color = "#ffecec" if is_error else "#ffffff"
        fg_color = "#c0392b" if is_error else "#333333"
        key_color = "#c0392b" if is_error else "#CD2C58"

        line_frame = tk.Frame(parent, bg=bg_color)
        line_frame.pack(fill=tk.X, pady=2)

        key_label = None
        if key:
            key_label = tk.Label(
                line_frame,
                text=f"{key}:",
                bg=bg_color,
                fg=key_color,
                font=("Epunda Sans", 10, "bold"),
                anchor="w",
            )
            key_label.pack(side=tk.LEFT, padx=(5, 10))

        value_label = tk.Label(
            line_frame,
            text=str(value),
            bg=bg_color,
            fg=fg_color,
            font=("Epunda Sans", 10),
            anchor="w",
            wraplength=800,
        )
        value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        return {"frame": line_frame, "key_label": key_label, "value_label": value_label}

    def collect_all_metrics(self):
        metrics = {}
        collectors = [
            ("system", system.get_system_info),
            ("hardware", hardware.get_hardware_info),
            ("memory", memory.get_memory_info),
            ("disk", disk.get_disk_info),
            ("cpu", process.get_cpu_info),
            ("process", lambda: process.get_process_list(limit=5)),
            ("network", network.get_network_info),
            ("passerelle", network.get_default_gateway),
            ("webservices", webservices.get_web_services),
        ]

        for name, collector in collectors:
            try:
                metrics[name] = collector()
            except Exception as e:
                metrics[name] = {"Erreur": str(e)}

        return metrics

    def update_display(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"Dernière mise à jour: {current_time}")

        metrics = self.collect_all_metrics()

        for section in [
            "system",
            "hardware",
            "memory",
            "disk",
            "cpu",
            "network",
            "passerelle",
            "webservices",
        ]:
            self.update_section(section, metrics[section])

        if isinstance(metrics["process"], list):
            process_dict = {
                f"Processus {i}": proc for i, proc in enumerate(metrics["process"], 1)
            }
            self.update_section("process", process_dict)
        else:
            self.update_section("process", metrics["process"])

    def refresh_loop(self):
        while self.running:
            try:
                self.root.after(0, self.update_display)
                time.sleep(1)
            except Exception as e:
                print(f"Erreur dans la boucle de rafraîchissement: {e}")
                time.sleep(1)


def launch_gui():
    root = tk.Tk()
    SystemDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
