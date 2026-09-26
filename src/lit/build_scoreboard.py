"""Join mitigation papers and their rubric scores into one scoreboard.

Reads  notes/mitigation/scores/papers_*.json  (paper records, one list per file)
       notes/mitigation/scores/scores_*.json  (rubric scores keyed by paper_id)
Writes notes/mitigation/scores/scoreboard.json

Checks: >= 10 papers per method, every paper scored, every score an integer 1-5
with a reason, no DOI repeated within a method. Exits non-zero on a failed check
unless --allow-gaps is given.
"""
import argparse
import glob
import json
import os
import sys
from collections import defaultdict

DIR = "notes/mitigation/scores"
CRITERIA = ["reproducibility", "effectiveness", "cost", "time", "environment"]
MIN_PAPERS = 10

METHODS = {
    "peroxide": ("Hydrogen / calcium peroxide", "Oxidizers", ["ours"]),
    "curcumin": ("Curcumin and plant compounds", "Natural compounds", ["ours"]),
    "mixing": ("Mixing, aeration, bubbles", "Physical", ["ours"]),
    "seaweed": ("Seaweed allelopathy", "Biological", ["ours"]),
    "shellfish": ("Shellfish / filter feeders", "Biological", ["ours"]),
    "clay": ("Clay / flocculation", "Flocculation", ["ruled_out"]),
    "p_inactivation": ("Phosphorus inactivation (alum, lanthanum)", "Nutrient control", ["ruled_out"]),
    "nutrient_reduction": ("Nutrient / watershed reduction", "Nutrient control", []),
    "ultrasound": ("Ultrasound", "Physical", []),
    "biomanipulation": ("Biomanipulation / grazers", "Biological", []),
    "algicidal_microbes": ("Algicidal bacteria, viruses, fungi", "Biological", []),
    "barley_straw": ("Barley straw", "Natural compounds", []),
    "oxidation": ("Ozone, UV, photocatalysis", "Oxidizers", []),
    "copper": ("Copper and chemical algicides", "Chemical", []),
    "shading": ("Shading / light limitation", "Physical", []),
}


def load(pattern):
    out = []
    for path in sorted(glob.glob(os.path.join(DIR, pattern))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        out.extend(data if isinstance(data, list) else data.get("scores", []))
    return out


def build_calibration(papers_by_id):
    """Compare the scorers' independent scores on the shared calibration papers."""
    files = sorted(glob.glob(os.path.join(DIR, "calib_s*.json")))
    if not files:
        return None
    runs = []
    for path in files:
        with open(path, encoding="utf-8") as f:
            runs.append({s["paper_id"]: s for s in json.load(f)})
    ids = sorted(set.intersection(*(set(r) for r in runs)))
    rows, spreads = [], []
    for pid in ids:
        row = {"paper_id": pid, "title": papers_by_id.get(pid, {}).get("title", pid)}
        for c in CRITERIA:
            vals = [r[pid][c] for r in runs]
            row[c] = vals
            spreads.append(max(vals) - min(vals))
        rows.append(row)
    n = len(spreads) or 1
    within1 = sum(s <= 1 for s in spreads)
    summary = (f"{len(runs)} scorers each scored the same {len(ids)} papers. "
               f"{within1} of {len(spreads)} criterion scores ({within1 / n:.0%}) agreed within 1 point; "
               f"{sum(s == 0 for s in spreads)} matched exactly; "
               f"{len(spreads) - within1} differed by 2 or more.")
    return {"summary": summary, "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-gaps", action="store_true")
    args = ap.parse_args()

    papers = load("papers_*.json")
    scores = {}
    for s in load("scores_*.json"):
        if "paper_id" in s:
            scores[s["paper_id"]] = s

    types = {}
    types_path = os.path.join(DIR, "study_types.json")
    if os.path.exists(types_path):
        with open(types_path, encoding="utf-8") as f:
            types = json.load(f)

    problems = []
    by_method = defaultdict(list)
    for p in papers:
        t = types.get(p["id"], {})
        p["study_type"] = t.get("type", "efficacy")
        p["study_note"] = t.get("note", "")
        if p["method"] not in METHODS:
            problems.append(f"unknown method {p['method']} on {p['id']}")
            continue
        s = scores.get(p["id"])
        if s is None:
            problems.append(f"unscored {p['id']}")
        else:
            for c in CRITERIA:
                v = s.get(c)
                if not isinstance(v, int) or not 1 <= v <= 5:
                    problems.append(f"bad {c}={v!r} on {p['id']}")
                if not (s.get("reasons") or {}).get(c):
                    problems.append(f"no reason for {c} on {p['id']}")
            p["scores"] = {c: s.get(c) for c in CRITERIA}
            p["reasons"] = s.get("reasons", {})
        by_method[p["method"]].append(p)

    methods = []
    for slug, (name, family, tags) in METHODS.items():
        ps = by_method.get(slug, [])
        dois = [p["doi"].lower() for p in ps if p.get("doi")]
        if len(dois) != len(set(dois)):
            problems.append(f"duplicate DOI within {slug}")
        if len(ps) < MIN_PAPERS:
            problems.append(f"{slug}: only {len(ps)} papers")
        # Rank a method on the papers that test it against algae; safety, mechanism,
        # feeding and misfiled papers stay listed but don't set the method's score.
        scored = [p for p in ps if "scores" in p and p["study_type"] == "efficacy"]
        roll = {}
        for c in CRITERIA:
            vals = [p["scores"][c] for p in scored if isinstance(p["scores"][c], int)]
            roll[c] = {
                "mean": round(sum(vals) / len(vals), 2) if vals else None,
                "min": min(vals) if vals else None,
                "max": max(vals) if vals else None,
            }
        means = [roll[c]["mean"] for c in CRITERIA if roll[c]["mean"] is not None]
        n = len(ps) or 1
        methods.append({
            "slug": slug, "name": name, "family": family, "tags": tags,
            "n_papers": len(ps),
            "n_efficacy": len(scored),
            "share_field": round(sum(p.get("setting") == "field" for p in ps) / n, 2),
            "share_negative": round(sum(bool(p.get("negative_result")) for p in ps) / n, 2),
            "share_full_text": round(sum(p.get("access") == "full" for p in ps) / n, 2),
            "share_marine": round(sum(p.get("freshwater_or_marine") in ("marine", "brackish", "both") for p in ps) / n, 2),
            "rollup": roll,
            "overall": round(sum(means) / len(means), 2) if means else None,
            "papers": ps,
        })

    all_dois = defaultdict(set)
    for p in papers:
        if p.get("doi"):
            all_dois[p["doi"].lower()].add(p["method"])
    for doi, ms in all_dois.items():
        if len(ms) > 1:
            print(f"note: {doi} appears under {sorted(ms)}")

    calibration = build_calibration({p["id"]: p for p in papers})

    out = {"criteria": CRITERIA, "methods": methods, "calibration": calibration,
           "n_papers": sum(m["n_papers"] for m in methods)}
    with open(os.path.join(DIR, "scoreboard.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    for m in sorted(methods, key=lambda m: -(m["overall"] or 0)):
        print(f"{m['slug']:20s} n={m['n_papers']:3d} overall={m['overall']}")
    print(f"total papers: {out['n_papers']}")
    if problems:
        print(f"{len(problems)} problems:")
        for p in problems[:40]:
            print("  " + p)
        if not args.allow_gaps:
            sys.exit(1)


if __name__ == "__main__":
    main()
