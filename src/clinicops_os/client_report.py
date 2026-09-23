from __future__ import annotations

from datetime import date
from html import escape

from .transition_report import PortfolioRow, portfolio_payload


def _text(value: object) -> str:
    text = str(value).strip() if value is not None else ""
    return escape(text or "—")


# Design language shared with the public site ("ledger", see design/DESIGN_TOKENS.md).
# Standalone reports (private client bundles) embed the token subset below so they never
# depend on network resources; the public specimen links /site.css instead and only
# receives COMPONENT_CSS, so both surfaces render the same components from one source.
STANDALONE_TOKEN_CSS = """:root{color-scheme:light dark;--bg:#f6f7f5;--surface:#fff;--surface-2:#eef1ee;--text:#0f1a17;--muted:#556360;--border:#e0e6e2;--border-strong:#cdd6d1;--accent:#0f5c52;--warn:#8a5a13;--r:6px;--font:"Geist","Geist Fallback",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--mono:"Geist Mono",ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace}
@media(prefers-color-scheme:dark){:root{--bg:#0d1211;--surface:#131a18;--surface-2:#182120;--text:#e6ece9;--muted:#98a6a1;--border:#25302d;--border-strong:#374541;--accent:#4fd8c4;--warn:#e0ad61}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font);font-size:1rem;line-height:1.58;-webkit-font-smoothing:antialiased}
main.wrap{max-width:1180px;margin:0 auto;padding:clamp(24px,5vw,56px) clamp(18px,4vw,32px)}
h1{font-size:clamp(1.7rem,3.4vw,2.4rem);line-height:1.12;letter-spacing:-.03em;margin:0 0 .4em;max-width:26em}
h2{font-size:1.3rem;line-height:1.2;letter-spacing:-.015em;margin:2.2em 0 .7em;padding-top:.9em;border-top:1px solid var(--border-strong)}
a{color:var(--accent)}
table{width:100%;border-collapse:collapse;font-size:.92rem}
th,td{padding:10px 12px 10px 0;text-align:left;vertical-align:top;border-bottom:1px solid var(--border)}
th{font-family:var(--mono);font-weight:500;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--border-strong)}
@media(prefers-contrast:more){:root{--border:#8a9691;--border-strong:#4b5854}}
"""

SITE_SHELL_CSS = "main.wrap{padding-top:clamp(40px,6vw,72px)}\n"

COMPONENT_CSS = """.notice{border:0;border-left:2px solid var(--warn);border-radius:0 var(--r) var(--r) 0;background:var(--surface-2);padding:18px 22px;margin:24px 0;max-width:53.04em}
.notice h2{margin:0 0 .5em;padding-top:0;border-top:0;font-size:1.3rem}
.notice p:last-child{margin-bottom:0}
.summary{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));margin:24px 0;border-top:1px solid var(--border-strong);border-bottom:1px solid var(--border)}
.summary section{padding:16px 14px 14px 0;margin-right:14px;border-right:1px solid var(--border);font-size:.85rem;color:var(--muted);line-height:1.35}
.summary section:last-child{border-right:0;margin-right:0}
.summary strong{display:block;margin-bottom:6px;font-family:var(--mono);font-weight:500;font-size:clamp(1.6rem,3vw,2.2rem);letter-spacing:-.03em;line-height:1.1;color:var(--text);font-variant-numeric:tabular-nums}
@media(max-width:820px){.summary{grid-template-columns:repeat(2,minmax(0,1fr))}.summary section:nth-child(2n){border-right:0;margin-right:0}.summary section{border-bottom:1px solid var(--border)}}
.table-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.table-scroll table{min-width:960px;display:table;margin:0}
td:first-child{font-family:var(--mono);font-variant-numeric:tabular-nums}
main ul,main ol{max-width:47.74em;padding-left:1.2rem}
main li{margin:.4em 0}
.report-foot{margin-top:32px;font-size:.9rem;color:var(--muted);max-width:47.74em}
.table-scroll:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
@media print{main.wrap{padding:0}.summary{break-inside:avoid}.table-scroll{overflow:visible}.table-scroll table{min-width:0;font-size:8.5pt}.table-scroll th,.table-scroll td{padding-right:6px}a{color:inherit;text-decoration:none}}
"""


