"""Export the deck to the PDF the portal takes, on this laptop, without a licensed PowerPoint.

    python -m presentation.export_pdf            # SIH26166_LunaXX_deck.pptx -> .pdf beside it

PowerPoint here is unlicensed: COM automation fails (0x80048240), but PRINTING still works.
So the deck is printed with PowerPoint's own `/pt` switch to "Microsoft Print to PDF" - the
render is PowerPoint's, not an approximation - and the "Save Print Output As" dialog that
printer always opens is answered by keystroke. A "Sign in to set up Office" window also
appears; it is left alone and PowerPoint is closed at the end.

The printer lays each 13.33 x 7.5 in slide on a Letter-landscape page (792 x 612 pt) with
white bands above and below; every page is then cropped to the slide band (792 x 446 pt)
with PyMuPDF, which is how the 10 Sep college-round PDF was made. PyMuPDF is not in the
demo venv on purpose (it is not on the demo path):
    pip install --target <some dir> pymupdf ; set PYTHONPATH=<some dir>

Checks on the result, all printed: 6 pages, the slide aspect ratio, each page's title text,
no text running into the footer bar (the one overflow the build audit cannot see),
no "[TBD]" left, the file size. Do not upload a PDF this script did not pass.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
DECK = HERE / "SIH26166_LunaXX_deck.pptx"
PDF = DECK.with_suffix(".pdf")
POWERPNT = r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE"
FOOTER_TOP_IN = 6.95                      # the template's footer bar starts here (build_deck)
# Page 1 and 2 carry the idea title since v9 (23 Sep): "TITLE PAGE" and "IDEA TITLE" were the
# template's placeholders for it, and build_deck's audit now bans both strings.
TITLES = ("Knows When It Is Wrong", "Knows When It Is Wrong", "TECHNICAL APPROACH",
          "FEASIBILITY AND VIABILITY", "IMPACT AND BENEFITS", "RESEARCH")

PS = r"""
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
$sh = New-Object -ComObject WScript.Shell
$p = Start-Process -FilePath '{ppt}' -ArgumentList @('/pt', '"Microsoft Print to PDF"', '""', '""', '"{src}"') -PassThru
$done = $false
for ($i = 0; $i -lt 120 -and -not $done; $i++) {{
  Start-Sleep -Milliseconds 500
  if ($sh.AppActivate('Save Print Output As')) {{
    Start-Sleep -Milliseconds 600
    [System.Windows.Forms.SendKeys]::SendWait('%n')
    Start-Sleep -Milliseconds 300
    [System.Windows.Forms.SendKeys]::SendWait('{keys}')
    Start-Sleep -Milliseconds 400
    [System.Windows.Forms.SendKeys]::SendWait('{{ENTER}}')
    $done = $true
  }}
}}
if (-not $done) {{ Stop-Process -Id $p.Id -Force; Write-Output 'NO DIALOG'; exit 3 }}
for ($i = 0; $i -lt 90; $i++) {{
  Start-Sleep -Seconds 1
  if (Test-Path '{out}') {{ $a = (Get-Item '{out}').Length; Start-Sleep 2
    if ($a -gt 0 -and $a -eq (Get-Item '{out}').Length) {{ break }} }}
}}
Start-Sleep -Seconds 2
Get-Process POWERPNT -ErrorAction SilentlyContinue | Stop-Process -Force
if (Test-Path '{out}') {{ Write-Output 'PRINTED' }} else {{ Write-Output 'NO PDF'; exit 4 }}
"""


def _sendkeys_escape(s: str) -> str:
    return "".join("{" + c + "}" if c in "+^%~(){}[]" else c for c in s)


def print_to_pdf(src: pathlib.Path, out: pathlib.Path) -> None:
    if not pathlib.Path(POWERPNT).exists():
        raise SystemExit(f"PowerPoint not found at {POWERPNT}")
    running = subprocess.run(["tasklist", "/FI", "IMAGENAME eq POWERPNT.EXE"], capture_output=True,
                             text=True).stdout
    if "POWERPNT" in running:
        raise SystemExit("PowerPoint is already running - close it first (the dialog would be ambiguous)")
    if out.exists():
        out.unlink()
    script = PS.format(ppt=POWERPNT, src=str(src), out=str(out).replace("'", "''"),
                       keys=_sendkeys_escape(str(out)).replace("'", "''"))
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                       capture_output=True, text=True, timeout=300)
    if "PRINTED" not in r.stdout:
        raise SystemExit(f"printing failed: {r.stdout.strip()} {r.stderr.strip()[:400]}")


def crop_and_check(printed: pathlib.Path, final: pathlib.Path) -> int:
    try:
        import pymupdf
    except ImportError:
        print("PyMuPDF is not importable - see the module docstring; the uncropped print is at "
              f"{printed}")
        return 2
    doc = pymupdf.open(str(printed))
    problems = []
    if doc.page_count != 6:
        problems.append(f"{doc.page_count} pages, not 6")
    for i, page in enumerate(doc):
        w, h = page.rect.width, page.rect.height
        band = w * 7.5 / 13.333                      # the slide's own aspect ratio
        top = (h - band) / 2
        page.set_cropbox(pymupdf.Rect(0, top, w, top + band))
        text = page.get_text()
        if i < len(TITLES) and TITLES[i] not in text:
            problems.append(f"page {i + 1}: title {TITLES[i]!r} not found")
        if "TBD" in text:
            problems.append(f"page {i + 1}: a [TBD] placeholder is still on the page")
        # Text that runs into the footer bar (from 6.95 in of 7.5). build_deck's audit checks
        # the text BOXES; only the rendered page shows text overflowing its box, and on 20 Sep
        # slides 2 and 4 did exactly that. The page number is the one thing allowed there.
        if i:
            r = page.rect
            foot = r.y0 + r.height * FOOTER_TOP_IN / 7.5
            for b in page.get_text("blocks"):
                if b[3] > foot + 1 and not b[4].strip().isdigit():
                    problems.append(f"page {i + 1}: text runs into the footer: {b[4].strip()[:50]!r}")
    doc.set_metadata({"title": "SIH26166 - LunaXX", "author": "Team LunaXX",
                      "subject": "Smart India Hackathon 2026, problem statement SIH26166"})
    doc.save(str(final), garbage=3, deflate=True)
    doc.close()
    chk = pymupdf.open(str(final))
    sizes = {(round(p.cropbox.width), round(p.cropbox.height)) for p in chk}
    print(f"wrote {final.name}: {chk.page_count} pages, page size {sizes} pt, "
          f"{final.stat().st_size:,} bytes")
    chk.close()
    for p in problems:
        print(f"  !! {p}")
    print("  PDF CHECK: " + ("clean" if not problems else f"{len(problems)} problem(s)"))
    return 0 if not problems else 1


def main() -> int:
    if not DECK.exists():
        print(f"missing {DECK} - run `python -m presentation.build_deck` first")
        return 2
    with tempfile.TemporaryDirectory() as td:
        # A copy with a plain name: the dialog is typed into, so the path stays simple.
        src = pathlib.Path(td) / "deck.pptx"
        src.write_bytes(DECK.read_bytes())
        printed = pathlib.Path(td) / "printed.pdf"
        t0 = time.time()
        print_to_pdf(src, printed)
        print(f"printed by PowerPoint in {time.time() - t0:.0f} s")
        return crop_and_check(printed, PDF)


if __name__ == "__main__":
    sys.exit(main())
