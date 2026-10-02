"""Stap 1: haal Eredivisie-wedstrijden op via football-data.org (v4).

Toont de uitslagen van gisteren en het programma van vandaag en morgen.

Gebruik:
    python fetch_matches.py          # leesbaar overzicht
    python fetch_matches.py --raw    # ruwe JSON van de API
"""

import json
import os
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

API_URL = "https://api.football-data.org/v4/competitions/DED/matches"
TZ = ZoneInfo("Europe/Amsterdam")


def get_token() -> str:
    load_dotenv()  # leest .env in de huidige map
    token = os.getenv("FOOTBALL_DATA_TOKEN")
    if not token:
        sys.exit("Geen FOOTBALL_DATA_TOKEN gevonden. Maak een .env-bestand aan (zie .env.example).")
    return token


def fetch_matches(token: str, date_from: date, date_to: date) -> dict:
    response = requests.get(
        API_URL,
        headers={"X-Auth-Token": token},
        params={"dateFrom": date_from.isoformat(), "dateTo": date_to.isoformat()},
        timeout=15,
    )
    if response.status_code == 429:
        sys.exit("429: te veel verzoeken (gratis tier = 10 per minuut). Wacht even.")
    if not response.ok:
        # Bij een fout (bv. ongeldige token) geeft de API zelf een uitleg mee
        sys.exit(f"Fout {response.status_code}: {response.text}")
    return response.json()


def local_date(match: dict) -> date:
    # utcDate ziet eruit als "2026-10-01T18:45:00Z"
    utc = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
    return utc.astimezone(TZ).date()


def format_match(match: dict) -> str:
    home = match["homeTeam"]["shortName"] or match["homeTeam"]["name"]
    away = match["awayTeam"]["shortName"] or match["awayTeam"]["name"]
    score = match["score"]["fullTime"]
    if match["status"] == "FINISHED":
        return f"{home} - {away}  {score['home']}-{score['away']}"
    kickoff = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00")).astimezone(TZ)
    extra = "" if match["status"] in ("SCHEDULED", "TIMED") else f"  [{match['status']}]"
    return f"{kickoff:%H:%M}  {home} - {away}{extra}"


def main() -> None:
    today = datetime.now(TZ).date()
    yesterday, tomorrow = today - timedelta(days=1), today + timedelta(days=1)

    # Eén dag extra marge aan het eind, en daarna filteren we zelf op de
    # Nederlandse datum. Zo maakt tijdzone-verschil met UTC niet uit.
    data = fetch_matches(get_token(), yesterday, tomorrow + timedelta(days=1))

    if "--raw" in sys.argv:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    sections = [
        ("Uitslagen gisteren", yesterday),
        ("Programma vandaag", today),
        ("Programma morgen", tomorrow),
    ]
    for title, day in sections:
        print(f"\n{title} ({day:%d-%m-%Y})")
        matches = [m for m in data.get("matches", []) if local_date(m) == day]
        if not matches:
            print("  geen wedstrijden")
        for match in matches:
            print("  " + format_match(match))


if __name__ == "__main__":
    main()
