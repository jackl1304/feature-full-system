# src/renderer/email.py

import os
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Pfad zum templates-Ordner relativ zu dieser Datei
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"])
)

def render_newsletter(items: List[Dict]) -> str:
    """
    Rendert eine Liste von Artikeldicts zu HTML mittels newsletter.html.
    """
    template = env.get_template("newsletter.html")
    return template.render(items=items)
