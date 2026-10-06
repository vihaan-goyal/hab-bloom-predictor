"""Turn snowball.csv into Part 2 of notes/HAB_MITIGATION_LITERATURE.md and a full CSV.

Strict filter for the MD: the title itself mentions controlling/removing/treating blooms or algae.
Everything (including loosely related papers) goes to notes/HAB_MITIGATION_SOURCES.csv.
"""
import os
import re

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\Users\vihaa\hab-bloom-predictor"
MD = os.path.join(REPO, "notes", "HAB_MITIGATION_LITERATURE.md")
CSV_OUT = os.path.join(REPO, "notes", "HAB_MITIGATION_SOURCES.csv")
PER_CAT = 70

CTRL_TITLE = re.compile(r"control|mitigat|remov|suppress|inhibit|treat|algicid|algaecid|flocculat|"
                        r"coagulat|eliminat|restor|kill|terminat|inactivat|prevent|combat|"
                        r"manag|reduc", re.I)
ALGAE_TITLE = re.compile(r"bloom|cyanobacteri|microcystis|alga|dinoflagellate|red tide|karenia|"
                         r"phytoplankton|planktothrix|anabaena|aphanizomenon|eutroph|cyanotoxin|"
                         r"microcystin", re.I)

df = pd.read_csv(os.path.join(HERE, "snowball.csv"))
df["title"] = df["title"].fillna("").str.replace(r"<[^>]+>", "", regex=True).str.strip()
df = df[df.title.str.len() > 0].drop_duplicates("title")

strict = df.title.str.contains(CTRL_TITLE) & df.title.str.contains(ALGAE_TITLE)
df["in_md"] = strict
df.to_csv(CSV_OUT, index=False)

def title_setting(t):
    t = t.lower()
    if re.search(r"review|overview|perspective|synthesis|meta-analysis|state of the art|advances", t):
        return "Review / synthesis"
    if re.search(r"whole[- ]lake|entire lake|in situ|field|reservoir|lake [a-z]|pond|full[- ]scale|case study", t):
        return "Field (from title)"
    if re.search(r"mesocosm|enclosure|microcosm", t):
        return "Mesocosm / enclosure"
    return "Not stated (no abstract)"


df.loc[~df.has_abstract, "setting"] = df.loc[~df.has_abstract, "title"].map(title_setting)
md_df = df[df.in_md].copy()
order = (md_df.groupby("category").size().sort_values(ascending=False)).index.tolist()
if "Other / general" in order:
    order.remove("Other / general")
    order.append("Other / general")


def esc(s):
    return str(s).replace("|", "/").replace("\n", " ").strip()


lines = []
lines.append("\n\n---\n\n# Part 2: citation snowball (automatically compiled)\n")
lines.append(
    f"Built 2026-09-24 with the OpenAlex scholarly database. It starts from the 16 peer-reviewed "
    f"seed papers in Part 1, takes each one's reference list and its most-cited citing papers "
    f"(level 1), then does the same for the 70 most-cited relevant level-1 papers (level 2). "
    f"That produced **{len(df):,} bloom-related papers**. The **{len(md_df):,}** below are the ones "
    f"whose *title* is about controlling, removing or treating blooms or algae. The full list, "
    f"including the loosely related papers, is in `notes/HAB_MITIGATION_SOURCES.csv`.\n")
lines.append(
    "**How to read these entries.** They were compiled by a script, not read by a person:\n"
    "- **Method**, **setting** (field / mesocosm / lab / review / modelling) and **result** are "
    "taken automatically from the abstract. The result is quoted from the abstract's own sentences.\n"
    "- **Environment** and **teen-reproducible** are judgements for the method *category* (see "
    "Part 1), not for the individual paper.\n"
    "- **Effective?** is a keyword reading of the abstract: ≥50% removal/reduction, negative words "
    "such as \"no significant\" or \"recovered\", or neither.\n"
    "- Open and read a paper before citing it. A handful may be off-topic where a title matched "
    "the keywords by accident.\n")
lines.append(f"Abstracts were available for {int(md_df.has_abstract.sum()):,} of these {len(md_df):,} papers. "
             f"Many publishers don't share abstracts with OpenAlex, so the rest show only the title and "
             f"link, with the setting guessed from the title where possible.\n")
lines.append(f"Showing up to {PER_CAT} per method, most-cited first.\n")

counts = md_df.category.value_counts()
lines.append("| Method category | Papers in this list | Field studies | Environment | Teen-reproducible? |")
lines.append("|---|---|---|---|---|")
for cat in order:
    sub = md_df[md_df.category == cat]
    lines.append(f"| {cat} | {len(sub)} | {int((sub.setting == 'Field').sum())} | "
                 f"{esc(sub.environment.iloc[0])} | {esc(sub.teen.iloc[0])} |")

for cat in order:
    sub = md_df[md_df.category == cat].sort_values("cited_by", ascending=False)
    shown = sub.head(PER_CAT)
    lines.append(f"\n## {cat} ({len(sub)} papers{'; top ' + str(PER_CAT) + ' shown' if len(sub) > PER_CAT else ''})\n")
    lines.append(f"**Environment (category):** {sub.environment.iloc[0]}. "
                 f"**Teen-reproducible (category):** {sub.teen.iloc[0]}.\n")
    for _, r in shown.iterrows():
        year = int(r.year) if pd.notna(r.year) else "n.d."
        if not r.has_abstract:
            res = "no abstract available in OpenAlex; open the link"
        elif isinstance(r.result_excerpt, str) and r.result_excerpt:
            res = esc(r.result_excerpt)
        else:
            res = "no quantitative result stated in the abstract"
        lines.append(f"- **[{esc(r.title)}]({r.url})** ({year}; cited {int(r.cited_by)}×)")
        lines.append(f"  - Setting: {r.setting}. Effective? {r.effective}.")
        lines.append(f"  - Result (from abstract): {res}")

with open(MD, "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"all related: {len(df)}; in MD (strict): {len(md_df)}; shown: "
      f"{sum(min(PER_CAT, n) for n in counts.values)}")
print(counts.to_string())
print(md_df.setting.value_counts().to_string())
