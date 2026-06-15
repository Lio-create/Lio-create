"""
E-Mail Verwaltung - Automatisches Kategorisieren von E-Mails per IMAP

Setup:
    sudo apt update
    sudo apt install python3.12-venv

    cd /home/lio/Schreibtisch/code
    rm -rf .venv
    python3 -m venv .venv
    source .venv/bin/activate
    pip install python-dotenv

    Lege eine Datei ".env" im selben Ordner an mit:
        GMAIL_APP_PASSWORT=dein-app-passwort
"""

import time
import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# ----------------- KONFIGURATION -----------------

load_dotenv()

EMAIL_ACCOUNT = "fabian_rene.foerster@gmx.de"
APP_PASSWORT_GMX = os.getenv("GMX_APP_PASSWORT")

ANZAHL_MAILS = 100 # Wie viele der neuesten Mails geprüft werden sollen

# Absender/Personen, die NIE verschoben werden (bleiben in der Inbox)
WICHTIGE_ABSENDER = [
    "jessica förster",
    "robert schifferer",
    "roi.lea@gmx.de",
    "fabian_rene.foerster@gmx.de",
    "skip.lio.tv@gmail.com",
    "@it-foerster.atlassian.net",
]

# Kategorie-Regeln: Schlüsselwort -> Zielordner (Label)
KATEGORIE_REGELN = {
    # Shopping / Bestellungen
    "amazon": "Shopping",
    "pandora": "Shopping",
    "temu": "Shopping",
    "shein": "Shopping",
    "open-mind market": "Shopping",
    "openmind.market": "Shopping",
    "klarna": "Shopping",
    "nyx": "Shopping",
    "mcdonald": "Shopping",
    "shell": "Shopping",
    "itunes": "Shopping",
    "zasta": "Shopping",
    "3-fpo": "Shopping",
    "eis-de": "Shopping",

    # Versand/Lieferung
    "dhl": "Versand",
    "go3000": "Versand",
    "lieferschein": "Versand",

    # Jobsuche (Jobangebote / Job-Alerts)
    "stepstone": "Jobangebote",
    "linkedin": "Jobangebote",
    "alerts für stellenangebote": "Jobangebote",
    "zety": "Jobangebote",
    "pagepersonnel": "Jobangebote",
    "cadenas": "Jobangebote",
    "eos gmbh": "Jobangebote",
    "ferchau": "Jobangebote",
    "it-support": "Jobangebote",
    "fachinformatiker": "Jobangebote",

    # Bewerbungen - dein aktiver Bewerbungsprozess
    "bewerbung": "Bewerbungen",
    "recruiting": "Bewerbungen",
    "vorstellungsgespräch": "Bewerbungen",
    "videointerview": "Bewerbungen",
    "telefoninterview": "Bewerbungen",
    "arbeitsvertrag": "Bewerbungen",
    "bundesagentur für arbeit": "Bewerbungen",
    "akkodis": "Bewerbungen",
    "dis ag": "Bewerbungen",
    "hemmersbach": "Bewerbungen",
    "knds": "Bewerbungen",

    # Rechnungen / Zahlungen
    "zahlung erhalten": "Rechnungen",
    "zahlungserinnerung": "Rechnungen",
    "rechnung": "Rechnungen",
    "easyfitness": "Rechnungen",
    "finion capital": "Rechnungen",

    # Gaming
    "ubisoft": "Gaming",
    "steam": "Gaming",
    "battle.net": "Gaming",
    "blizzard": "Gaming",
    "supercell": "Gaming",
    "epicgames": "Gaming",
    "nintendo": "Gaming",
    "xbox": "Gaming",
    "playstation": "Gaming",
    "sony": "Gaming",
    "faceit": "Gaming",
    "skinsmonkey": "Gaming",
    "geoguessr": "Gaming",
    "glyph": "Gaming",
    "ea-spiele": "Gaming",
    "ea-sicherheitscode": "Gaming",

    # Streaming
    "netflix": "Streaming",
    "spotify": "Streaming",
    "primevideo": "Streaming",
    "soundcloud": "Streaming",
    "soundtrap": "Streaming",
    "tagesschau": "Streaming",

    # Konto & Sicherheit
    "google": "Konto-Sicherheit",
    "github": "Konto-Sicherheit",
    "microsoft": "Konto-Sicherheit",
    "accountprotection": "Konto-Sicherheit",
    "n26": "Konto-Sicherheit",
    "reddit": "Konto-Sicherheit",
    "mediafire": "Konto-Sicherheit",
    "teamviewer": "Konto-Sicherheit",
    "gmx sicherheitshinweis": "Konto-Sicherheit",
    "new device logged in": "Konto-Sicherheit",
    "claude.ai": "Konto-Sicherheit",

    # Social
    "snapchat": "Social",
    "fiverr": "Social",
    "instagram": "Social",
    "vũ thị lợi": "Social",

    # Kleinanzeigen
    "kleinanzeigen": "Kleinanzeigen",

    # Tools / Software
    "atlassian": "Tools",
    "jira": "Tools",
    "lovable": "Tools",
    "openai": "Tools",
    "gitkraken": "Tools",
    "use ai": "Tools",
    "use.ai": "Tools",

    # Marketing / Werbung
    "copecart": "Werbung",
    "testbirds": "Werbung",
    "cusbclo": "Werbung",
    "stake.us": "Werbung",
    "cryptobrowser": "Werbung",
    "macadam": "Werbung",
    "gratiswette": "Werbung",
    "wm26": "Werbung",
    "wm 2026": "Werbung",

    # Wichtig/Persönlich (Rechnungen, Verträge, Inkasso)
    "inkasso": "Wichtig",
    "lastschrift": "Wichtig",
    "überweisung": "Wichtig",
    "leb april": "Wichtig",
    "edln": "Wichtig",
    "mobilfunknummer": "Wichtig",
}
# ----------------- HILFSFUNKTIONEN -----------------

