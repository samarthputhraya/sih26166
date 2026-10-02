"""Export the deck to the PDF the portal takes, on this laptop, without a licensed PowerPoint.

    python -m presentation.export_pdf            # SIH26166_LunaXX_deck.pptx -> .pdf beside it

PowerPoint here is unlicensed: COM automation fails (0x80048240), but PRINTING still works.
So the deck is printed with PowerPoint's own `/pt` switch to "Microsoft Print to PDF" - the
render is PowerPoint's, not an approximation - and the "Save Print Output As" dialog that
printer always opens is answered by window messages, not keystrokes (see PS). A "Sign in to
get started with PowerPoint" window also appears; it is left alone and PowerPoint is closed
at the end.

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

import os
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
# Addresses printed on the slides, made clickable again after printing (search text -> link).
# The console's address is searched first; "github.com/samarthputhraya/sih26166" does not match
# inside "samarthputhraya.github.io/sih26166", so the two never overlap.
LINKS = (("samarthputhraya.github.io/sih26166", "https://samarthputhraya.github.io/sih26166/"),
         ("github.com/samarthputhraya/sih26166", "https://github.com/samarthputhraya/sih26166"),
         *((f"arxiv.org/abs/{a}", f"https://arxiv.org/abs/{a}")       # every arXiv reference on slide 6
           for a in ("2509.04775", "2604.25208", "2104.00680", "1912.05909", "1602.02720",
                     "2106.12738", "2101.01710")))
# Page 1 and 2 carry the idea title since v9 (23 Sep): "TITLE PAGE" and "IDEA TITLE" were the
# template's placeholders for it, and build_deck's audit now bans both strings.
TITLES = ("Knows When It Is Wrong", "Knows When It Is Wrong", "TECHNICAL APPROACH",
          "FEASIBILITY AND VIABILITY", "IMPACT AND BENEFITS", "RESEARCH")

# Run as a .ps1 with the paths in LX_PPT, LX_SRC and LX_OUT. The printer's "Save Print Output As"
# dialog is found by its title AND PowerPoint's process id, and answered with window messages:
# WM_SETTEXT into its file-name box (Edit, id 1001), then WM_COMMAND IDOK. Nothing depends on the
# focus. Until 2 Oct it was answered by SendKeys after AppActivate - and PowerPoint's "Sign in to
# get started" window, which opens on top, took the focus and the keystrokes: no PDF was written.
PS = r"""
$ErrorActionPreference = 'Stop'
Add-Type @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class Dlg {
  delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc f, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr parent, EnumProc f, IntPtr l);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] static extern int GetDlgCtrlID(IntPtr h);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, string l);
  [DllImport("user32.dll")] static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  // The visible top-level window of process `pid` with this title, or zero.
  public static IntPtr Find(string title, int pid) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
      var sb = new StringBuilder(256); GetWindowText(h, sb, 256); uint p;
      GetWindowThreadProcessId(h, out p);
      if (p == (uint)pid && IsWindowVisible(h) && sb.ToString() == title) { found = h; return false; }
      return true; }, IntPtr.Zero);
    return found;
  }
  // The descendant of `dlg` with this window class and control id, or zero.
  public static IntPtr Child(IntPtr dlg, string cls, int id) {
    IntPtr found = IntPtr.Zero;
    EnumChildWindows(dlg, (h, l) => {
      var sb = new StringBuilder(64); GetClassName(h, sb, 64);
      if (sb.ToString() == cls && GetDlgCtrlID(h) == id) { found = h; return false; }
      return true; }, IntPtr.Zero);
    return found;
  }
  public static void SetText(IntPtr h, string s) { SendMessage(h, 0x000C, IntPtr.Zero, s); }   // WM_SETTEXT
  public static void Ok(IntPtr dlg, IntPtr btn) { SendMessage(dlg, 0x0111, (IntPtr)1, btn); }   // WM_COMMAND, IDOK
}
'@
$out = $env:LX_OUT
$p = Start-Process -FilePath $env:LX_PPT -ArgumentList @('/pt', '"Microsoft Print to PDF"', '""', '""', ('"' + $env:LX_SRC + '"')) -PassThru
$dlg = [IntPtr]::Zero
for ($i = 0; $i -lt 120 -and $dlg -eq [IntPtr]::Zero; $i++) {
  Start-Sleep -Milliseconds 500
  $dlg = [Dlg]::Find('Save Print Output As', $p.Id)
}
if ($dlg -eq [IntPtr]::Zero) { Stop-Process -Id $p.Id -Force; Write-Output 'NO DIALOG'; exit 3 }
$edit = [IntPtr]::Zero
for ($i = 0; $i -lt 40 -and $edit -eq [IntPtr]::Zero; $i++) {
  Start-Sleep -Milliseconds 250
  $edit = [Dlg]::Child($dlg, 'Edit', 1001)
}
$save = [Dlg]::Child($dlg, 'Button', 1)
if ($edit -eq [IntPtr]::Zero -or $save -eq [IntPtr]::Zero) {
  Stop-Process -Id $p.Id -Force; Write-Output 'NO FILE NAME BOX OR SAVE BUTTON'; exit 5 }
