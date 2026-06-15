"""
E-Mail Verwaltung - Automatisches Kategorisieren von E-Mails per IMAP

Setup:
    pip install python-dotenv

    Lege eine Datei ".env" im selben Ordner an mit:
        GMAIL_APP_PASSWORT=dein-app-passwort
"""

import os
import ssl
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# ----------------- KONFIGURATION -----------------

print(ssl.OPENSSL_VERSION)

load_dotenv()

EMAIL_ACCOUNT = "fcbjungs@gmail.com"
APP_PASSWORT = os.getenv("GMAIL_APP_PASSWORT")

ANZAHL_MAILS = 50  # Wie viele der neuesten Mails geprüft werden sollen

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

    # Jobsuche
    "stepstone": "Jobangebote",
    "linkedin": "Jobangebote",
    "alerts für stellenangebote": "Jobangebote",
    "zety": "Jobangebote",
    "pagepersonnel": "Jobangebote",
    "cadenas": "Jobangebote",

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

    # Streaming
    "netflix": "Streaming",
    "spotify": "Streaming",
    "primevideo": "Streaming",
    "soundcloud": "Streaming",
    "soundtrap": "Streaming",

    # Konto & Sicherheit
    "google": "Konto-Sicherheit",
    "github": "Konto-Sicherheit",
    "microsoft": "Konto-Sicherheit",
    "accountprotection": "Konto-Sicherheit",
    "n26": "Konto-Sicherheit",
    "reddit": "Konto-Sicherheit",
    "mediafire": "Konto-Sicherheit",

    # Social
    "snapchat": "Social",
    "fiverr": "Social",

    # Kleinanzeigen
    "kleinanzeigen": "Kleinanzeigen",

    # Tools / Software
    "atlassian": "Tools",
    "jira": "Tools",
    "lovable": "Tools",
    "openai": "Tools",
    "gitkraken": "Tools",

    # Marketing / Werbung
    "copecart": "Werbung",
    "testbirds": "Werbung",
    "cusbclo": "Werbung",
    "stake.us": "Werbung",
    "cryptobrowser": "Werbung",
    "macadam": "Werbung",
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
    if not APP_PASSWORT:
        print("FEHLER: Kein App-Passwort gefunden. .env-Datei prüfen!")
        return

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_ACCOUNT, APP_PASSWORT)
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
            print(f"Verschoben nach '{kategorie}': {betreff[:50]}")
            verschoben_count += 1
        else:
            print(f"Keine Kategorie für: {betreff[:50]}")
            keine_kategorie_count += 1

    mail.expunge()
    mail.logout()

    print("\n--- Zusammenfassung ---")
    print(f"Verschoben: {verschoben_count}")
    print(f"Keine Kategorie (in Inbox geblieben): {keine_kategorie_count}")
    print(f"Übersprungen (Fehler): {uebersprungen_count}")


if __name__ == "__main__":
    main()