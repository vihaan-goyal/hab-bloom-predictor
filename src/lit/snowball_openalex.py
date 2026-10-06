"""Citation snowball for HAB mitigation literature, using the OpenAlex API (no key).

Seeds are the peer-reviewed papers in notes/HAB_MITIGATION_LITERATURE.md. Level 1 takes each
seed's references (backward) and its most-cited citing papers (forward). Level 2 repeats that for
the most-cited relevant level-1 papers. A paper is kept only if its title or abstract is about
blooms/algae AND about controlling them. Each kept paper is tagged with a method category, the
setting (field / mesocosm / lab / review), and a results excerpt drawn from its abstract.

Outputs (next to this script): cache.json, snowball.csv
"""
import json
import os
import re
import time

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache.json")
API = "https://api.openalex.org/works"
FIELDS = "id,doi,title,publication_year,cited_by_count,abstract_inverted_index,referenced_works,type"

SEEDS = [  # (label, doi or title search)
    ("H2O2 whole lake", "doi:10.1016/j.watres.2011.11.016"),
    ("Curcumin K. brevis", "doi:10.3390/w16101458"),
    ("Floc and Sink tropical", "doi:10.3390/toxins13060405"),
    ("Algicidal bacteria review", "doi:10.3389/fmicb.2022.871177"),
    ("Calcium peroxide K. brevis", "title:An effective algaecide for the targeted destruction of Karenia brevis"),
    ("Modified clay review", "title:Mitigation of harmful algal blooms using modified clays: Theory, mechanisms, and applications"),
    ("Clay flocculation Sengco", "title:Controlling harmful algal blooms through clay flocculation"),
    ("Floc and Lock", "title:Controlling eutrophication by combined bloom precipitation and sediment phosphorus inactivation"),
    ("Alum longevity Huser", "title:Longevity and effectiveness of aluminum addition to reduce sediment phosphorus release and restore lake water quality"),
    ("Lake Barleber", "title:Suppression of bloom-forming colonial cyanobacteria by phosphate precipitation"),
    ("Artificial mixing Visser", "title:Artificial mixing prevents nuisance blooms of the cyanobacterium Microcystis in Lake Nieuwe Meer"),
    ("Ultrasound review Park", "title:Recent advances in ultrasonic treatment: Challenges and field applications for controlling harmful algal blooms"),
    ("Biomanipulation Jeppesen", "title:Biomanipulation as a restoration tool to combat eutrophication"),
    ("Barley straw review", "title:Barley (Hordeum vulgare)-induced growth inhibition of algae: a review"),
    ("Curcumin mesocosm", "title:Lessons learned from mesocosm experiments with curcumin"),
    ("Lurling mitigation review", "title:Mitigating cyanobacterial blooms: how effective are 'effective microorganisms'"),
]

BLOOM = re.compile(r"\b(bloom|cyanobacteri|cyanoHAB|blue-green alga|microcystis|planktothrix|anabaena|"
                   r"aphanizomenon|dolichospermum|karenia|red tide|dinoflagellate|harmful alga|"
                   r"phytoplankton|algae|algal|microalga|cochlodinium|margalefidinium|prymnesium|"
                   r"heterosigma|alexandrium|pseudo-nitzschia|eutrophic)", re.I)
CONTROL = re.compile(r"\b(control|mitigat|remov|suppress|inhibit|treat|flocculat|coagulat|algicid|"
                     r"algaecid|kill|terminat|eliminat|restor|manag|prevent|degrad|sedimentat|"
                     r"inactivat|lanthanum|alum\b|peroxide|ozon|ultrason|biomanipulat)", re.I)

CATEGORIES = [  # first match wins; order matters
    ("Hydrogen peroxide / peroxides", r"hydrogen peroxide|\bH2O2\b|calcium peroxide|percarbonate|peroxymonosulfate|persulfate"),
    ("Clay / flocculation / coagulation", r"\bclay|flocculat|coagula|polyaluminium|polyaluminum|\bPAC\b|chitosan|loess|kaolin|montmorillonite|bentonite(?! .{0,20}lanthanum)"),
    ("Phosphorus inactivation (alum, lanthanum)", r"\balum\b|aluminium sulfate|aluminum sulfate|lanthanum|phoslock|phosphorus inactivation|sediment capping|capping|iron addition|P inactivation"),
    ("Copper / chemical algicides", r"copper|CuSO4|endothall|diquat|algaecide|algicide(?!.{0,20}bacteri)"),
    ("Ultrasound", r"ultrason|ultrasound|sonication"),
    ("Mixing / aeration / destratification", r"artificial mixing|destratif|aeration|bubble plume|hypolimnetic oxygenation|oxygenation|flushing|hydraulic"),
    ("Biomanipulation / grazers / filter feeders", r"biomanipulat|fish removal|piscivor|zooplankton|daphnia|grazing|grazer|bivalve|mussel|oyster|clam|filter-feed|filter feed"),
    ("Algicidal bacteria / viruses / fungi", r"algicidal bacteri|bacteri(um|a) .{0,30}(lys|algicid)|cyanophage|virus|phage|fung(us|i|al)|protozoa|biological control|microorganism"),
    ("Plant / natural compounds (barley, allelopathy, curcumin)", r"barley|straw|allelopath|plant extract|curcumin|polyphenol|tannin|flavonoid|essential oil|macrophyte|natural product|natural compound|extract"),
    ("Oxidation / UV / photocatalysis / electrochemical", r"ozon|\bUV\b|ultraviolet|photocataly|electrochem|electrolys|plasma|advanced oxidation|chlorin|permanganate|ferrate|TiO2"),
    ("Nanomaterials", r"\bnano|graphene"),
    ("Nutrient / watershed reduction", r"nutrient (load|reduction)|load reduction|wastewater|watershed|diversion|dredg|nitrogen reduction|phosphorus reduction"),
]

