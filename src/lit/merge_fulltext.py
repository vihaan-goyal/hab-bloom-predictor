"""Merge full-text reading patches into the mitigation paper records.

Reads  notes/mitigation/scores/fulltext/*.json  ({paper_id: {status, source_url,
       updates, key_details, discrepancy}})
Writes the matching notes/mitigation/scores/papers_*.json in place, and
       notes/mitigation/scores/fulltext/changed_ids.json (papers read in full,
       which need re-scoring).

Only papers with status "full_read" are changed: access becomes "full", the
listed fields are replaced, and key_details / discrepancy are stored. Other
statuses (no_access, not_free, blocked, failed) are only counted.
"""
import glob
import json
import os
from collections import Counter

DIR = "notes/mitigation/scores"
FIELDS = {"organism", "freshwater_or_marine", "setting", "scale", "dose", "duration",
          "result", "effect_pct", "env_effects", "negative_result"}


def main():
    patches = {}
    status = Counter()
    for path in sorted(glob.glob(os.path.join(DIR, "fulltext", "*.json"))):
        if path.endswith("changed_ids.json"):
            continue
        with open(path, encoding="utf-8") as f:
            for pid, patch in json.load(f).items():
                status[patch.get("status", "?")] += 1
                if patch.get("status") == "full_read":
                    patches[pid] = patch

    changed = []
    for path in sorted(glob.glob(os.path.join(DIR, "papers_*.json"))):
        with open(path, encoding="utf-8") as f:
            papers = json.load(f)
        touched = False
        for p in papers:
            patch = patches.get(p["id"])
            if not patch:
                continue
            for k, v in (patch.get("updates") or {}).items():
                if k in FIELDS:
                    p[k] = v
            p["access"] = "full"
            p["key_details"] = patch.get("key_details", "")
            if patch.get("discrepancy"):
                p["fulltext_discrepancy"] = patch["discrepancy"]
            changed.append(p["id"])
            touched = True
        if touched:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(papers, f, ensure_ascii=False, indent=1)

    with open(os.path.join(DIR, "fulltext", "changed_ids.json"), "w", encoding="utf-8") as f:
        json.dump(sorted(changed), f, indent=1)
    print("patch statuses:", dict(status))
    print("records upgraded to full text:", len(changed))
    missing = sorted(set(patches) - set(changed))
    if missing:
        print("patched ids not found in any papers file:", missing)


if __name__ == "__main__":
    main()
