from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_STATES = {
    "aligned",
    "mismatch_signal",
    "missing_evidence",
    "not_applicable",
    "unresolved",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def validate(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data.get("schema_version") == "1.0", "schema_version must be 1.0")
    require(isinstance(data.get("packet_id"), str) and data["packet_id"], "packet_id required")
    require(data.get("status") in {"draft", "review_ready", "closed"}, "invalid packet status")
    require(isinstance(data.get("workstream"), str) and data["workstream"], "workstream required")

    change = data.get("change")
    require(isinstance(change, dict), "change object required")
    for field in ("title", "source_reference", "summary"):
        require(isinstance(change.get(field), str) and change[field].strip(), f"change.{field} required")

    scope = data.get("scope")
    require(isinstance(scope, dict), "scope object required")
    require(isinstance(scope.get("population_basis"), str) and scope["population_basis"].strip(), "scope.population_basis required")

    surfaces = data.get("surfaces")
    require(isinstance(surfaces, list) and surfaces, "at least one surface required")
    seen_ids: set[str] = set()
    unresolved_ids: set[str] = set()
    for index, surface in enumerate(surfaces, start=1):
        require(isinstance(surface, dict), f"surface {index} must be an object")
        surface_id = surface.get("surface_id")
        require(isinstance(surface_id, str) and surface_id, f"surface {index}: surface_id required")
        require(surface_id not in seen_ids, f"duplicate surface_id: {surface_id}")
        seen_ids.add(surface_id)
        require(isinstance(surface.get("name"), str) and surface["name"].strip(), f"{surface_id}: name required")
        state = surface.get("evidence_state")
        require(state in ALLOWED_STATES, f"{surface_id}: invalid evidence_state {state!r}")
        require(isinstance(surface.get("owner"), str) and surface["owner"].strip(), f"{surface_id}: owner required")
        require(isinstance(surface.get("closure_evidence"), str) and surface["closure_evidence"].strip(), f"{surface_id}: closure_evidence required")
        require(isinstance(surface.get("decision_required"), bool), f"{surface_id}: decision_required must be boolean")
        if state in {"mismatch_signal", "missing_evidence", "unresolved"} or surface["decision_required"]:
            unresolved_ids.add(surface_id)

    queue = data.get("unresolved_queue")
    require(isinstance(queue, list), "unresolved_queue must be a list")
    queue_ids: set[str] = set()
    for index, item in enumerate(queue, start=1):
        require(isinstance(item, dict), f"unresolved item {index} must be an object")
        surface_id = item.get("surface_id")
        require(surface_id in seen_ids, f"unresolved item references unknown surface_id: {surface_id!r}")
        require(isinstance(item.get("question"), str) and item["question"].strip(), f"{surface_id}: question required")
        require(isinstance(item.get("next_owner"), str) and item["next_owner"].strip(), f"{surface_id}: next_owner required")
        queue_ids.add(surface_id)
    require(unresolved_ids <= queue_ids, f"unresolved queue missing surfaces: {sorted(unresolved_ids - queue_ids)}")

    boundary = data.get("review_boundary")
    require(isinstance(boundary, dict), "review_boundary required")
    require(boundary.get("compliance_finding") is False, "public/synthetic packet must not assert a compliance finding")
    require(isinstance(boundary.get("automation_role"), str) and boundary["automation_role"].strip(), "review_boundary.automation_role required")
    require(isinstance(boundary.get("human_role"), str) and boundary["human_role"].strip(), "review_boundary.human_role required")

    validation = data.get("validation")
    require(isinstance(validation, dict), "validation object required")
    if validation.get("fixture_type") == "sanitized_synthetic":
        require(validation.get("real_world_validation_evidence") is False, "synthetic fixture cannot claim real-world validation")
        require(validation.get("scalability_evidence") is False, "synthetic fixture cannot claim scalability")

    return {
        "status": "VALID",
        "packet_id": data["packet_id"],
        "surface_count": len(surfaces),
        "unresolved_count": len(queue),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a ClinicOps change-control packet")
    parser.add_argument("path", nargs="?", default="examples/change_control_packet.example.json")
    args = parser.parse_args()
    result = validate(Path(args.path))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
