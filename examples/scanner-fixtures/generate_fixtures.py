#!/usr/bin/env python3
"""Generate FICTIONAL Regulatory Integrity Scanner fixtures.

Every manufacturer, device and identifier here is invented ("Example MedTech A/B",
"Exempla ..."). Basic UDI-DI values are prefixed FIC. UDI-DIs use the reserved-looking
prefix 0950600 with a valid GS1 mod-10 check digit. source_url / evidence links are
deliberately blank (repo rule: no placeholder URLs).

Usage:
  python3 generate_fixtures.py small              # rewrite the committed small fixtures
  python3 generate_fixtures.py large OUT.csv [N]  # ~2,000 rows (default), not committed
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEAD = ["basic_udi_di", "udi_di", "trade_name", "model", "risk_class", "manufacturer_srn",
        "certificate_no", "sscp_ref", "doc_version", "source_system", "source_role",
        "evidence_ref", "evidence_date", "owner"]


def gs1(body13: str) -> str:
    s = sum(int(c) * (3 if i % 2 == 0 else 1) for i, c in enumerate(body13))
    return body13 + str((10 - s % 10) % 10)


def udi(n: int) -> str:
    return gs1("0950600%06d" % n)


def row(vals):
    return ",".join('"%s"' % v.replace('"', '""') if ("," in v or '"' in v) else v for v in vals)


def rec(n, name, cls="IIb", cert="CERT-A-1001", sscp="SSCP-A-v3", ver="IFU-12", sys_="RIM",
        role="authoritative", ev="RIM export r12", date="2026-09-10", owner="RA Ops",
        model=None, srn="DK-MF-000000001"):
    return [f"FICBU{n:05d}", udi(n), name, model or f"EX-{n}", cls, srn, cert, sscp, ver, sys_,
            role, ev, date, owner]


def write(name, header, rows, sep="\n", enc="utf-8"):
    text = sep.join([row(header)] + [row(r) for r in rows]) + sep
    (HERE / name).write_bytes(text.encode(enc))


def small():
    clean = []
    for n, nm, cls in [(1, "Exempla Flow Monitor", "IIb"), (2, "Exempla Sense Patch", "IIa"),
                       (3, "Exempla Dose Assist", "IIb")]:
        clean.append(rec(n, nm, cls))
        clean.append(rec(n, nm, cls, sys_="EUDAMED", role="observed", ev="Public record extract", date="2026-09-12"))
        clean.append(rec(n, nm, cls, sys_="Label register", role="observed", ev="Label register row %d" % n, date="2026-09-11", owner="QA"))
    write("clean.csv", HEAD, clean)

    # Odd header names, different order, extra columns (Example MedTech B export style)
    mh = ["Owner / Responsible", "Extra: internal note", "Product Name", "Basic UDI-DI", "Catalogue No", "Device Class",
          "UDI-DI", "Source", "Source Role", "Evidence URL/Ref", "As-of Date", "Certificate", "SSCP", "Document Revision", "Unused column"]
    m = []
    for n, nm in [(11, "Exempla Airflow Sensor"), (12, "Exempla Airflow Sensor Kit")]:
        for sys_, role, d in [("RIM", "authoritative", "2026-09-01"), ("EUDAMED", "observed", "2026-09-03")]:
            m.append(["RA Ops", "ignore me", nm, f"FICBU{n:05d}", f"EX-{n}", "IIa", udi(n), sys_, role,
                      "Export r3", d, "CERT-B-2002", "SSCP-B-v1", "IFU-4", ""])
    write("messy-headers.csv", mh, m)

    # Same Basic UDI-DI: conflicting certificate / SS(C)P / document version, no authority for one group
    c = [rec(21, "Exempla Pump A", cert="CERT-A-3001", sscp="SSCP-A-v4", ver="IFU-7"),
         rec(21, "Exempla Pump A", cert="CERT-A-3009", sscp="SSCP-A-v3", ver="IFU-6", sys_="EUDAMED", role="observed", ev="Public record extract"),
         rec(21, "Exempla Pump A", cert="CERT-A-3001", sscp="SSCP-A-v4", ver="IFU-7", sys_="Label register", role="observed", ev="Row 8", owner="QA"),
         # two authoritative sources disagree
         rec(22, "Exempla Pump B", cert="CERT-A-3100", sscp="SSCP-A-v2", ver="IFU-3"),
         rec(22, "Exempla Pump B", cert="CERT-A-3101", sscp="SSCP-A-v2", ver="IFU-3", sys_="QMS", ev="QMS export"),
         # no authoritative row at all
         rec(23, "Exempla Pump C", sys_="EUDAMED", role="observed", ev="Public record extract"),
         # duplicate UDI-DI in one source
         rec(24, "Exempla Pump D"), rec(24, "Exempla Pump D")]
    write("conflicting.csv", HEAD, c)

    mv = [rec(31, "Exempla Valve A"),
          rec(31, "Exempla Valve A", sys_="EUDAMED", role="observed", ev="", date="2026-09-12"),        # no evidence ref
          rec(32, "", cls=""),                                                                              # blank name + class
          rec(32, "Exempla Valve B", cls="Class 2b", sys_="EUDAMED", role="observed", date=""),             # odd class, no date
          rec(33, "Exempla Valve C", cert="", sscp="", owner="")]                                           # blank cert/sscp/owner
    write("missing-values.csv", HEAD, mv)

    # bad fixtures
    (HERE / "bad-empty.csv").write_bytes(b"")
    (HERE / "bad-headers-only.csv").write_bytes((row(HEAD) + "\n").encode())
    latin = [rec(41, "Blåbær Åndedrætsmonitor"), rec(41, "Blåbær Åndedrætsmonitor", sys_="EUDAMED", role="observed")]
    write("bad-encoding-latin1.csv", HEAD, latin, enc="latin-1")
    dup = ["basic_udi_di", "udi_di", "trade_name", "trade_name", "source_system", "source_role"]
    write("bad-duplicate-headers.csv", dup, [[f"FICBU00051", udi(51), "Exempla A", "Exempla B", "RIM", "authoritative"],
                                              [f"FICBU00051", udi(51), "Exempla A", "Exempla A", "EUDAMED", "observed"]])
    ragged = [row(HEAD), row(rec(61, "Exempla Ragged")[:9]), row(rec(61, "Exempla Ragged", sys_="EUDAMED", role="observed") + ["extra", "cells"])]
    (HERE / "bad-ragged.csv").write_text("\n".join(ragged) + "\n")
    # semicolon-delimited (common Excel export in Danish locale)
    write("bad-semicolon.csv", HEAD, [rec(71, "Exempla Semi")], sep="\n")
    p = HERE / "bad-semicolon.csv"
    p.write_text(p.read_text().replace(",", ";"))


def large(out, n=2000):
    lines = [row(HEAD)]
    groups = -(-n // 3)
    k = 0
    for g in range(1, groups + 1):
        nm = f"Exempla Series {g:04d}"
        base = rec(100000 + g, nm)
        obs = rec(100000 + g, nm, sys_="EUDAMED", role="observed", ev="Public record extract", date="2026-09-12")
        lab = rec(100000 + g, nm, sys_="Label register", role="observed", ev=f"Row {g}", owner="QA")
        if g % 17 == 0: obs[2] = nm + " Plus"          # trade-name drift
        if g % 23 == 0: lab[12] = ""                    # missing date
        if g % 29 == 0: obs[6] = "CERT-A-9999"          # certificate drift
        if g % 31 == 0: base[4] = "Class 9"             # unrecognised class
        for r in (base, obs, lab):
            if k < n:
                lines.append(row(r)); k += 1
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "large":
        large(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2000)
    else:
        small()
