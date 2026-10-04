"""Stap 3: verstuur de samenvatting als e-mail via Resend.

Gebruikt summarize.py voor de data en de samenvatting, en verstuurt
het resultaat via de Resend API naar EMAIL_TO uit je .env.

Gebruik:
    python send_email.py
"""

import html
import os
import sys
from datetime import datetime

import requests

from fetch_matches import TZ
from summarize import build_overview, summarize

RESEND_URL = "https://api.resend.com/emails"
# Zonder eigen domein mag je alleen vanaf dit adres versturen,
# en alleen naar het e-mailadres van je eigen Resend-account.
AFZENDER = "Eredivisie Bot <onboarding@resend.dev>"


def send_email(subject: str, body_html: str) -> None:
    api_key = os.getenv("RESEND_API_KEY")
    to = os.getenv("EMAIL_TO")
    if not api_key or not to:
        sys.exit("RESEND_API_KEY of EMAIL_TO ontbreekt in je .env-bestand.")

    response = requests.post(
        RESEND_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"from": AFZENDER, "to": [to], "subject": subject, "html": body_html},
        timeout=15,
    )
    if not response.ok:
        sys.exit(f"Fout van Resend ({response.status_code}): {response.text}")
    print(f"E-mail verstuurd naar {to}!")


def main() -> None:
    overview = build_overview()  # laadt ook de .env
    summary = summarize(overview)
    print("Samenvatting:\n" + summary + "\n")

    today = datetime.now(TZ)
    body = (
        f"<p>{html.escape(summary)}</p>"
        "<hr>"
        f"<pre>{html.escape(overview)}</pre>"
    )
    send_email(f"⚽ Eredivisie-update {today:%d-%m-%Y}", body)


if __name__ == "__main__":
    main()
