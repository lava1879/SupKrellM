import http.client
from html.parser import HTMLParser

class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()


def fetch_http_info(host, port):
    info = {}
    try:
        conn_cls = http.client.HTTPConnection
        conn = conn_cls(host, port, timeout=3)
        conn.request("GET", "/")
        resp = conn.getresponse()

        info["statut"] = f"{resp.status} {resp.reason}"
        info["serveur"] = resp.getheader("Server", "Inconnu")
        body = resp.read(4096).decode(errors="ignore")

        parser = TitleParser()
        parser.feed(body)
        info["titre"] = parser.title or "Aucun titre détecté"

        if "<link" in body and "icon" in body:
            info["favicon"] = "Présent"
        else:
            info["favicon"] = "Non détecté"

    except Exception as e:
        info["Erreur"] = str(e)
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return info


def get_web_services(targets=None):
    if targets is None:
        targets = [("localhost", 80), ("localhost", 443)]

    results = {}
    for host, port in targets:
        key = f"http://{host}:{port}"
        results[key] = fetch_http_info(host, port)
    return results