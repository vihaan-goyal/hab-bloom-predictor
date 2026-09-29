"""
check_dependencies.py
---------------------
Compares every third-party import in the repo against environment.yml.

Exists because `polars` was imported by 9 scripts -- including
audit_flagged_windows.py and check_label_integrity.py -- while being absent
from environment.yml, so a clean checkout following the documented setup could
not run them at all.

Run:  python tests/check_dependencies.py
"""
import ast
import os
import re
import sys

SKIP_DIRS = {".git", "__pycache__", ".claude", ".ipynb_checkpoints", "node_modules"}

# import name -> distribution name, where they differ
ALIASES = {
    "sklearn": "scikit-learn",
    "netCDF4": "netCDF4",
    "cv2": "opencv-python",
    "PIL": "pillow",
    "yaml": "pyyaml",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "imblearn": "imbalanced-learn",
}

# Packages listed only in the channels: block, not dependencies.
CHANNELS = {"defaults", "conda-forge", "pip:"}


def local_modules(root):
    """Every module name that resolves to a .py file inside this repo. Scripts
    here import each other as same-directory modules (rolling_origin_cv,
    horizon_decomp, convlstm_model), which are not packages."""
    names = {"src", "tests"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                names.add(fn[:-3])
    return names


def repo_root():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def declared(env_path):
    """Package names listed in environment.yml, lowercased."""
    names = set()
    for line in open(env_path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("-"):
            continue
        spec = line.lstrip("- ").split("#")[0].strip()   # drop inline comments
        name = re.split(r"[=<>!~\[]", spec)[0].strip().lower()
        if name and name != "pip" and name not in CHANNELS:
            names.add(name)
    return names


def imported(root, LOCAL):
    """{module: {files}} for every non-stdlib, non-local import."""
    std = set(sys.stdlib_module_names)
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            try:
                tree = ast.parse(open(full, encoding="utf-8").read())
            except Exception:
                continue
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    mods = [node.module.split(".")[0]]
                for m in mods:
                    if m in std or m in LOCAL:
                        continue
                    found.setdefault(m, set()).add(rel)
    return found


def main():
    root = repo_root()
    env = os.path.join(root, "environment.yml")
    have = declared(env)
    used = imported(root, local_modules(root))

    missing = {m: f for m, f in used.items()
               if ALIASES.get(m, m).lower() not in have and m.lower() not in have}

    print("Third-party imports NOT declared in environment.yml:")
    if not missing:
        print("  (none)")
    for m in sorted(missing):
        files = sorted(missing[m])
        print(f"  {m:<14} {len(files)} file(s), e.g. {files[0]}")

    used_names = {ALIASES.get(m, m).lower() for m in used} | {m.lower() for m in used}
    unused = sorted(h for h in have if h not in used_names and h != "python")
    print("\nDeclared but never imported (informational):")
    for u in unused:
        print("  ", u)

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
