"""Conversion-path contract (plenum lens 19, built 2026-11-16).

Pins the reply path from a free tool or research page to a conversation: a
keepable response time, a question route that needs no company or product
name, a four-field scope brief, a next step on every listed tool, and nothing
that would break the "nothing leaves your browser, no email gate" promise.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _read(rel: str) -> str:
    return (DOCS / rel).read_text(encoding="utf-8")


def _visible_text(html: str) -> str:
    body = html.split("<main", 1)[1].split("</main>", 1)[0]
    body = re.sub(r"<script\b.*?</script>", " ", body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.DOTALL)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))


# Phrases the lens ruled out of the public conversion path.
BANNED_PUBLIC_PHRASES = (
    "within 24 hours",
    "same day",
    "same-day",
    "anonymous",
    "answered personally",
    "newsletter",
    "subscribe",
    "book a call",
    "calendly",
)


def test_contact_states_a_keepable_response_time_and_a_hidden_away_line() -> None:
    html = _read("contact.html")
    text = _visible_text(html)
    assert "within three working days" in text
    # The away line exists for the founder to switch on, and ships switched off.
    away = re.search(r'<p class="away" id="away"([^>]*)>', html)
    assert away, "away line missing"
    assert "hidden" in away.group(1).split(), "away line must be hidden by default"
    for phrase in BANNED_PUBLIC_PHRASES:
        assert phrase not in html.lower(), phrase


def test_contact_has_a_question_route_that_needs_no_names() -> None:
    html = _read("contact.html")
    assert 'id="ask"' in html
    assert "You do not need to name your company, product or study" in html
    # Questions and corrections use support@, scope requests use info@.
    assert re.search(r'href="mailto:support@clinicops\.dk\?subject=Question%3A%20[^"]*"', html)
    assert 'href="mailto:info@clinicops.dk?subject=ClinicOps%20scope%20request"' in html
    # The template is visible on the page for webmail users without a mail handler.
    assert "The situation, as a pattern (no names needed):" in html
    # No claim of anonymity; the page says the address identifies the sender.
    assert "Your email address shows who you are" in html
    # One Danish sentence, marked as Danish.
    assert re.search(r'<p lang="da">Skriv gerne på dansk[^<]*</p>', html)


def test_contact_carries_no_imprint_until_the_domicile_decision_is_made() -> None:
    """D1 (domicile, tax ID) is open. The contact page must not publish it yet."""
    text = _visible_text(_read("contact.html"))
    for token in ("NIF", "Tax ID", "domicile", "Egedalsv", "Iskandar"):
        assert token not in text, token


def test_privacy_notice_gives_a_retention_number_for_enquiries() -> None:
    html = _read("privacy-notice/index.html")
    section = html.split("<h2>7. Retention</h2>", 1)[1].split("</section>", 1)[0]
    assert "deleted twelve months after the last contact" in section
    assert "as long as needed" in section  # client files keep the legal-obligation wording


def test_auto_reply_document_exists_and_matches_the_site_commitment() -> None:
    doc = (ROOT / "03_OPERATIONS" / "MAILBOX_AUTO_REPLY_AND_RESPONSE_TIME.md").read_text(encoding="utf-8")
    assert "within three working days" in doc
    assert "tre hverdage" in doc
    assert "CM-01" in doc and "CM-05" in doc
    assert "Please do not send patient-identifiable data or confidential files by email" in doc