ENV = {
    "Hydrogen peroxide / peroxides": "Short-lived: breaks down to water and oxygen within days; selective for cyanobacteria at low doses",
    "Clay / flocculation / coagulation": "Adds material that settles to the bottom and is not retrieved; coagulants often add aluminium",
    "Phosphorus inactivation (alum, lanthanum)": "Adds aluminium, lanthanum or iron to the lake permanently, by design",
    "Copper / chemical algicides": "Persistent chemicals; copper is toxic to non-target organisms and accumulates in sediment",
    "Ultrasound": "No chemicals; effects on non-target organisms unclear",
    "Mixing / aeration / destratification": "No chemicals; changes stratification and uses energy",
    "Biomanipulation / grazers / filter feeders": "Deliberately changes the food web",
    "Algicidal bacteria / viruses / fungi": "Introduces living organisms; non-target effects poorly known",
    "Plant / natural compounds (barley, allelopathy, curcumin)": "Natural compounds; low persistence, but decomposing plant material can lower oxygen",
    "Oxidation / UV / photocatalysis / electrochemical": "Can form by-products (e.g. bromate, chlorinated compounds); needs equipment",
    "Nanomaterials": "Nanoparticle release and toxicity concerns",
    "Nutrient / watershed reduction": "Treats the cause; changes land use or wastewater, not the lake directly",
    "Other / general": "Depends on method; see abstract",
}
TEEN = {
    "Hydrogen peroxide / peroxides": "Yes: jar tests with drugstore 3% H2O2 and a non-toxic culture",
    "Clay / flocculation / coagulation": "Bench only (the counselor ruled out clay)",
    "Phosphorus inactivation (alum, lanthanum)": "No",
    "Copper / chemical algicides": "Not recommended (toxic chemicals)",
    "Ultrasound": "Partly: lab test with an ultrasonic cleaner",
    "Mixing / aeration / destratification": "Demonstration only (tall tube + air pump)",
    "Biomanipulation / grazers / filter feeders": "Field no; jar grazing tests with Daphnia are possible",
    "Algicidal bacteria / viruses / fungi": "No (microbiology lab, biosafety forms)",
    "Plant / natural compounds (barley, allelopathy, curcumin)": "Yes: jar tests with a non-toxic culture",
    "Oxidation / UV / photocatalysis / electrochemical": "Mostly no (equipment, by-products); a UV-lamp jar test is possible with care",
    "Nanomaterials": "No",
    "Nutrient / watershed reduction": "No (policy / engineering scale)",
    "Other / general": "Depends",
}

RESULT_SENT = re.compile(r"[^.]*\d[^.]*\b(remov|reduc|inhibit|decreas|efficien|kill|suppress|declin|lower|"
                         r"eliminat|prevent|recover|increas)[^.]*\.", re.I)
NEG = re.compile(r"\b(no significant|not significant|ineffective|did not|failed|no effect|limited effect|"
                 r"recovered|re-?emerge|rebound)", re.I)
POS_PCT = re.compile(r"(\d{2,3}(?:\.\d+)?)\s?%")


def load_cache():
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    return {}


cache = load_cache()


def save_cache():
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f)


def get(params, key):
    if key in cache:
        return cache[key]
    for attempt in range(5):
        try:
            r = requests.get(API, params=params, timeout=60)
            if r.status_code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            r.raise_for_status()
            out = r.json()
            cache[key] = out
            time.sleep(0.15)
            return out
        except requests.RequestException:
            time.sleep(3 * (attempt + 1))
    return {"results": []}


def abstract(w):
    inv = w.get("abstract_inverted_index") or {}
    if not inv:
        return ""
    pos = {}
    for word, idx in inv.items():
        for i in idx:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def relevant(w):
    text = (w.get("title") or "") + " " + abstract(w)
    return bool(BLOOM.search(text)) and bool(CONTROL.search(text))


