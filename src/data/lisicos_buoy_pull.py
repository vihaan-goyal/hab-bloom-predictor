"""
lisicos_buoy_pull.py
--------------------
Stage 1 of the buoy work: pull LISICOS continuous-buoy chlorophyll from the
NERACOOS ERDDAP, QC it, aggregate 15-minute data to daily, and report coverage.

Why: the ship-survey series samples every ~21 days, so 99% of forward windows
hold <=1 reading and most "errors" are unverifiable. The moored buoys sample every
15 minutes at western sites (Execution Rocks, Western LIS), exactly where the FPs
and the sparsest sampling coincide. This pull is the prerequisite for adjudicating
those single-reading false positives against high-cadence truth.

Design choices:
  - Dataset IDs are DISCOVERED from the ERDDAP, not hardcoded, then filtered to the
    LIS water-quality buoys. The chlorophyll VARIABLE name is discovered per dataset
    by reading its metadata (it differs across sondes), so nothing is guessed.
  - QC drops non-physical values and despikes with a rolling-median filter (buoy
    fluorometers foul and spike). This is basic QC, not a substitute for the
    provider's flags; coverage and quality still need eyeballing after.
  - Output is one tidy daily file you can merge or use to re-label western stations.

Run from repo root (needs network):
    python lisicos_buoy_pull.py
    python lisicos_buoy_pull.py --datasets UCONN_EXRX_WQ_SUR UCONN_WLIS_WQ_SUR
    python lisicos_buoy_pull.py --start 1993-01-01 --end 2025-12-31
"""

import argparse
import io
import sys

import numpy as np
import pandas as pd

try:
    import requests
except ImportError:
    requests = None

BASE = "https://data.neracoos.org/erddap"  # ERDDAP 2.x; .org/www is 1.82
SITE_TOKENS = ("EXRX", "WLIS", "CLIS")  # western -> central LIS buoys


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base", default=BASE)
    p.add_argument("--datasets", nargs="+", default=None,
                   help="override dataset IDs instead of auto-discovering")
    p.add_argument("--start", default="1993-01-01")
    p.add_argument("--end", default="2025-12-31")
    p.add_argument("--spike-window", type=int, default=5,
                   help="rolling-median window (samples) for despiking")
    p.add_argument("--spike-tol", type=float, default=30.0,
                   help="drop a sample if |x - rolling_median| exceeds this (ug/L)")
    p.add_argument("--max-chl", type=float, default=500.0,
                   help="hard cap; values above are sensor errors")
    p.add_argument("--out", default="data/buoy_chl_daily.csv")
    return p.parse_args()


def _get(url, expect_csv=True):
    if requests is None:
        sys.exit("requests not installed. pip install requests --break-system-packages")
    r = requests.get(url, timeout=120, headers={"User-Agent": "hab-bloom-predictor"})
    r.raise_for_status()
    txt = r.text
    if expect_csv:
        head = txt.lstrip()[:200].lower()
        if head.startswith("<!doctype") or head.startswith("<html") or "<table" in head:
            raise ValueError(f"server returned HTML, not CSV, for {url}")
    return txt


KNOWN_FALLBACK = [
    "UCONN_EXRX_WQ_SFC", "UCONN_EXRX_WQ_MID", "UCONN_EXRX_WQ_BTM",
    "UCONN_WLIS_WQ_SFC", "UCONN_WLIS_WQ_MID", "UCONN_WLIS_WQ_BTM",
    "UCONN_CLIS_WQ_SFC", "UCONN_CLIS_WQ_MID", "UCONN_CLIS_WQ_BTM",
]


def _ids_from_csv(text):
    df = pd.read_csv(io.StringIO(text))
    col = next((c for c in df.columns if "dataset id" in c.lower()), None)
    if col is None:
        col = next((c for c in df.columns if "dataset" in c.lower()), df.columns[-1])
    return df[col].astype(str)


def _filter_lis(ids):
    ids = pd.Series(pd.unique(ids))
    keep = ids[ids.str.contains("UCONN", case=False) &
               ids.str.contains("WQ", case=False) &
               ids.str.contains("|".join(SITE_TOKENS), case=False)]
    return sorted(keep)


def discover_datasets(base):
    """Find UConn LIS water-quality buoy dataset IDs. Tries the search endpoint
    (clean CSV), then the institution-categorized listing, then known IDs."""
    # 1) search endpoint - returns a small, clean CSV
    try:
        url = (f"{base}/search/index.csv?"
               f"searchFor=UCONN%20WQ&itemsPerPage=1000&page=1")
        got = _filter_lis(_ids_from_csv(_get(url, expect_csv=False)))
        if got:
            return got
    except Exception as e:
        print(f"  search endpoint failed ({e}); trying category listing...")
    # 2) categorize by institution = UCONN
    try:
        url = f"{base}/categorize/institution/index.csv"
        # this just confirms reachability; fall through to known IDs either way
        _get(url)
    except Exception:
        pass
    # 3) known IDs, probed individually in main() via metadata
    print("  using known fallback IDs (will probe each for existence)")
    return KNOWN_FALLBACK


