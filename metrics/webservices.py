import http.client
import ssl
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


def fetch_http_info(host="localhost", port=80, use_https=False):
    info = {}
    try:
        conn_cls = http.client.HTTPSConnection if use_https else http.client.HTTPConnection
        context = ssl._create_unverified_context() if use_https else None
        conn = conn_cls(host, port, timeout=3, context=context)
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
        targets = [("localhost", 80, False), ("localhost", 443, True)]

    results = {}
    for host, port, secure in targets:
        key = f"http{'s' if secure else ''}://{host}:{port}"
        results[key] = fetch_http_info(host, port, secure)
    return results