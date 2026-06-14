"""
Build human-review tables for leakage candidates.

Inputs:
- results/leakage_audit.json

Outputs:
- results/leakage_review_decisions.csv
- dataset/metadata/deleak_split_plan_v1_6.csv
- docs/LEAKAGE_REVIEW_PROTOCOL.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results"
METADATA_DIR = BASE_DIR / "dataset" / "metadata"
DOCS_DIR = BASE_DIR / "docs"


def review_status(hamming: int) -> str:
    if hamming <= 1:
        return "likely_duplicate_review_required"
    if hamming <= 3:
        return "near_duplicate_review_required"
    return "possible_near_duplicate_review_required"


def recommended_action(pair: dict) -> str:
    splits = {pair["a_split"], pair["b_split"]}
    if "test" in splits:
        return "exclude_or_group_before_final_test_claim"
    if "val" in splits:
        return "group_before_model_selection_claim"
    return "group_in_future_split"


def main() -> None:
    audit_path = RESULTS_DIR / "leakage_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    pairs = audit.get("near_duplicate_pairs", [])

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    review_csv = RESULTS_DIR / "leakage_review_decisions.csv"
    plan_csv = METADATA_DIR / "deleak_split_plan_v1_6.csv"

    fieldnames = [
        "pair_id", "hamming", "a", "a_split", "a_species",
        "b", "b_split", "b_species", "review_status",
        "human_decision", "recommended_action", "notes",
    ]
    rows = []
    for idx, pair in enumerate(pairs, start=1):
        rows.append({
            "pair_id": f"leak-{idx:03d}",
            "hamming": pair["hamming"],
            "a": pair["a"],
            "a_split": pair["a_split"],
            "a_species": pair["a_species"],
            "b": pair["b"],
            "b_split": pair["b_split"],
            "b_species": pair["b_species"],
            "review_status": review_status(pair["hamming"]),
            "human_decision": "",
            "recommended_action": recommended_action(pair),
            "notes": "",
        })

    with review_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with plan_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "pair_id", "path", "current_split", "species",
            "recommended_v1_6_handling",
        ])
        writer.writeheader()
        for row in rows:
            for side in ("a", "b"):
                writer.writerow({
                    "pair_id": row["pair_id"],
                    "path": row[side],
                    "current_split": row[f"{side}_split"],
                    "species": row[f"{side}_species"],
                    "recommended_v1_6_handling": row["recommended_action"],
                })

    protocol = [
        "# Leakage Review Protocol",
        "",
        "Use this protocol before claiming a de-leaked v1.6 split.",
        "",
        "1. Open `results/leakage_near_duplicate_pairs.jpg`.",
        "2. Fill `results/leakage_review_decisions.csv`.",
        "3. Mark each pair as `confirmed_duplicate`, `same_observation_likely`, `visually_similar_but_ok`, or `false_positive`.",
        "4. Build a new split only after confirmed/same-observation pairs are grouped.",
        "5. Retrain or re-evaluate before replacing v1.5 metrics.",
        "",
        "Do not move files manually without updating `dataset/metadata/deleak_split_plan_v1_6.csv`.",
    ]
    (DOCS_DIR / "LEAKAGE_REVIEW_PROTOCOL.md").write_text(
        "\n".join(protocol) + "\n", encoding="utf-8"
    )

    print(f"Wrote {review_csv}")
    print(f"Wrote {plan_csv}")


if __name__ == "__main__":
    main()