def _parse_das(text):
    """Parse an OPeNDAP .das into {var: {attr: value}}. Tolerant, regex-light."""
    out, cur = {}, None
    for line in text.splitlines():
        t = line.strip()
        if t.endswith("{"):
            cur = t[:-1].strip(); out.setdefault(cur, {})
        elif t == "}":
            cur = None
        elif cur and ";" in t:
            parts = t.rstrip(";").split(None, 2)  # type, name, value
            if len(parts) == 3:
                name, val = parts[1], parts[2].strip().strip('"')
                out[cur][name] = val
    return out


def discover_chl_var(base, dsid):
    """Return (chl_variable_name, units) by reading the dataset .das."""
    das = _parse_das(_get(f"{base}/tabledap/{dsid}.das", expect_csv=False))
    hits = []
    for var, attrs in das.items():
        if var in ("NC_GLOBAL", "s", ""):
            continue
        blob = " ".join(str(v).lower() for v in attrs.values())
        nm = var.lower()
        if "chlorophyll" in blob or nm.startswith("chl") or "chlor" in nm:
            hits.append((var, attrs.get("units", "?")))
    if not hits:
        return None, None
    # prefer concentration units (ug/L, mg m-3) over RFU / percent
    hits.sort(key=lambda vu: ("ug/l" in vu[1].lower() or "mg m" in vu[1].lower()),
              reverse=True)
    return hits[0]


def pull_series(base, dsid, var, start, end):
    # .csv0 = no header, no units row; we name the columns ourselves
    q = (f"{base}/tabledap/{dsid}.csv0?time,{var}"
         f"&time>={start}T00:00:00Z&time<={end}T23:59:59Z")
    txt = _get(q, expect_csv=False)
    if "<html" in txt[:200].lower() or "<!doctype" in txt[:200].lower():
        raise ValueError("data endpoint returned HTML")
    df = pd.read_csv(io.StringIO(txt), header=None, names=["time", "chl"])
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce").dt.tz_localize(None)
    df["chl"] = pd.to_numeric(df["chl"], errors="coerce")
    return df.dropna(subset=["time", "chl"])


def qc_and_daily(df, spike_window, spike_tol, max_chl):
    df = df.sort_values("time").copy()
    n0 = len(df)
    df = df[(df["chl"] > 0) & (df["chl"] < max_chl)]
    med = df["chl"].rolling(spike_window, center=True, min_periods=1).median()
    df = df[(df["chl"] - med).abs() <= spike_tol]
    n1 = len(df)
    df["date"] = df["time"].dt.normalize()
    daily = (df.groupby("date")["chl"]
               .agg(chl_daily_mean="mean", chl_daily_max="max", n_obs="count")
               .reset_index())
    return daily, n0, n1


def main():
    a = parse_args()
    if a.datasets:
        datasets = a.datasets
        print(f"using supplied datasets: {datasets}")
    else:
        print("discovering UConn LIS WQ buoy datasets...")
        datasets = discover_datasets(a.base)
        if not datasets:
            sys.exit("no matching datasets found; pass --datasets explicitly "
                     "(e.g. UCONN_EXRX_WQ_SUR UCONN_WLIS_WQ_SUR)")
        print(f"found {len(datasets)}: {datasets}")

    frames = []
    print(f"\n{'dataset':<22} {'chl var':<12} {'raw':>8} {'kept':>8} "
          f"{'days':>6} {'date range':<25}")
    for dsid in datasets:
        try:
            try:
                var, units = discover_chl_var(a.base, dsid)
            except Exception as e:
                print(f"{dsid:<22} (not available: {str(e)[:40]})")
                continue
            if var is None:
                print(f"{dsid:<22} {'(no chl var)':<12}")
                continue
            raw = pull_series(a.base, dsid, var, a.start, a.end)
            daily, n0, n1 = qc_and_daily(raw, a.spike_window, a.spike_tol, a.max_chl)
            if daily.empty:
                print(f"{dsid:<22} {var:<12} {n0:>8} {n1:>8} {'0':>6}  (empty after QC)")
                continue
            daily.insert(0, "dataset", dsid)
            daily.insert(1, "site", dsid.split("_")[1])
            daily.insert(2, "chl_units", units)
            frames.append(daily)
            rng = f"{daily['date'].min().date()} .. {daily['date'].max().date()}"
            print(f"{dsid:<22} {var:<12} {n0:>8} {n1:>8} {len(daily):>6}  {rng:<25}")
        except Exception as e:
            print(f"{dsid:<22} ERROR: {e}")

    if not frames:
        sys.exit("\nno usable buoy data pulled.")
    out = pd.concat(frames, ignore_index=True)
    import os
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    out.to_csv(a.out, index=False)

    print("\nCOVERAGE SUMMARY")
    for site, g in out.groupby("site"):
        months = pd.to_datetime(g["date"]).dt.month
        summer = months.isin([6, 7, 8, 9]).mean()
        print(f"  {site:<6} {len(g):>5} days  "
              f"{g['date'].min().date()}..{g['date'].max().date()}  "
              f"summer(JJAS)={summer:.0%}  median chl={g['chl_daily_mean'].median():.1f}")
    print(f"\nSaved {a.out}")
    print("\nNext: map western ship stations (A4, B3) to the nearest buoy by lat/lon")
    print("and re-check the single-reading FP windows against this daily series.")


if __name__ == "__main__":
    main()