Start-Sleep -Milliseconds 500
[Dlg]::SetText($edit, $out)
Start-Sleep -Milliseconds 300
[Dlg]::Ok($dlg, $save)
for ($i = 0; $i -lt 90; $i++) {
  Start-Sleep -Seconds 1
  if (Test-Path $out) { $a = (Get-Item $out).Length; Start-Sleep 2
    if ($a -gt 0 -and $a -eq (Get-Item $out).Length) { break } }
}
Start-Sleep -Seconds 2
Get-Process POWERPNT -ErrorAction SilentlyContinue | Stop-Process -Force
if (Test-Path $out) { Write-Output 'PRINTED' } else { Write-Output 'NO PDF'; exit 4 }
"""


def print_to_pdf(src: pathlib.Path, out: pathlib.Path) -> None:
    if not pathlib.Path(POWERPNT).exists():
        raise SystemExit(f"PowerPoint not found at {POWERPNT}")
    running = subprocess.run(["tasklist", "/FI", "IMAGENAME eq POWERPNT.EXE"], capture_output=True,
                             text=True).stdout
    if "POWERPNT" in running:
        raise SystemExit("PowerPoint is already running - close it first")
    if out.exists():
        out.unlink()
    script = src.with_name("print.ps1")
    script.write_text(PS, encoding="utf-8-sig")         # with a BOM: PowerShell 5.1 reads it as UTF-8
    env = {**os.environ, "LX_PPT": POWERPNT, "LX_SRC": str(src), "LX_OUT": str(out)}
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
                       capture_output=True, text=True, timeout=300, env=env)
    if "PRINTED" not in r.stdout:
        raise SystemExit(f"printing failed: {r.stdout.strip()} {r.stderr.strip()[:400]}")


def _family(font_program: bytes | None) -> str | None:
    """The family name inside an embedded TrueType program, or None if it cannot be read."""
    if not font_program:
        return None
    try:
        import io
        from PIL import ImageFont
        return ImageFont.truetype(io.BytesIO(font_program), 12).getname()[0]
    except (OSError, ValueError):
        return None


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
        # ONE face, as printed (SPOC review, 27 Sep). The .pptx names Calibri on every run, but
        # PowerPoint's print path once set slide 1's second title line in Arial - the embedded
        # subset names are anonymous (CIDFont+F2), so read each font program's own family name.
        for f in page.get_fonts(full=True):
            buf = doc.extract_font(f[0])[3]
            fam = _family(buf)
            if fam and fam != "Calibri":
                problems.append(f"page {i + 1}: printed in {fam}, not Calibri - export again")
    # Printing to PDF drops PowerPoint's hyperlinks, so a judge reading the PDF could not click the
    # addresses on slides 3 and 6. Put the links back over the printed text (v11, 2 Oct).
    n_links = 0
    for page in doc:
        for text, uri in LINKS:
            for rect in page.search_for(text):
                page.insert_link({"kind": pymupdf.LINK_URI, "from": rect, "uri": uri})
                n_links += 1
    print(f"  {n_links} link(s) restored over the printed addresses")
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
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
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