def decode_str(s):
    if s is None:
        return ""
    decoded, encoding = decode_header(s)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def ensure_folder_exists(mail, folder_name):
    """Legt das Label/Ordner an, falls es noch nicht existiert."""
    status, folders = mail.list()
    existing = []
    for f in folders:
        decoded = f.decode()
        if '"' in decoded:
            existing.append(decoded.split('"')[-2])
    if folder_name not in existing:
        mail.create(folder_name)


# ----------------- HAUPTPROGRAMM -----------------

def main():
    if not APP_PASSWORT_GMX:
        print("FEHLER: Kein App-Passwort gefunden. .env-Datei prüfen!")
        return

# Für GMX:
    mail = imaplib.IMAP4_SSL("imap.gmx.net")
    mail.login(EMAIL_ACCOUNT, APP_PASSWORT_GMX)
    mail.select("inbox")

    status, data = mail.search(None, "ALL")
    mail_ids = data[0].split()
    letzte_n = mail_ids[-ANZAHL_MAILS:]

    verschoben_count = 0
    uebersprungen_count = 0
    keine_kategorie_count = 0

    for num in letzte_n:
        status, msg_data = mail.fetch(num, "(RFC822)")

        if status != "OK" or msg_data[0] is None:
            print(f"Mail {num} nicht abrufbar, übersprungen.")
            uebersprungen_count += 1
            continue

        msg = email.message_from_bytes(msg_data[0][1])

        absender = decode_str(msg.get("From")).lower()
        betreff = decode_str(msg.get("Subject")).lower()

        # 1. Prüfen ob wichtiger Absender -> niemals verschieben
        ist_wichtig = False
        for wichtig in WICHTIGE_ABSENDER:
            if wichtig.lower() in absender:
                ist_wichtig = True
                break

        if ist_wichtig:
            print(f"Wichtig (übersprungen): {betreff[:50]}")
            continue

        # 2. Kategorie anhand der Regeln finden
        kategorie = None
        for keyword, ziel in KATEGORIE_REGELN.items():
            if keyword in absender or keyword in betreff:
                kategorie = ziel
                break

        if kategorie:
            ensure_folder_exists(mail, kategorie)
            mail.copy(num, kategorie)
            mail.store(num, "+FLAGS", "\\Deleted")
            mail.expunge()  # sofort ausführen
            print(f"Verschoben nach '{kategorie}': {betreff[:50]}")
            verschoben_count += 1
            time.sleep(1)
        else:
            continue

    mail.logout()

    print("\n--- Zusammenfassung ---")
    print(f"Verschoben: {verschoben_count}")
    print(f"Keine Kategorie (in Inbox geblieben): {keine_kategorie_count}")
    print(f"Übersprungen (Fehler): {uebersprungen_count}")


if __name__ == "__main__":
    main()