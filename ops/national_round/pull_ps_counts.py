"""Snapshot the public SIH 2026 problem-statement table: ideas submitted per PS, out of 500.

The link the portal hands a team leader (sih.gov.in/allProblemStatements/...) redirects to the
sign-in page; the same table, with the same "Submitted Idea(s) Count" column, is public at
sih.gov.in/sih2026PS. One run writes one dated CSV next to this file, so two runs a few days apart
give the growth rate that the research prompt's 25 Sep re-check needs.

    python ops/national_round/pull_ps_counts.py                 # fetch live, write today's CSV
    python ops/national_round/pull_ps_counts.py --html page.html # parse a saved copy instead

Standard library only, so any Python runs it.
"""
import argparse
import csv
import datetime
import glob
import html
import os
import re
import sys
import urllib.request

URL = "https://sih.gov.in/sih2026PS"
HERE = os.path.dirname(os.path.abspath(__file__))
OURS = "SIH26166"
FIELDS = ["ps", "category", "ideas", "cap", "org", "theme", "deadline", "title"]


def _text(fragment):
    fragment = re.sub(r"<!--.*?-->", " ", fragment, flags=re.S)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def parse(page):
    # Each row opens with its S.No. cell. The title cell embeds a whole modal (with nested
    # tables), so rows are split on that opening cell rather than on <tr>.
    body = page[page.find("<tbody>"):]
    parts = re.split(r'<tr>\s*<td class="colomn_border">\d+</td>', body)
    rows = []
    for chunk in parts[1:]:
        org = re.search(r'<td class="colomn_border">(.*?)</td>', chunk, re.S)
        title = re.search(r'data-target="#ViewProblemStatement\d+"\s*>(.*?)</a>', chunk, re.S)
        tail = re.search(r"<td>\s*(Software|Hardware)\s*</td>\s*<td>\s*(SIH\d+)\s*</td>\s*"
                         r"<td>\s*(\d+)\s*/\s*(\d+)\s*</td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>",
                         chunk, re.S)
        if not tail:
            raise ValueError("row layout changed: " + _text(chunk)[:120])
        rows.append({"ps": tail.group(2), "category": tail.group(1),
                     "ideas": int(tail.group(3)), "cap": int(tail.group(4)),
                     "org": _text(org.group(1)) if org else "",
                     "theme": _text(tail.group(5)), "deadline": _text(tail.group(6)),
                     "title": _text(title.group(1)) if title else ""})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--html", help="parse this saved page instead of fetching")
    args = ap.parse_args()

    if args.html:
        page = open(args.html, encoding="utf-8", errors="replace").read()
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        page = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
    rows = parse(page)

    now = datetime.datetime.now()
    out = os.path.join(HERE, f"ps_counts_{now:%Y-%m-%d}.csv")
    if os.path.exists(out):  # a second run the same day must not overwrite the first
        out = os.path.join(HERE, f"ps_counts_{now:%Y-%m-%d_%H%M}.csv")
    earlier = sorted(p for p in glob.glob(os.path.join(HERE, "ps_counts_*.csv")) if p != out)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    software = sorted(r["ideas"] for r in rows if r["category"] == "Software")
    ours = next(r for r in rows if r["ps"] == OURS)
    fewer = sum(1 for n in software if n < ours["ideas"])
    print(f"{len(rows)} PSs, {sum(r['ideas'] for r in rows)} ideas in total -> {out}")
    print(f"software median {software[len(software) // 2]} | at the {rows[0]['cap']} cap: "
          f"{sum(1 for r in rows if r['ideas'] >= r['cap'])} PSs")
    print(f"{OURS}: {ours['ideas']}/{ours['cap']}, more than {fewer} of {len(software)} software PSs")

    if earlier:  # growth since the oldest snapshot, for our PS and the fastest movers
        with open(earlier[0], encoding="utf-8") as f:
            then = {r["ps"]: int(r["ideas"]) for r in csv.DictReader(f)}
        print(f"\nsince {os.path.basename(earlier[0])}:")
        grown = sorted(rows, key=lambda r: r["ideas"] - then.get(r["ps"], 0), reverse=True)
        for r in [ours] + [r for r in grown[:10] if r["ps"] != OURS]:
            print(f"  {r['ps']} {then.get(r['ps'], 0):>4} -> {r['ideas']:>4}  {r['title'][:70]}")


if __name__ == "__main__":
    sys.exit(main())
