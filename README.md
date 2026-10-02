# Eredivisie uitslagen & programma

Testproject: Eredivisie-data ophalen → laten samenvatten door Claude → mailen via Resend.

## Stap 1: wedstrijden ophalen (klaar)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # Windows: copy .env.example .env
# open .env en vul je football-data.org token in

python fetch_matches.py          # leesbaar overzicht
python fetch_matches.py --raw    # ruwe JSON
```

Je token staat alleen in `.env`. Dat bestand staat in `.gitignore`, dus het komt nooit in Git/GitHub.
