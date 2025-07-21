# scripts/proofread.py
import os
import sys
import json
import requests

# API-Schlüssel und Text aus der Umgebungsvariable holen
api_key = os.environ.get("GEMINI_API_KEY")
pr_title = os.environ.get("PR_TITLE")
pr_body = os.environ.get("PR_BODY")

# Prüfen, ob alle nötigen Informationen vorhanden sind
if not api_key:
    print("Fehler: GEMINI_API_KEY wurde nicht gefunden.")
    sys.exit(1)
if not pr_body:
    print("Info: Pull-Request-Beschreibung ist leer. Es gibt nichts zu prüfen.")
    # Wir beenden den Prozess erfolgreich, da es kein Fehler ist.
    # Um den korrigierten Text auszugeben, muss er leer sein.
    print(f"::set-output name=corrected_text::")
    sys.exit(0)

# Die URL für die Gemini API
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

# Der Prompt, der an die KI gesendet wird
prompt = f"""Bitte korrigiere den folgenden Newsletter-Entwurf auf Grammatik, Rechtschreibung und Stil.
Gib NUR den korrigierten Text zurück, ohne eine Einleitung oder sonstige Kommentare.

Originaltitel: {pr_title}
Originaltext:
{pr_body}
"""

# Die Daten für die API-Anfrage vorbereiten
payload = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}

# Die Anfrage an die API senden
try:
    response = requests.post(api_url, json=payload, timeout=60)
    response.raise_for_status()  # Löst einen Fehler bei schlechtem Statuscode aus (z.B. 403, 500)
    data = response.json()

    # Den korrigierten Text sicher aus der Antwort extrahieren
    if "candidates" in data and data["candidates"]:
        corrected_text = data["candidates"][0]["content"]["parts"][0]["text"]
        # Den korrigierten Text für den nächsten Schritt im Workflow ausgeben
        print(f"::set-output name=corrected_text::{corrected_text}")
    else:
        # Falls die API eine gültige, aber leere oder unerwartete Antwort gibt
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
