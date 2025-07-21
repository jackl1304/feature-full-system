# scripts/proofread.py
import os
import sys
import json
import requests

# --- NEU: Funktion zum Lesen von Dateien ---
def read_file_content(filepath):
    """Liest den Inhalt einer Datei sicher."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warnung: Datei nicht gefunden unter {filepath}")
        return ""
    except Exception as e:
        print(f"Fehler beim Lesen der Datei {filepath}: {e}")
        return ""

# API-Schlüssel und Dateipfade aus Umgebungsvariablen holen
api_key = os.environ.get("GEMINI_API_KEY")
# CHANGED_FILES ist eine Zeichenkette mit Dateipfaden, getrennt durch Leerzeichen
changed_files_str = os.environ.get("CHANGED_FILES")

if not api_key:
    print("Fehler: GEMINI_API_KEY wurde nicht gefunden.")
    sys.exit(1)

if not changed_files_str:
    print("Info: Keine geänderten Markdown-Dateien im Pull Request gefunden. Überspringe.")
    sys.exit(0)

# --- NEU: Verarbeitung mehrerer Dateien ---
all_text_to_proofread = ""
# Wir teilen die Zeichenkette in eine Liste von Dateipfaden
changed_files = changed_files_str.split()

for file_path in changed_files:
    print(f"Lese Inhalt aus Datei: {file_path}")
    content = read_file_content(file_path)
    if content:
        # Wir fügen den Dateinamen und den Inhalt für den Kontext hinzu
        all_text_to_proofread += f"--- Inhalt von {os.path.basename(file_path)} ---\n{content}\n\n"

if not all_text_to_proofread:
    print("Info: Die geänderten Dateien waren leer oder konnten nicht gelesen werden.")
    sys.exit(0)

# Die URL für die Gemini API
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

# Der Prompt wurde angepasst, um den neuen Input zu verarbeiten
prompt = f"""Bitte korrigiere den folgenden Text aus einer oder mehreren Newsletter-Dateien auf Grammatik, Rechtschreibung und Stil.
Gib NUR den korrigierten Text zurück. Behalte die Trenner bei (z.B. '--- Inhalt von datei.md ---'), damit der Benutzer weiß, welcher Text zu welcher Datei gehört.

Originaltexte:
{all_text_to_proofread}
"""

# Die Daten für die API-Anfrage vorbereiten
payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}

# Die Anfrage an die API senden (alles ab hier bleibt gleich)
try:
    response = requests.post(api_url, json=payload, timeout=90)
    response.raise_for_status()
    data = response.json()

    if "candidates" in data and data["candidates"]:
        corrected_text = data["candidates"][0]["content"]["parts"][0]["text"]
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f'corrected_text={corrected_text}', file=fh)
    else:
        print("Fehler: Die API-Antwort enthielt keine gültigen 'candidates'.")
        print("Vollständige API-Antwort:", json.dumps(data))
        sys.exit(1)

except requests.exceptions.RequestException as e:
    print(f"Fehler bei der API-Anfrage: {e}")
    sys.exit(1)
except (KeyError, IndexError) as e:
    print(f"Fehler beim Verarbeiten der API-Antwort: {e}")
    print("Vollständige API-Antwort:", json.dumps(data))
    sys.exit(1)
