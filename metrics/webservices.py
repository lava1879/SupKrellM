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

def fetch():
    host = "www.google.com"
    port = 443
    info = {}

    try:
        context = ssl._create_unverified_context()
        conn = http.client.HTTPSConnection(host, port, timeout=5, context=context)
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

    return {f"https://{host}": info}

def get_web_services():
    return fetch()