def resolve_seed(spec):
    kind, val = spec.split(":", 1)
    if kind == "doi":
        res = get({"filter": f"doi:{val}", "select": FIELDS}, "seed:" + spec)["results"]
    else:
        res = get({"search": val, "select": FIELDS, "per-page": 3}, "seed:" + spec)["results"]
    return res[0] if res else None


def fetch_ids(ids):
    out = []
    ids = [i.split("/")[-1] for i in ids]
    for k in range(0, len(ids), 50):
        chunk = ids[k:k + 50]
        res = get({"filter": "openalex_id:" + "|".join(chunk), "select": FIELDS, "per-page": 50},
                  "ids:" + "|".join(chunk))["results"]
        out.extend(res)
    return out


def citing(wid, n=200):
    short = wid.split("/")[-1]
    return get({"filter": f"cites:{short}", "select": FIELDS, "sort": "cited_by_count:desc",
                "per-page": n}, f"cites:{short}:{n}")["results"]


def expand(w, n_cite):
    refs = fetch_ids(w.get("referenced_works") or [])
    cit = citing(w["id"], n_cite)
    return [x for x in refs + cit if relevant(x)]


def categorize(text):
    for name, pat in CATEGORIES:
        if re.search(pat, text, re.I):
            return name
    return "Other / general"


def setting(title, abs_):
    t = (title + " " + abs_).lower()
    if "review" in title.lower() or "meta-analysis" in t:
        return "Review / synthesis"
    if re.search(r"whole[- ]lake|in situ|field (trial|study|application|test|experiment)|reservoir|lake .{0,20}(treat|appl)|pond (treat|appl)|full[- ]scale", t):
        return "Field"
    if re.search(r"mesocosm|enclosure|limnocorral|microcosm", t):
        return "Mesocosm / enclosure"
    if re.search(r"model|simulat", t) and not re.search(r"laborator|culture", t):
        return "Modelling"
    return "Lab"


def result_excerpt(abs_):
    sents = [m.group(0).strip() for m in RESULT_SENT.finditer(abs_)]
    ex = " ".join(sents[:2])
    return (ex[:350] + "...") if len(ex) > 350 else ex


def effective_flag(abs_, ex):
    if not abs_:
        return "Unknown (no abstract)"
    if NEG.search(ex or abs_[:800]):
        return "Mixed / limited (per abstract)"
    pcts = [float(p) for p in POS_PCT.findall(ex)]
    if pcts and max(pcts) >= 50:
        return "Reported effective (per abstract)"
    if ex:
        return "Some effect reported (per abstract)"
    return "Not stated in abstract"


def main():
    papers = {}
    level = {}
    seed_of = {}
    seeds = []
    for label, spec in SEEDS:
        w = resolve_seed(spec)
        if not w:
            print(f"  seed not found: {label}")
            continue
        print(f"  seed {label}: {w['title'][:80]} ({w['publication_year']}, cited {w['cited_by_count']})")
        seeds.append(w)
        papers[w["id"]] = w
        level[w["id"]] = 0
        seed_of[w["id"]] = label
    save_cache()

    l1 = []
    for s in seeds:
        for x in expand(s, 200):
            if x["id"] not in papers:
                papers[x["id"]] = x
                level[x["id"]] = 1
                seed_of[x["id"]] = seed_of[s["id"]]
                l1.append(x)
        save_cache()
    print(f"level 1: {len(l1)} relevant papers")

    top_l1 = sorted(l1, key=lambda w: -w.get("cited_by_count", 0))[:70]
    n2 = 0
    for i, s in enumerate(top_l1):
        for x in expand(s, 100):
            if x["id"] not in papers:
                papers[x["id"]] = x
                level[x["id"]] = 2
                seed_of[x["id"]] = seed_of[s["id"]]
                n2 += 1
        if i % 10 == 0:
            save_cache()
            print(f"  level 2: expanded {i + 1}/{len(top_l1)}, +{n2} so far")
    save_cache()
    print(f"level 2: {n2} relevant papers")

    rows = []
    for wid, w in papers.items():
        abs_ = abstract(w)
        title = w.get("title") or ""
        ex = result_excerpt(abs_)
        cat = categorize(title + " " + abs_)
        rows.append(dict(
            title=title, year=w.get("publication_year"), cited_by=w.get("cited_by_count", 0),
            url=w.get("doi") or wid, openalex=wid, level=level[wid], via_seed=seed_of[wid],
            category=cat, setting=setting(title, abs_), environment=ENV[cat],
            result_excerpt=ex, effective=effective_flag(abs_, ex), teen=TEEN[cat],
            has_abstract=bool(abs_)))
    df = pd.DataFrame(rows).sort_values(["category", "cited_by"], ascending=[True, False])
    df.to_csv(os.path.join(HERE, "snowball.csv"), index=False)
    print(f"TOTAL {len(df)} papers; by category:")
    print(df.category.value_counts().to_string())
    print(df.setting.value_counts().to_string())


if __name__ == "__main__":
    main()