def render_client_html(
    rows: list[PortfolioRow],
    *,
    as_of: date,
    title: str = "ClinicOps Portfolio Transition Brief",
    site_shell: bool = False,
) -> str:
    """Render a self-contained client-facing HTML projection of the portfolio contract.

    The report is deliberately static and dependency-free so it can be shared through a
    controlled client workspace today and placed behind an authenticated portal later.

    With ``site_shell=True`` the report links the public site stylesheet (``/site.css``)
    instead of embedding the standalone tokens, so the public specimen and private
    deliverables are produced by the same renderer and the same components.
    """

    payload = portfolio_payload(rows, as_of=as_of)
    summary = payload["summary"]
    payload_rows = payload["rows"]
    limitations = payload["limitations"]

    table_rows: list[str] = []
    for row in payload_rows:
        source = str(row["source_url"]).strip()
        source_html = (
            f'<a href="{escape(source, quote=True)}" rel="noopener noreferrer">source</a>'
            if source
            else "—"
        )
        table_rows.append(
            "<tr>"
            f"<td>{_text(row['priority_score'])}</td>"
            f"<td>{_text(row['company'])}</td>"
            f"<td>{_text(row['device'])}</td>"
            f"<td>{_text(row['actor_role'])}</td>"
            f"<td>{_text(row['registration_type'])}</td>"
            f"<td>{_text(row['certificate_expiry'])}</td>"
            f"<td>{_text(row['danish_market'])}</td>"
            f"<td>{_text(row['workstream'])}</td>"
            f"<td>{source_html}</td>"
            "</tr>"
        )

    head_css = SITE_SHELL_CSS + COMPONENT_CSS if site_shell else STANDALONE_TOKEN_CSS + COMPONENT_CSS
    limitations_html = "".join(f"<li>{_text(item)}</li>" for item in limitations)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>
{head_css}</style>
</head>
<body>
<main id="main" tabindex="-1" class="wrap">
<div class="report-head">
<h1>{escape(title)}</h1>
<p><strong>As of:</strong> {as_of.isoformat()}</p>
<div class="notice">Work-plan screening from supplied or public metadata. Priority is operator triage only; this report is not a compliance determination, legal conclusion, or full-register EUDAMED audit.</div>
</div>

<h2>Portfolio snapshot</h2>
<div class="summary">
<section><strong>{summary['records_reviewed']}</strong>records reviewed</section>
<section><strong>{summary['manufacturer_legacy']}</strong>legacy / legacy-screened MF records</section>
<section><strong>{summary['manufacturer_mdr_non_legacy']}</strong>MDR / non-legacy MF records</section>
<section><strong>{summary['procedure_pack_role']}</strong>PR / system-procedure-pack records</section>
<section><strong>{summary['danish_market_confirmed']}</strong>confirmed Danish-market rows</section>
</div>

<h2>Prioritised work plan</h2>
<div class="table-scroll" tabindex="0" role="region" aria-label="Prioritised work plan table"><table aria-label="Prioritised work plan">
<thead><tr><th scope="col">Priority</th><th scope="col">Company</th><th scope="col">Device</th><th scope="col">Role</th><th scope="col">Registration</th><th scope="col">Certificate expiry</th><th scope="col">Danish market</th><th scope="col">Workstream</th><th scope="col">Evidence source</th></tr></thead>
<tbody>{''.join(table_rows)}</tbody>
</table></div>

<h2>Interpretation constraints</h2>
<ul>{limitations_html}</ul>

<h2>Recommended next questions</h2>
<ol>
<li>Which legacy manufacturer-role devices have the earliest verified certificate or transition dates?</li>
<li>Which of those devices are confirmed for the relevant target market?</li>
<li>Who owns Basic UDI-DI, SS(C)P, market-language availability and change-control work for each transition?</li>
<li>Which evidence is already controlled internally and which must be obtained from the manufacturer, authorised representative or notified body?</li>
</ol>

<footer class="report-foot">Generated by ClinicOps from the validated portfolio bundle contract. Human regulatory review remains required before external reliance on device-specific conclusions.</footer>
</main>
</body>
</html>
"""
