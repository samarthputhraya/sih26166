# 01 — How We Work Together

**Problem:** six people, six cities' worth of distance, 2 hrs/day each, and everyone's work depends
on someone else's output.

**Rule:** nobody ever sends a project file to another person. Ever. Files live in one place and
everyone reads from that place.

---

## THE SHORT VERSION

| What | Where | Who touches it |
|---|---|---|
| Code, CSVs, docs, small results | **GitHub repo** | everyone, own folder only |
| Big lunar images (`data/`) | **Google Drive, auto-synced** | Rohan writes, everyone reads |
| Raw 750 MB downloads | **Rohan's PC only** | Rohan |
| "I'm done" / "I'm blocked" | **WhatsApp** | everyone |

You were right that "Rohan finishes → says *done* in chat → Samrudh picks up from the files" is the
correct model. This document is just the plumbing that makes it work.

---

## WHY TWO PLACES INSTEAD OF ONE

GitHub **rejects any file over 100 MB** and gets slow and miserable well before a repo hits 1 GB.
One OHRC ZIP is ~750 MB. If Rohan commits raw data, the push fails; if he commits a lot of medium
files, the repo bloats permanently and everyone's `git pull` takes ten minutes.

Google Drive gives 15 GB free and its desktop app syncs a folder automatically — Rohan drops a file
in, it appears on everyone's machine with no action from anyone. That is exactly the behaviour you
described, and it is the right tool for image data.

Git LFS is the "proper" answer but its free tier is 1 GB of storage and 1 GB of bandwidth per
month. We would blow through that in two days. Skip it.

---

## ⚠️ ONEDRIVE — READ BEFORE `git init`

The repo lives at `C:\Users\samar\OneDrive\Documents\SIH26166`, inside a OneDrive-synced folder.
That is workable, but three things will bite if left alone:

**1. Files On-Demand will break Gate 4.** OneDrive can leave files as cloud *placeholders* — they
look present in Explorer but Python cannot open them. Gate 4 runs with wifi off; a placeholder in
`demo_cache/` fails at exactly the worst moment.
> **Do this now:** right-click the `SIH26166` folder → **"Always keep on this device."**
> This is the single most important setting on this list.

**2. OneDrive syncing `.git/` can corrupt the repo.** Git writes many small files quickly; sync
landing mid-write has been known to produce a broken index or lost objects. GitHub is already our
real backup, so OneDrive's copy of `.git/` adds risk with no benefit.
> **Do this:** pause OneDrive during long git operations — the initial push, big merges.
> Tray icon → Pause syncing → 2 hours. If you ever see `error: bad index file` or
> `unable to read tree`, pause sync and re-clone from GitHub.

**3. `venv/` will hammer sync.** Thousands of small files, none worth backing up. It's in
`.gitignore`, but OneDrive doesn't read that.
> **Do this:** OneDrive settings → Account → Choose folders → untick `venv` once it exists.
> Or create the venv outside the synced folder entirely.

**If anything corrupts:** the GitHub copy is authoritative. Delete the local folder, re-clone,
re-create `data_path.txt`. Nothing is lost provided you have been pushing daily — which is exactly
why `/wrap` pushes every session.

---

## SETUP — SAMARTHA, ONCE (30 min, Day 1)

**1. Create the GitHub repo**
- `github.com/new` → name `sih26166` → **Private** → Add README
- Settings → Collaborators → add all 5 by GitHub username
- Free private repos allow unlimited collaborators

**2. Create `.gitignore` before anything else.** This is what stops someone accidentally
committing a 750 MB file and breaking the repo for everyone:

```gitignore
# Big data lives in Google Drive, never in git
data/raw/
data/pairs/
demo_cache/
weights/
*.IMG
*.img
*.tif
*.tiff
*.zip
*.JP2
*.mp4

# Python
venv/
__pycache__/
*.pyc
.ipynb_checkpoints/

# OS
Thumbs.db
desktop.ini
.DS_Store
```

**3. Create the Google Drive folder**
- One Drive account (yours) → new folder `SIH26166_DATA`
- Inside it: `raw_samples/`, `pairs/`, `demo_cache/`, `weights/`
- Share → add all 5 → **Editor**
- Send the link once, in the WhatsApp group, pinned

**4. Push the skeleton** — full folder structure from Canonical Facts §14, with an empty
`.gitkeep` in each directory so the structure exists for everyone on first clone.

---

## SETUP — EVERYONE ELSE, ONCE (10 min, Day 1)

**1. Install Git** — `git-scm.com/download/win`, accept every default.

**2. Install Google Drive for Desktop** — `google.com/drive/download`. Sign in. Find the shared
`SIH26166_DATA` folder and click **"Make available offline"** — otherwise files are links, not
files, and Python cannot open them.

