# Charakter-RPG
# Erstellung, Kampf, Leveling, Shop

# Imports
import os
import json
import random
import time

# Farben (ANSI-Codes)
ROT = "\033[91m"
GRUEN = "\033[92m"
BLAU = "\033[94m"
GELB = "\033[93m"
GOLD = "\033[38;5;220m"
RESET = "\033[0m"

# Definierung der Gebiete
gebiete = [
    {"name": "Wiesen", "min_level": 1, "max_level": 5},
     {"name": "Wald", "min_level": 3, "max_level": 10},
    {"name": "Höhlen", "min_level": 8, "max_level": 20},
    {"name": "Vulkan", "min_level": 15, "max_level": 30},
]

# Shop-Items
shop_items = [
    {"name": "Heiltrank", "preis": 20, "typ": "heilung", "wert": 50},
    {"name": "Kraft-Elixier", "preis": 100, "typ": "staerke_boost", "wert": 10},
    {"name": "Lebens-Kristall", "preis": 150, "typ": "max_leben_boost", "wert": 20},
    {"name": "Manatrank", "preis": 25, "typ": "mana_auffuellen", "wert": 40},
]

# Story Modus einheiten
story_quests = [
    {
        "titel": "Die ersten Schritte",
        "text": "Ein kleiner Wolf treibt sein Unwesen am Dorfrand. Die Bewohner bitten dich um Hilfe...",
        "anzahl_gegner": 5,
        "gegner_min_level": 1,
        "gegner_max_level": 5,
        "boss_level": 7,
        "belohnung_muenzen": 50,
    },
    {
        "titel": "Der Waldgeist",
        "text": "Tief im Wald erwacht ein uralter Geist. Niemand, der ihn sah, ist je zurückgekehrt...",
        "anzahl_gegner": 10,
        "gegner_min_level": 5,
        "gegner_max_level": 10 ,
        "boss_level": 12,
        "belohnung_muenzen": 100,
    },
    {
        "titel": "Der Drachenkönig",
        "text": "Auf dem Vulkan thront ein gewaltiger Drache. Nur die Mutigsten wagen den Aufstieg...",
        "anzahl_gegner": 15,
        "gegner_min_level": 10,
        "gegner_max_level": 15,
        "boss_level": 20,
        "belohnung_muenzen": 500,
    },
]

DATEIPFAD = "charaktere.json"
SCHNELLER_KAMPF = True
# Clear console
CLEAR = os.system("cls" if os.name == "nt" else "clear")

# ---------------------------------------------
# Charakter Bilder definieren
# ---------------------------------------------
ASCII_KRIEGER = """
KRIEGER
STR ████████░░ Nahkampf · Tank
          ╭─────╮          ▲
          │ ●  ●│         ███
          │  ╶  │         ███
         ╭┴─────┴╮        ███
        ╱│ █████ │╲       ███
       ▐ │ █████ │ ▌    ▆▆███▆▆
        ╲│ █████ │════════▟█▙
         ╰─┬───┬─╯        ▝▀▘
           │   │
          ╱│   │╲
         ▐ │   │ ▌
           │   │
          ╱╲   ╱╲
         ▟▆▘   ▝▆▙
"""

ASCII_MAGIER = """
MAGIER
INT ████████░░ Magie · Fernkampf
            ╱╲
           ╱  ╲
          ╱ ✦  ╲
         ╱──────╲
        │  ●  ● │
        │   ╶   │
        │ ╲▁▁▁╱ │
         ╲──┬┬──╱
        ╱╲ ╱││╲       ✦
       │  ╳ ▒▒ ╳─────◓
       │ │ ▒▒▒▒ │
        ╲│ ▒▒▒▒ │
         │ ▒▒▒▒ │
        ╱  ▒▒▒▒  ╲
       ╱▁▁▁▁▁▁▁▁▁▁╲
"""

