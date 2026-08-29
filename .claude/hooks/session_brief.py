#!/usr/bin/env python
"""SessionStart hook — prints a short position brief for SIH26166.

Defensive by design: this hook must NEVER block a session. Every failure path
exits 0 silently. A broken hook costs more time than the brief saves.

Windows note: the console defaults to cp1252, and STATUS.md contains em-dashes
and emoji. Printing those raw raises UnicodeEncodeError, which the outer
try/except would swallow -- leaving a hook that appears to run and prints
nothing. So: reconfigure stdout to UTF-8, and emit ASCII-only decoration.
"""
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def sh(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout, errors="replace")
        return (r.stdout or "").strip()
    except Exception:
        return ""


# Common characters STATUS.md uses that cp1252 consoles choke on.
_TRANSLIT = {
    "—": "-", "–": "-", "→": "->", "≥": ">=", "≤": "<=",
    "×": "x", "•": "*", "‘": "'", "’": "'",
    "“": '"', "”": '"', "⚠": "", "️": "", "✅": "",
}


def safe(text):
    """Transliterate what we can, drop what we cannot. Belt and braces."""
    for k, v in _TRANSLIT.items():
        text = text.replace(k, v)
    return text.encode("ascii", "ignore").decode("ascii")


def main():
    root = Path(__file__).resolve().parents[2]
    status = root / "ops" / "STATUS.md"
    lines = []

    # Day / gate position -- STATUS.md is the single source of truth.
    if status.exists():
        try:
            wanted = ("| **Day**", "| **Next gate**", "| **Internal hackathon**")
            for ln in status.read_text(encoding="utf-8", errors="replace").splitlines():
                s = ln.strip()
                if s.startswith(wanted):
                    lines.append("  " + s.strip("|").replace("**", "").replace("|", " -").strip())
        except Exception:
            pass
    else:
        lines.append("  ops/STATUS.md missing - previous session did not run /wrap")

    # Uncommitted work left behind?
    dirty = sh("git status --porcelain")
    if dirty:
        lines.append(f"  [!] {len(dirty.splitlines())} uncommitted file(s) - last session may not have wrapped")

    # Did teammates push while we were away?
    recent = sh('git log --oneline --since="18 hours ago"')
    if recent:
        authors = sh('git log --since="18 hours ago" --format=%an')
        who = ", ".join(sorted({a for a in authors.splitlines() if a}))
        lines.append(f"  [<] {len(recent.splitlines())} new commit(s) since yesterday: {who or 'unknown'}")

    if not lines:
        return

    print(safe("-- SIH26166 " + "-" * 46))
    for ln in lines:
        print(safe(ln))
    print(safe("  Run /next to rebuild context and get a plan."))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