**3. Clone the repo**
```bash
cd C:\Users\<you>
git clone https://github.com/<samartha>/sih26166.git
cd sih26166
```

**4. Point the repo at the Drive data.** Create `data_path.txt` in the repo root containing your
own path to the synced folder, e.g.:
```
G:\My Drive\SIH26166_DATA
```
This file is in `.gitignore`, so everyone's path can differ without conflict. Code reads it:
```python
from pathlib import Path
DATA = Path(Path("data_path.txt").read_text().strip())
img = DATA / "pairs" / "pair_01_source.tif"
```

**5. Set up Python**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**6. Tell Git who you are**
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## THE DAILY RHYTHM — FOUR COMMANDS

Same four every day. You do not need to understand Git beyond this.

**Before you start (30 seconds):**
```bash
cd sih26166
git pull
```
You now have everyone's latest work. Google Drive has already synced the images in the background.

**When you finish (1 minute):**
```bash
git add .
git commit -m "Samrudh: metrics.py grid coverage + tests"
git push
```

**Then post one line in WhatsApp:**
> "Done for today — metrics.py has all 5 metrics + 3 tests passing. Pushed. Risheeth you can use
> `evaluate()` now."

That last sentence is the entire handoff. No files attached, no zip, no "wait let me send it."

---

## WHY YOU WON'T GET MERGE CONFLICTS

Because **each person owns a folder and nobody else writes in it.**

| Folder | Owner | Everyone else |
|---|---|---|
| `core/` | **Samartha** | read only |
| `evaluation/` | **Samrudh** | read only |
| `baselines/` | **Risheeth** | read only |
| `app/change_detection.py` | **Rishabh** | read only |
| `app/streamlit_app.py` | **Samartha** | read only |
| `presentation/` | **Saniya** | read only |
| `data/*.csv`, `data/*.md` | **Rohan** | read only |
| `requirements.txt` | **Samartha only** | ask him to add your package |

Two people editing different files can never conflict. Git handles that automatically. This is why
the folder structure looks the way it does — it isn't tidiness, it's conflict prevention.

**If you need something changed in someone else's folder, ask them.** Do not edit it. That is the
one rule that keeps this frictionless.

> **Note:** we work directly on `main`. No branches, no pull requests. Branch-and-PR is better
> practice for a long-lived project, but here it would make Samartha a bottleneck on five people's
> 2-hour days — and "no teammate ever waits on Samartha" outranks tidy Git history. Samartha reads
> the diffs each morning; if something is wrong, `git revert` is one command.

---

## ⚠️ THE ONE FILE THAT *WILL* CONFLICT — AND THE FIX

`evaluation/results_log.csv` is written by Samrudh, Risheeth **and** Samartha. If three people
append rows to the same CSV and push, Git conflicts every single time, and CSV conflicts are
horrible to resolve by hand.

**Fix: nobody appends to a shared file. Each run writes its own.**

```python
# evaluation/log_run.py
from pathlib import Path
import pandas as pd

def log_run(metrics: dict, who: str, pair_id: str, tier: str, method: str, stamp: str):
    """stamp: 'YYYYMMDD_HHMM'. One file per run. Never append to a shared CSV."""
    out = Path("evaluation/runs"); out.mkdir(parents=True, exist_ok=True)
    row = {"who": who, "pair_id": pair_id, "tier": tier, "method": method, **metrics}
    pd.DataFrame([row]).to_csv(out / f"run_{stamp}_{who}_{pair_id}_{method}.csv", index=False)

def collect() -> pd.DataFrame:
    """Merge every run into the single results_log.csv. Samrudh runs this."""
    files = sorted(Path("evaluation/runs").glob("*.csv"))
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df.to_csv("evaluation/results_log.csv", index=False)
    return df
```

Individual run files never collide because the filename contains who, what and when.
**Samrudh runs `collect()` once a day** and commits the merged `results_log.csv`. He is the only
person who writes that file — which also makes him the single custodian of every number in the
project, exactly as his role requires.

---

## WHAT GOES WHERE — QUICK LOOKUP

| Artifact | Git | Drive | Why |
|---|---|---|---|
| `.py` files | ✅ | ❌ | text, tiny, needs history |
| `pairs_catalogue.csv`, `DATASET_CARD.md` | ✅ | ❌ | text, everyone needs it |
| `results_log.csv`, run files | ✅ | ❌ | text, and it's our proof |
| `.md` guides | ✅ | ❌ | |
| Cropped image pairs (`data/pairs/`) | ❌ | ✅ | tens of MB each |
| Raw downloads (750 MB ZIPs) | ❌ | ❌ | **Rohan's PC only.** Nobody else needs them. |
| Model weights (`weights/`) | ❌ | ✅ | ~50 MB binary, needed offline at Gate 4 |
| `demo_cache/` | ❌ | ✅ | needed on Samartha's laptop for Gate 4 |
| Failure gallery JPEGs | ✅ | ❌ | small, and Saniya needs them in the deck |
| Backup demo video | ❌ | ✅ | plus a local copy on a phone |
| Deck `.pptx` | ✅ | ❌ | Saniya's folder, small |