ASCII_SCHURKE = """
SCHURKE
DEX ████████░░ Schaden · Tempo
         ╱╲▂▂╱╲
        ╱ ▔▔▔▔ ╲
       ╱╱  ▂▂  ╲╲
      ╱ │ ◣  ◢ │ ╲
      │ │ ╲▔▔╱ │ │
       ╲│ ▽▽▽▽ │╱
      ◤ ╲▔▔▔▔▔╱ ◥
     ╱ ╳╲│    │╱╳ ╲
    ◤ ╱  │    │  ╲ ◥
       ╱ │    │ ╲
         │    │
        ▟▆    ▆▙
"""


# ---------------------------------------------
# Charakter erstellen
# ---------------------------------------------
def charakter_erstellen():
    charakter = {}

    os.system("cls" if os.name == "nt" else "clear")

    charakter["name"] = input("Gib den Namen des Charakters ein:\n\n>: ")

    while True:
        charakter["gender"] = input(
            "\nGib das Geschlecht des Charakters ein:\nAUSWAHL: Männlich (M:) / Weiblich (W:)\n\n>: "
        ).upper()
        if charakter["gender"] in ["M", "W"]:
            break
        print("Ungültige Antwort")

    while True:
        charakter["klasse"] = input(
            "\nGib die Klasse des Charakters ein:\nAUSWAHL: Krieger / Magier / Schurke\n\n>: "
        ).upper()
        if charakter["klasse"] in ["KRIEGER", "MAGIER", "SCHURKE"]:
            break
        print("Ungültige Antwort!")

    # Standard Werte je Klasse
    if charakter["klasse"] == "KRIEGER":
        charakter["leben"] = 100
        charakter["max_leben"] = 100
        charakter["staerke"] = 70
        charakter["mana"] = 100
        charakter["max_mana"] = 100

    elif charakter["klasse"] == "MAGIER":
        charakter["leben"] = 80
        charakter["max_leben"] = 80
        charakter["staerke"] = 50
        charakter["mana"] = 120
        charakter["max_mana"] = 120

    elif charakter["klasse"] == "SCHURKE":
        charakter["leben"] = 120
        charakter["max_leben"] = 120
        charakter["staerke"] = 60
        charakter["mana"] = 90
        charakter["max_mana"] = 90

    # Gilt für alle Klassen
    charakter["story_fortschritt"] = 0
    charakter["level"] = 1
    charakter["xp"] = 0
    charakter["muenzen"] = 50

    return charakter

# ---------------------------------------------
# ASCII Bilder neben Charaktere anzeigen
# ---------------------------------------------
def nebeneinander_anzeigen(links, rechts, breite_links=20, versatz_rechts=0):
    links_zeilen = links.strip("\n").split("\n")
    rechts_zeilen = rechts.strip("\n").split("\n")

    # Leerzeilen voranstellen, um rechts zu verschieben
    rechts_zeilen = [""] * versatz_rechts + rechts_zeilen

    max_zeilen = max(len(links_zeilen), len(rechts_zeilen))

    for i in range(max_zeilen):
        links_teil = links_zeilen[i] if i < len(links_zeilen) else ""
        rechts_teil = rechts_zeilen[i] if i < len(rechts_zeilen) else ""
        print(f"{links_teil:<{breite_links}} {rechts_teil}")

# ---------------------------------------------
# Alle Charaktere anzeigen
# ---------------------------------------------
def alle_charakter_anzeigen(liste):
    for charakter in liste:
        if charakter["klasse"] == "KRIEGER":
            art = ASCII_KRIEGER
        elif charakter["klasse"] == "MAGIER":
            art = ASCII_MAGIER
        elif charakter["klasse"] == "SCHURKE":
            art = ASCII_SCHURKE

        xp_benoetigt = charakter["level"] * 100

        info_text = (
            f"Name: {BLAU}{charakter['name']}{RESET}\n"
            f"Level: {GOLD}{charakter['level']}{RESET}\n"
            f"Geschlecht: {charakter['gender']}\n"
            f"Klasse: {charakter['klasse']}\n"
            f"Leben: {GRUEN}{charakter['leben']}{RESET} / {GRUEN}{charakter['max_leben']}{RESET}\n"
            f"Stärke: {ROT}{charakter['staerke']}{RESET}\n"
            f"Mana: {BLAU}{charakter['mana']}{RESET} / {BLAU}{charakter['max_mana']}{RESET}\n"
            f"XP: {BLAU}{charakter['xp']}{RESET} / {BLAU}{xp_benoetigt}{RESET}\n"
            f"Münzen: {GOLD}{charakter['muenzen']}{RESET}"
        )

        nebeneinander_anzeigen(art, info_text, breite_links=30, versatz_rechts=6)
        print("")


