import argparse
from .identifier import classify_identifier
from .claim_guard import check_claim


def id_check():
    p = argparse.ArgumentParser()
    p.add_argument("identifier")
    args = p.parse_args()
    a = classify_identifier(args.identifier)
    print(f"kind: {a.kind}")
    print(f"legacy_screen: {a.legacy_screen}")
    print(f"gs1_valid: {a.gs1_valid}")
    print(f"note: {a.note}")


def claim_check():
    p = argparse.ArgumentParser()
    p.add_argument("text")
    args = p.parse_args()
    flags = check_claim(args.text)
    if not flags:
        print("No encoded ClinicOps claim-guard flags triggered.")
        return
    for f in flags:
        print(f"[{f.severity}] {f.pattern}: {f.guidance}")