**Rule of thumb: under 5 MB and text-ish → Git. Over that, or binary → Drive.**

---

## WHAT WHATSAPP IS ACTUALLY FOR

Not files. Three things:

1. **"Done" messages** — *"Pushed Tier A pairs + catalogue. 6 pairs in Drive `pairs/`. Risheeth,
   you're unblocked."*
2. **Blockers, within 30 minutes** — *"metrics.py wants (N,2) float32, my SIFT returns a list of
   DMatch. Adapter or change the interface?"*
3. **The daily standup** — one line each, same time daily. Show an artifact, not a status:
   *"Pushed `shaded_relief.py`, renders the DEM at any sun angle, screenshot below"*
   beats *"worked on evaluation"*.

**Pin in the group:** repo URL · Drive folder URL · standup time · this document.

---

## NIGHTLY SPECS GO IN GITHUB ISSUES

Samartha writes five specs a night. Put each one in a **GitHub Issue**, assigned to that person,
titled `[Day 4] Samrudh — metrics.py tests`.

Why not WhatsApp: specs scroll away, and by Day 6 nobody can find Day 3's acceptance criteria.
Issues are permanent, addressable, checkable off, and never conflict.

Each person closes their own issue when done. Anyone can see at a glance what everyone is on.

---

## THE SIX GIT COMMANDS YOU ACTUALLY NEED

```bash
git pull                       # get everyone's latest — do this FIRST, every session
git status                     # what have I changed?
git add .                      # stage my changes
git commit -m "message"        # save them locally
git push                       # share them
git log --oneline -10          # what's happened recently
```

That's it. You will not need anything else.

---

## WHEN IT BREAKS — GIT TROUBLESHOOTING

| Message | What it means | Do this |
|---|---|---|
| `Updates were rejected` | Someone pushed since your last pull | `git pull` then `git push` |
| `CONFLICT (content): ...` | You both edited the same file | Post in chat. **Do not guess.** Whoever owns the folder resolves it. |
| `fatal: not a git repository` | Wrong directory | `cd sih26166` |
| `Permission denied` / auth prompt | Not signed in | Install GitHub CLI (`gh auth login`) or use a personal access token |
| `file is 754.00 MB; exceeds limit` | You tried to commit data | It belongs in Drive. `git reset HEAD <file>`, then add it to `.gitignore` |
| Drive file exists but Python can't open it | Not downloaded, just a link | Right-click → **Make available offline** |
| **You've made a mess and are stuck** | | **Stop. Post in chat.** Do not run commands you found online — `git reset --hard` deletes work permanently. Samartha fixes it in two minutes. |

> Nothing in Git is truly lost once committed. Almost every "I destroyed everything" turns out to
> be recoverable. **Committing often is what makes that true** — commit at the end of every
> session even if the work is unfinished.

---

## THE HANDOFF CHAIN — WHO UNBLOCKS WHOM

```
Rohan   ──▶ pairs + catalogue ──▶ Samartha, Samrudh, Risheeth, Rishabh
Samrudh ──▶ evaluate()        ──▶ Samartha, Risheeth
Samartha──▶ aligned outputs   ──▶ Rishabh
        └─▶ illumination.py   ──▶ Risheeth (the ablation)
Risheeth──▶ baseline numbers  ──▶ Saniya, Samartha (UI)
Rishabh ──▶ detect_changes()  ──▶ Samartha (UI)
Samrudh ──▶ results_log.csv   ──▶ Saniya (every number in the deck)
```

**Every arrow is a file in the repo or in Drive. Not a message, not an attachment.**

And note the design: on Days 1–2 **nobody is waiting on anyone**. Risheeth and Rishabh both build
their own test pairs in five lines. Samrudh needs one DEM tile. That was deliberate — the first
draft of the plan had two people starting blocked on Day 2.

---

## FIRST-DAY CHECKLIST

**Samartha:** repo created · `.gitignore` committed **first** · 5 collaborators added · Drive folder
shared · skeleton pushed · both links pinned in WhatsApp

**Everyone else:** Git installed · repo cloned · Drive Desktop installed and folder **offline** ·
`data_path.txt` created · venv + requirements installed · **one test commit pushed** (edit the
README, add your name) so we know your setup works before you need it

> Do the test commit on Day 1. Discovering on Day 5 that your Git auth doesn't work costs you a
> session you don't have.
