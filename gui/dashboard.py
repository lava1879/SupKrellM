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
            "Header.TLabel",
            background="#2c3e50",
            foreground="#ffffff",
            font=("Epunda Sans Light", 16, "bold"),
            padding=10,
        )

        style.configure(
            "Section.TLabel",
            background="#1abc9c",
            foreground="#ffffff",
            font=("Epunda Sans Light", 12, "bold"),
            padding=5,
        )

        style.configure(
            "Info.TLabel",
            background="#ffffff",
            foreground="#333333",
            font=("Epunda Sans Light", 10),
            padding=5,
        )

        style.configure(
            "Time.TLabel",
            background="#f4f6f8",
            foreground="#333333",
            font=("Epunda Sans Light", 11),
            padding=5,
        )

    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Rapport Système - Temps Réel",
            bg="#2c3e50",
            fg="#ffffff",
            font=("Epunda Sans Light", 18, "bold"),
        )
        header_label.pack(pady=15)

        self.time_label = tk.Label(
            self.root,
            text="",
            bg="#f4f6f8",
            fg="#333333",
            font=("Epunda Sans Light", 11),
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

    def create_metric_sections(self):
        self.sections = {}

        self.sections["system"] = self.create_section("Système")

        self.sections["hardware"] = self.create_section("Matériel")

        self.sections["disk"] = self.create_section("Disques")

        self.sections["memory"] = self.create_section("Mémoire")

        self.sections["cpu"] = self.create_section("CPU")

        self.sections["process"] = self.create_section("Processus (Top 5)")

        self.sections["network"] = self.create_section("Réseau")

        self.sections["passerelle"] = self.create_section("Passerelle par défaut")

        self.sections["webservices"] = self.create_section("Web Services")

    def create_section(self, title):
        section_frame = tk.Frame(
            self.scrollable_frame, bg="#ffffff", relief=tk.RAISED, borderwidth=1
        )
        section_frame.pack(fill=tk.X, padx=10, pady=10)

        header = tk.Label(
            section_frame,
            text=title,
            bg="#1abc9c",
            fg="#ffffff",
            font=("Epunda Sans Light", 12, "bold"),
            anchor="center",
        )
        header.pack(fill=tk.X, pady=(0, 5))

        content = tk.Frame(section_frame, bg="#ffffff")
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        return {"frame": section_frame, "header": header, "content": content}

    def clear_section(self, section_name):
        content_frame = self.sections[section_name]["content"]
        for widget in content_frame.winfo_children():
            widget.destroy()

    def add_info_line(self, parent, key, value, is_error=False):
        line_frame = tk.Frame(parent, bg="#ffffff" if not is_error else "#ffecec")
        line_frame.pack(fill=tk.X, pady=2)

        key_label = tk.Label(
            line_frame,
            text=f"{key}:",
            bg="#ffffff" if not is_error else "#ffecec",
            fg="#1abc9c" if not is_error else "#c0392b",
            font=("Epunda Sans Light", 10, "bold"),
            anchor="w",
        )
        key_label.pack(side=tk.LEFT, padx=(5, 10))

        value_label = tk.Label(
            line_frame,
            text=str(value),
            bg="#ffffff" if not is_error else "#ffecec",
            fg="#333333" if not is_error else "#c0392b",
            font=("Epunda Sans Light", 10),
            anchor="w",
            wraplength=800,
        )
        value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def update_section(self, section_name, data):
        self.clear_section(section_name)
        content_frame = self.sections[section_name]["content"]

        if isinstance(data, dict):
            for key, value in data.items():
                is_error = "Erreur" in key or "erreur" in str(value).lower()

                if isinstance(value, dict):
                    sub_frame = tk.Frame(
                        content_frame, bg="#f9f9f9", relief=tk.GROOVE, borderwidth=1
                    )
                    sub_frame.pack(fill=tk.X, pady=5)

                    sub_header = tk.Label(
                        sub_frame,
                        text=key,
                        bg="#e8f5f2",
                        fg="#1abc9c",
                        font=("Epunda Sans Light", 10, "bold"),
                    )
                    sub_header.pack(fill=tk.X, padx=5, pady=2)

                    for k, v in value.items():
                        self.add_info_line(sub_frame, k, v, "Erreur" in k)

                elif isinstance(value, list):
                    sub_frame = tk.Frame(
                        content_frame, bg="#f9f9f9", relief=tk.GROOVE, borderwidth=1
                    )
                    sub_frame.pack(fill=tk.X, pady=5)

                    sub_header = tk.Label(
                        sub_frame,
                        text=key,
                        bg="#e8f5f2",
                        fg="#1abc9c",
                        font=("Epunda Sans Light", 10, "bold"),
                    )
                    sub_header.pack(fill=tk.X, padx=5, pady=2)

                    for item in value:
                        if isinstance(item, dict):
                            item_frame = tk.Frame(
                                sub_frame, bg="#ffffff", relief=tk.SOLID, borderwidth=1
                            )
                            item_frame.pack(fill=tk.X, padx=5, pady=2)

                            for k, v in item.items():
                                if k != "CPU":
                                    self.add_info_line(item_frame, k, v, False)
                        else:
                            self.add_info_line(sub_frame, "", item, False)
                else:
                    self.add_info_line(content_frame, key, value, is_error)
        else:
            label = tk.Label(
                content_frame,
                text=str(data),
                bg="#ffffff",
                fg="#333333",
                font=("Epunda Sans Light", 10),
                wraplength=800,
            )
            label.pack(fill=tk.X, pady=2)

    def collect_all_metrics(self):
        metrics = {}

        try:
            metrics["system"] = system.get_system_info()
        except Exception as e:
            metrics["system"] = {"Erreur": str(e)}

        try:
            metrics["hardware"] = hardware.get_hardware_info()
        except Exception as e:
            metrics["hardware"] = {"Erreur": str(e)}

        try:
            metrics["memory"] = memory.get_memory_info()
        except Exception as e:
            metrics["memory"] = {"Erreur": str(e)}

        try:
            metrics["disk"] = disk.get_disk_info()
        except Exception as e:
            metrics["disk"] = {"Erreur": str(e)}

        try:
            metrics["cpu"] = process.get_cpu_info()
        except Exception as e:
            metrics["cpu"] = {"Erreur": str(e)}

        try:
            metrics["process"] = process.get_process_list(limit=5)
        except Exception as e:
            metrics["process"] = {"Erreur": str(e)}

        try:
            metrics["network"] = network.get_network_info()
        except Exception as e:
            metrics["network"] = {"Erreur": str(e)}
            
        try:
            metrics["passerelle"] = network.get_default_gateway()
        except Exception as e:
            metrics["passerelle"] = {"Erreur": str(e)}

        try:
            metrics["webservices"] = webservices.get_web_services()
        except Exception as e:
            metrics["webservices"] = {"Erreur": str(e)}

        return metrics

    def update_display(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"Dernière mise à jour: {current_time}")

        metrics = self.collect_all_metrics()

        self.update_section("system", metrics["system"])
        self.update_section("hardware", metrics["hardware"])
        self.update_section("memory", metrics["memory"])
        self.update_section("disk", metrics["disk"])
        self.update_section("cpu", metrics["cpu"])

        if isinstance(metrics["process"], list):
            process_dict = {}
            for i, proc in enumerate(metrics["process"], 1):
                process_dict[f"Processus {i}"] = proc
            self.update_section("process", process_dict)
        else:
            self.update_section("process", metrics["process"])

        self.update_section("network", metrics["network"])
        self.update_section("passerelle", metrics["passerelle"])
        self.update_section("webservices", metrics["webservices"])

    def refresh_loop(self):
        while self.running:
            try:
                self.root.after(0, self.update_display)
                time.sleep(10)
            except Exception as e:
                print(f"Erreur dans la boucle de rafraîchissement: {e}")
                time.sleep(10)


def launch_gui():
    root = tk.Tk()
    SystemDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
