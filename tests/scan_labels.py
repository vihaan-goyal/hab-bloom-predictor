"""Helper: print every file that builds a bloom label inline.

Used to refresh the frozen allowlist in tests/test_no_inline_labels.py.
Run:  python tests/scan_labels.py
"""
import io
import os
import re
import tokenize

SKIP = (".git", "__pycache__", ".claude", ".ipynb_checkpoints")

PATTERNS = {
    # df['bloom_28d'] = 0  -- initialize-to-zero, the uncensored Family B label
    "inline_zero_init": re.compile(r"bloom_\w*'?\]?\s*=\s*0\b"),
    # groupby(...).shift(-7) / .shift(-HORIZON) -- positional row shift, Family C
    "positional_shift": re.compile(r"\.shift\(\s*-\s*\w+\s*\)"),
    # iloc[idx + FORECAST_HORIZON] -- positional row offset, Family C
    "positional_iloc": re.compile(r"iloc\[\s*\w+\s*\+\s*\w*HORIZON"),
}


def strip_comments_and_docstrings(src):
    """Blank out comments and triple-quoted blocks.

    Ordinary string literals are KEPT, because the pattern we search for
    contains one (`df['bloom_28d'] = 0`). Only comments and docstrings are
    dropped, so that a comment *describing* a past defect is not itself
    reported as one.

    Blanks the offending character ranges in place rather than rebuilding the
    source from tokens, so line and column layout is preserved and patterns
    that span a line still match.
    """
    lines = [list(ln) for ln in src.splitlines(keepends=True)]
    spans = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                spans.append((tok.start, tok.end))
            elif tok.type == tokenize.STRING:
                body = tok.string.lstrip("rbufRBUF")
                if body[:3] in ('"""', "'''"):
                    spans.append((tok.start, tok.end))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return src      # unparseable: fall back to raw; better to over-report

    for (srow, scol), (erow, ecol) in spans:
        for row in range(srow, erow + 1):
            if row - 1 >= len(lines):
                break
            ln = lines[row - 1]
            lo = scol if row == srow else 0
            hi = ecol if row == erow else len(ln)
            for i in range(lo, min(hi, len(ln))):
                if ln[i] != "\n":
                    ln[i] = " "
    return "".join("".join(ln) for ln in lines)


def scan(root="."):
    """Return {relative_path: [pattern names]} for every offending file."""
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune by directory NAME only. Matching against the full dirpath would
        # skip everything when the checkout itself sits under one of these
        # names -- a git worktree lives under .claude/worktrees/.
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            try:
                src = open(full, encoding="utf-8").read()
            except Exception:
                continue
            code = strip_comments_and_docstrings(src)
            kinds = sorted(k for k, p in PATTERNS.items() if p.search(code))
            if kinds:
                found[rel] = kinds
    return found


if __name__ == "__main__":
    hits = scan(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    print(f"{len(hits)} files")
    for p in sorted(hits):
        print(f'    "{p}",  # {",".join(hits[p])}')
