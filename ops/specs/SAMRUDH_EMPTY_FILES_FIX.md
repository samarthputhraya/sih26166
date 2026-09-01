# Samrudh — your six commits are real, your six files are empty. Here is the fix.

**You did commit. You did push. Both worked.** `git log` shows your messages, `git status` says
"working tree clean". Nothing you did with git was wrong.

What went wrong is that the *files* you committed have **0 bytes in them**. Git faithfully stored
six empty files and six good commit messages. Git has no opinion about whether a file has content —
it will commit an empty file all day without warning you.

So this is not "start over". Your work is probably still sitting on your machine. **Do step 0
first and do not close any editor windows until you have.**

---

## 🔴 STEP 0 — BEFORE YOU CLOSE ANYTHING

**If VS Code (or whatever editor you used) is still open from last night, do not close it.**

Look at your editor tabs. A tab with a **white dot ●** instead of an **✕** means that file has
**unsaved content sitting in memory**. That is almost certainly where your code is.

If you see a dot on `metrics.py` or any of the others:

1. Click that tab.
2. **Ctrl+S**.
3. Repeat for every tab with a dot.
4. Jump to **Step 3**.

That is the whole fix, and it takes ten seconds. Closing the editor first is the only way to
actually lose the work — so do this before anything else.

---

## STEP 1 — See it for yourself (60 seconds)

Believe it from your own terminal before you rewrite anything. In the repo folder:

```bash
git log --stat -1
```

Look at the last line. It says:

```
 1 file changed, 0 insertions(+), 0 deletions(-)
```

**`0 insertions`** is the tell. A real `metrics.py` would say `0 files changed, 210 insertions(+)`
or similar. Zero insertions means the file you committed was empty.

Now check the files on disk:

**PowerShell:**
```powershell
Get-ChildItem evaluation\ | Select-Object Name, Length
```

**Git Bash:**
```bash
wc -c evaluation/*
```

Every one of the six will show **0**. That is the same thing GitHub is showing everyone else.

---

## STEP 2 — Find where your actual code went

Pick the branch that matches what happened.

### 2A · The editor is closed, but VS Code kept a local history

VS Code silently keeps timestamped copies of files you edited. Try this first:

1. Open the repo in VS Code.
2. Open `evaluation/metrics.py` (it will be blank).
3. **Ctrl+Shift+P** → type **`Local History: Find Entry to Restore`** → Enter.
4. If entries appear, pick last night's and restore it.

You can also look directly:

```powershell
explorer "$env:APPDATA\Code\User\History"
```

Sort by date modified, look for last night around 21:00–22:00.

### 2B · You wrote the file somewhere else

Very common — the editor saved to a different folder than the repo. Search your whole user folder
for the code by a string that would only be in *your* file:

**PowerShell:**
```powershell
Get-ChildItem -Path $env:USERPROFILE -Recurse -Include *.py -ErrorAction SilentlyContinue |
  Select-String -Pattern "def evaluate" |
  Select-Object -First 20 Path, LineNumber
```

**Git Bash:**
```bash
grep -rl "def evaluate" ~ --include=*.py 2>/dev/null | head -20
```

If it finds a hit outside the repo, that is your work. Copy it into
`<repo>\evaluation\metrics.py` and go to Step 3.

Also worth checking: your Downloads folder, your Desktop, and any second copy of the repo
(`git rev-parse --show-toplevel` tells you which repo folder you are actually standing in — make
sure it is the one you think).

### 2C · It genuinely is not anywhere — rewrite it

Not a disaster. Your commit messages prove you understood the design: the held-out residual split,
GT accuracy only on synthetic, a mandatory tier column. **That thinking is the hard part and you
already did it.**

The full spec, with the exact expected test values measured on this venv, is in
**`ops/specs/day_3.md`** under *"[Day 3] Samrudh — evaluation/metrics.py"*. Do `metrics.py` first
and only `metrics.py` — it is the one thing blocking Gate 1 on Day 5.

> ⚠️ One trap from that spec worth repeating, because it costs an hour: your guide says
> `test_known_offset` gives `residual ≈ 3.606`. **It does not.** `residual_px` is measured *after*
> fitting, so the fit absorbs the shift and it comes out ≈ 0. The 3.606 (= √13) belongs to
> `rmse_gt_px`.

---

## STEP 3 — Save, then VERIFY, then commit

This is the loop that stops it happening again. The verify step is the whole point.

```bash
# 1. SAVE IN YOUR EDITOR FIRST. Ctrl+S. No dot on the tab.

# 2. Prove the file has content BEFORE git touches it
wc -c evaluation/metrics.py          # Git Bash
#   or PowerShell:
#   (Get-Item evaluation\metrics.py).Length
```

**If that number is 0, stop. Do not commit.** Go back to your editor.

```bash
# 3. Stage it
git add evaluation/metrics.py

# 4. Prove git has the CONTENT, not just the name.
#    This prints what git will actually store:
git diff --cached --stat
```

You must see something like `evaluation/metrics.py | 210 ++++++++++`. **If it says
`0 insertions`, the file is still empty** — stop and fix it.

```bash
# 5. Now commit
git commit -m "metrics: evaluate() with held-out residual split"

# 6. Push
git push
```

---

## STEP 4 — Confirm it actually landed

```bash
git log --stat -1
```

Look for a real insertion count, **not** `0 insertions(+)`.

Then run the test that matters — this is the exact command that decides Gate 1:

```bash
python -m pytest evaluation/ -q
```

Right now that exits **5** ("no tests collected"). When your file has content it should exit **0**
with 5 tests passing.

And the end-to-end check:

```bash
python -m core.pipeline data/pairs/pair_01
```

Today it prints *"UNAVAILABLE — evaluation/metrics.py does not exist yet"*. When yours lands, it
prints the five metrics instead. **That single line changing is Gate 1.**

---

## Why this happened, so it does not happen twice

Empty files are invisible to every signal you were watching:

| what you checked | what it said | why it fooled you |
|---|---|---|
| `git status` | "working tree clean" | true — an empty file is committed just fine |
| `git log` | your six messages | true — messages are stored separately from content |
| GitHub file list | all six files present | true — they exist, they are just 0 bytes |

The only signal that shows it is **content size**: `0 insertions(+)` in `git log --stat`, or a
length of `0`.

**The one habit that prevents it:** run `git diff --cached --stat` after `git add` and before
`git commit`, every time. It takes two seconds and shows you exactly what git is about to store.

---

## What to send back

Once it is pushed, one message:

> `metrics.py` is in, `pytest evaluation/` exits 0 with 5 tests.

That unblocks Samartha's `evaluate()` integration and clears the last Gate-1 criterion.

**You are not behind on understanding — you are one Ctrl+S behind on delivery.**