# ---------------------------------------------
# Gegner erstellen (automatisch, levelabhängig)
# ---------------------------------------------
def gegner_erstellen(min_level, max_level):
    level = random.randint(min_level, max_level)
    gegner = {}
    gegner["name"] = "Gegner"
    gegner["leben"] = 50 + (level * 10)
    gegner["max_leben"] = 50 + (level * 10)
    gegner["staerke"] = 30 + (level * 5)
    gegner["mana"] = 0
    gegner["level"] = level

    return gegner

# ---------------------------------------------
# Lebensleiste im Kapmf
# ---------------------------------------------
def lebensleiste(aktuell, maximum, leange=20):
    aktuell = max(0, aktuell) #nie negativ anzeigen
    gefuellt = int((aktuell / maximum ) * leange)
    leer = leange - gefuellt
    return f"[{'█' * gefuellt}{'░' * leer}] {aktuell}/{maximum}"

# ---------------------------------------------
# Lebensleiste im Kapmf anzeigen
# ---------------------------------------------

def kampf_anzeige(spieler, gegner, letzte_aktion=""):
    os.system("cls" if os.name == "nt" else "clear")
    print(f"⚔️  {BLAU}{spieler['name']}{RESET} (Lvl {spieler['level']}) vs. {ROT}{gegner['name']}{RESET} (Lvl {gegner['level']})\n")
    print(f"{spieler['name']:10} {lebensleiste(spieler['leben'], spieler['max_leben'])}")
    print(f"{gegner['name']:10} {lebensleiste(gegner['leben'], gegner['max_leben'])}")
    print(f"\n{letzte_aktion}")


# ---------------------------------------------
# Charakter per Name finden
# ---------------------------------------------
def charakter_finden(liste, name):
    for charakter in liste:
        if charakter["name"] == name:
            return charakter
    return None

# ---------------------------------------------
# Hauptmenü anzeige
# ---------------------------------------------
def hauptmenue_anzeige():
    print("╔" + "═" * 50 + "╗")
    print("║" + "  CHARAKTER-RPG - HAUPTMENÜ".ljust(50) + "║")
    print("╚" + "═" * 50 + "╝")

    print(f"{BLAU}--- Charakter ---{RESET}")
    print("1. Erstellen")
    print("2. Anzeigen")
    print("3. Löschen")
    print(f"\n{ROT}--- Abenteuer ---{RESET}")
    print("4. Kampfmodus")
    print("5. Storymodus")
    print(f"\n{GOLD}--- Sonstiges ---{RESET}")
    print("6. Shop")
    print("7. Beenden")

    startup_option = input("\n>: ")
    return startup_option


# ---------------------------------------------
# Speichern
# ---------------------------------------------
def speichern(liste):
    with open(DATEIPFAD, "w") as datei:
        json.dump(liste, datei)

