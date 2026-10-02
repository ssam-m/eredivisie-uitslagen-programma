"""Stap 2: laat Claude een luchtige Nederlandse samenvatting maken.

Gebruikt de functies uit fetch_matches.py om de wedstrijden op te halen,
en stuurt het overzicht naar de Claude API.

Gebruik:
    python summarize.py
"""

import sys
from datetime import datetime, timedelta

import anthropic

from fetch_matches import TZ, fetch_matches, format_match, get_token, local_date

MODEL = "claude-sonnet-4-6"
DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]

INSTRUCTIE = """Je bent een enthousiaste Nederlandse voetbalverslaggever.
Vat het Eredivisie-overzicht hieronder samen in 3 tot 5 zinnen, in het Nederlands,
met een luchtige toon. Noem de uitslagen van gisteren en de wedstrijden van vandaag
en morgen. Gebruik alleen de gegevens uit het overzicht: verzin geen uitslagen,
doelpuntenmakers of andere feiten. Zijn er geen wedstrijden, maak daar dan een
grappige opmerking over. Geef alleen de samenvatting terug, zonder kopje."""


def build_overview() -> str:
    """Haalt de wedstrijden op en maakt er een leesbaar tekstoverzicht van."""
    today = datetime.now(TZ).date()
    yesterday, tomorrow = today - timedelta(days=1), today + timedelta(days=1)
    data = fetch_matches(get_token(), yesterday, tomorrow + timedelta(days=1))

    lines = []
    for title, day in [
        ("Uitslagen gisteren", yesterday),
        ("Programma vandaag", today),
        ("Programma morgen", tomorrow),
    ]:
        lines.append(f"{title} ({DAGEN[day.weekday()]} {day:%d-%m-%Y}):")
        matches = [m for m in data.get("matches", []) if local_date(m) == day]
        lines += ["  " + format_match(m) for m in matches] or ["  geen wedstrijden"]
    return "\n".join(lines)


def summarize(overview: str) -> str:
    client = anthropic.Anthropic()  # leest ANTHROPIC_API_KEY (via .env)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=INSTRUCTIE,
            messages=[{"role": "user", "content": overview}],
        )
    except anthropic.AuthenticationError:
        sys.exit("Je ANTHROPIC_API_KEY klopt niet. Controleer je .env-bestand.")
    except anthropic.APIStatusError as e:
        sys.exit(f"Fout van de Claude API ({e.status_code}): {e.message}")
    except anthropic.APIConnectionError:
        sys.exit("Geen verbinding met de Claude API. Check je internet.")

    return "".join(block.text for block in response.content if block.type == "text")


def main() -> None:
    overview = build_overview()  # laadt ook de .env (via get_token)
    print("Ruwe data:\n" + overview + "\n")
    print("Samenvatting van Claude:\n" + summarize(overview))


if __name__ == "__main__":
    main()