# ---------------------------------------------
# Kampf
# ---------------------------------------------
def kampf(spieler, gegner):
    print(f"\n⚔️  {BLAU}{spieler['name']}{RESET} (Lvl {spieler['level']}) vs. {ROT}{gegner['name']}{RESET} (Lvl {gegner['level']})\n")

    while spieler["leben"] > 0 and gegner["leben"] > 0:
        # Spieler greift an
        if spieler["mana"] >= 40 and random.random() < 0.3:
            schaden = random.randint(10, 20) + (spieler["staerke"] // 5)
            spieler["mana"] -= 40
            aktion_text = f"{BLAU}{spieler['name']}{RESET} führt einen {GOLD}Spezialangriff{RESET} aus und verursacht {ROT}{schaden}{RESET} Schaden!\n"
        else:
            schaden = random.randint(0, 5) + (spieler["staerke"] // 10)
            aktion_text = f"{BLAU}{spieler['name']}{RESET} greift an und verursacht {ROT}{schaden}{RESET} Schaden!\n"

        gegner["leben"] -= schaden

        kampf_anzeige(spieler, gegner, aktion_text)
        if not SCHNELLER_KAMPF:
            time.sleep(2)

        if gegner["leben"] <= 0:
            break

        # Gegner greift an
        if gegner["mana"] >= 40 and random.random() < 0.3:
            schaden = random.randint(10, 20) + (gegner["staerke"] // 5)
            gegner["mana"] -= 40
            aktion_text = f"{ROT}{gegner['name']}{RESET} führt einen {GOLD}Spezialangriff{RESET} aus und verursacht {ROT}{schaden}{RESET} Schaden!\n"
        else:
            schaden = random.randint(0, 5) + (gegner["staerke"] // 10)
            aktion_text = f"{ROT}{gegner['name']}{RESET} greift an und verursacht {ROT}{schaden}{RESET} Schaden!\n"

        spieler["leben"] -= schaden

        kampf_anzeige(spieler, gegner, aktion_text)

        if not SCHNELLER_KAMPF:
            time.sleep(2)

    print("\n--- Kampf beendet! ---")

    if spieler["leben"] > 0:
        print(f"{GRUEN}{spieler['name']} hat gewonnen!{RESET}")

        # XP & Münzen
        verhaeltnis = gegner["level"] / spieler["level"]
        xp_gewonnen = int(gegner["level"] * 100 * verhaeltnis)
        muenzen_gewonnen = int(gegner["level"] * 10 * verhaeltnis)

        spieler["xp"] += xp_gewonnen
        spieler["muenzen"] += muenzen_gewonnen

        print(f"{spieler['name']} erhält {xp_gewonnen} XP! (Gesamt: {spieler['xp']})")
        print(f"{spieler['name']} erhält {GOLD}{muenzen_gewonnen} Münzen{RESET}! (Gesamt: {spieler['muenzen']})")

        # Level-Up Prüfung
        xp_benoetigt = spieler["level"] * 100
        while spieler["xp"] >= xp_benoetigt:
            spieler["xp"] -= xp_benoetigt
            spieler["level"] += 1
            spieler["max_leben"] += 10
            spieler["staerke"] += 5
            print(f"{GELB}{spieler['name']} ist auf Level {spieler['level']} aufgestiegen!{RESET}")
            xp_benoetigt = spieler["level"] * 100

    else:
        print(f"{ROT}{gegner['name']} hat gewonnen!{RESET}")



# ---------------------------------------------
# Migration alter Charakter-Daten
# ---------------------------------------------
def charakter_migrieren(charakter):
    if "tempo" in charakter and "staerke" not in charakter:
        charakter["staerke"] = charakter.pop("tempo")
    if "stärke" in charakter and "staerke" not in charakter:
        charakter["staerke"] = charakter.pop("stärke")
    if "max_leben" not in charakter:
        charakter["max_leben"] = charakter["leben"]
    if "muenzen" not in charakter:
        charakter["muenzen"] = 0
    if "xp" not in charakter:
        charakter["xp"] = 0
    if "level" not in charakter:
        charakter["level"] = 1
    if "max_mana" not in charakter:
        charakter["max_mana"] = charakter["mana"]
    if "story_fortschritt" not in charakter:
        charakter["story_fortschritt"] = 0


# ---------------------------------------------
# Programmstart
# ---------------------------------------------
os.system("cls" if os.name == "nt" else "clear")

try:
    with open(DATEIPFAD, "r") as datei:
        alle_charaktere = json.load(datei)
except (FileNotFoundError, json.JSONDecodeError):
    alle_charaktere = []

# Alte Charaktere an aktuelles Format anpassen
for charakter in alle_charaktere:
    charakter_migrieren(charakter)


# ---------------------------------------------
# Hauptmenü
# ---------------------------------------------
while True:
    startup_option = hauptmenue_anzeige()

    if startup_option == "1":  # Charakter erstellen
        neuer_charakter = charakter_erstellen()
        alle_charaktere.append(neuer_charakter)
        speichern(alle_charaktere)

    elif startup_option == "2":  # Alle Charaktere anzeigen
        os.system("cls" if os.name == "nt" else "clear")
        alle_charakter_anzeigen(alle_charaktere)

    elif startup_option == "3":  # Alle Charaktere löschen
        os.system("cls" if os.name == "nt" else "clear")
        alle_charaktere = []
        speichern(alle_charaktere)

    elif startup_option == "4":  # Kampfmodus
        os.system("cls" if os.name == "nt" else "clear")

        if len(alle_charaktere) == 0:
            print("Du hast noch keine Charaktere!")
        else:
            alle_charakter_anzeigen(alle_charaktere)
            auswahl = input("Welcher Charakter soll auf eine Reise gehen? (Name eingeben)\n\n>: ")

            spieler = charakter_finden(alle_charaktere, auswahl)

            if spieler is None:
                print("Charakter nicht gefunden!")
            else:
                while True:
                    print("\n=== GEBIETE ===\n")
                    for index, gebiet in enumerate(gebiete):
                        print(f"{index + 1}. {gebiet['name']} (Level {gebiet['min_level']}-{gebiet['max_level']})")

                    gebiet_auswahl = input("\nWelches Gebiet? (Nummer)\n\n>: ")

                    if not gebiet_auswahl.isdigit():
                            print("Ungültige Eingabe!")
                            continue
                    
                    gebiet_index = int(gebiet_auswahl) - 1

                    if gebiet_index < 0 or gebiet_index >= len(gebiete):
                        print("Dieses Gebiet gibt es nicht!")
                        continue

                    gewaehltes_gebiet = gebiete[gebiet_index]
                    break
                    
                while True:
                    gegner = gegner_erstellen(gewaehltes_gebiet["min_level"], gewaehltes_gebiet["max_level"])
                    kampf(spieler, gegner)
                    speichern(alle_charaktere)

                    weiter = input("\nWeiterkämpfen? (j/n)\n\n>: ").upper()
                    if weiter != "J":
                        break

    elif startup_option == "5":  # Storymodus
            CLEAR # Konsole Clearen

            if len(alle_charaktere) == 0:
                print("Du hast noch keine Charaktere!")
            else:
                alle_charakter_anzeigen(alle_charaktere)
                auswahl = input("Welcher Charakter soll der Story folgen? (Name eingeben)\n\n>: ")

                spieler = charakter_finden(alle_charaktere, auswahl)

                if spieler is None:
                    print("Charakter nicht gefunden!")
                else:
                    CLEAR # Konsole Clearen
                    # Hier kommt die eigentliche Story-Logik
                    if spieler["story_fortschritt"] >= len(story_quests):
                        print(f"{GELB}{spieler['name']} hat bereits alle Quests abgeschlossen!{RESET}")
                    else:
                        aktuelle_quest = story_quests[spieler["story_fortschritt"]]
                        print(f"\n=== {aktuelle_quest['titel']} ===\n")
                        print(aktuelle_quest["text"])
                        print(f"\nGegner-Level: {aktuelle_quest['boss_level']}")

                        start = input("\nMöchtest du gegen diesen Gegner antreten? (j/n)\n\n>: ").upper()
                        
                        if start == "J":
                            # Normale Gegner zuerst
                            for i in range(aktuelle_quest["anzahl_gegner"]):
                                print(f"\n--- Gegner {i + 1} von {aktuelle_quest['anzahl_gegner']} ---")
                                gegner = gegner_erstellen(aktuelle_quest["gegner_min_level"], aktuelle_quest["gegner_max_level"])
                                kampf(spieler, gegner)
                                time.sleep(1)

                            # Danach der Boss
                            print(f"\n--- BOSS ---")
                            boss = gegner_erstellen(aktuelle_quest["boss_level"], aktuelle_quest["boss_level"])
                            kampf(spieler, boss)

                        if spieler["leben"] > 0:
                            spieler["story_fortschritt"] += 1
                            spieler["muenzen"] += aktuelle_quest["belohnung_muenzen"]
                            print(f"\n{GRUEN}Quest abgeschlossen! {spieler['name']} erhält {aktuelle_quest['belohnung_muenzen']} Münzen!{RESET}")

                            speichern(alle_charaktere)

    elif startup_option == "6":  # Shop
        os.system("cls" if os.name == "nt" else "clear")

        if len(alle_charaktere) == 0:
            print("Du hast noch keine Charaktere!")
        else:
            alle_charakter_anzeigen(alle_charaktere)
            auswahl = input("Welcher Charakter soll in den Shop gehen? (Name eingeben)\n\n>: ")

            spieler = charakter_finden(alle_charaktere, auswahl)

            if spieler is None:
                print("Charakter nicht gefunden!")
            else:
                while True:
                    os.system("cls" if os.name == "nt" else "clear")
                    print(f"=== SHOP === (Münzen: {GOLD}{spieler['muenzen']}{RESET})\n")

                    for index, item in enumerate(shop_items):
                        print(f"{index + 1}. {item['name']} - {item['preis']} Münzen")

                    auswahl_item = input("\nWelches Item möchtest du kaufen? (Nummer eingeben, oder 0 für zurück)\n\n>: ")

                    if auswahl_item == "0":
                        break

                    if not auswahl_item.isdigit():
                        print("Ungültige Eingabe!")
                        continue

                    index = int(auswahl_item) - 1

                    if index < 0 or index >= len(shop_items):
                        print("Dieses Item gibt es nicht!")
                        continue

                    gewaehltes_item = shop_items[index]

                    if spieler["muenzen"] >= gewaehltes_item["preis"]:
                        spieler["muenzen"] -= gewaehltes_item["preis"]

                        # Effekt anwenden
                        if gewaehltes_item["typ"] == "heilung":
                            spieler["leben"] = min(spieler["leben"] + gewaehltes_item["wert"], spieler["max_leben"])
                            print(f"{GRUEN}{spieler['name']} wurde um {gewaehltes_item['wert']} Leben geheilt!{RESET}")

                        elif gewaehltes_item["typ"] == "staerke_boost":
                            spieler["staerke"] += gewaehltes_item["wert"]
                            print(f"{GRUEN}{spieler['name']}s Stärke ist um {gewaehltes_item['wert']} gestiegen!{RESET}")

                        elif gewaehltes_item["typ"] == "max_leben_boost":
                            spieler["max_leben"] += gewaehltes_item["wert"]
                            spieler["leben"] += gewaehltes_item["wert"]
                            print(f"{GRUEN}{spieler['name']}s maximales Leben ist um {gewaehltes_item['wert']} gestiegen!{RESET}")

                        elif gewaehltes_item["typ"] == "mana_auffuellen":
                            spieler["mana"] = min(spieler["mana"] + gewaehltes_item["wert"], spieler["max_mana"])
                            print(f"{GRUEN}{spieler['name']} hat sein Mana um {gewaehltes_item['wert']} Punkte aufgefüllt!{RESET}")

                        speichern(alle_charaktere)
                    else:
                        print(f"{ROT}Nicht genug Münzen!{RESET}")

                    time.sleep(2)

    elif startup_option == "7":  # Beenden
        os.system("cls" if os.name == "nt" else "clear")
        break

    else:
        print("Ungültige Eingabe!")