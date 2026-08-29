# Day 1 — shared setup (paste at the top of every issue)

Repo: `https://github.com/samarthputhraya/sih26166` · private · branch `main`

```bash
# 1. Clone. On Windows use `python`, never `python3` (it opens the Microsoft Store and fails).
git clone https://github.com/samarthputhraya/sih26166.git C:\Users\<you>\sih26166
cd C:\Users\<you>\sih26166

# 2. venv OUTSIDE the OneDrive-synced folder. Not optional — OneDrive syncing
#    thousands of venv files will hang your machine.
python -m venv C:\Users\<you>\venvs\sih26166
C:\Users\<you>\venvs\sih26166\Scripts\activate
python -m pip install --upgrade pip

# 3. Install ONLY the line in your own spec. Do NOT run
#    `pip install -r requirements.txt` today — it pulls ~250 MB of torch that
#    nobody needs on Day 1, plus rasterio, which is currently broken (see below).

# 4. Identify yourself to git, once.
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**Everyone: make one test commit today** — add your name to `README.md`, push. Discovering broken
git auth on Day 5 costs a session nobody has.

**If your collaborator invite has not arrived**, do not stall. None of the five Day-1 tasks read
anything from the repo. Work in a plain local folder and copy your files in once the clone works.

---

## Two environment facts, verified on the demo machine today

**`rasterio` is installed but unusable.** `import rasterio` raises:

```
ImportError: DLL load failed while importing _base: An Application Control policy has blocked this file.
```

Windows Application Control is blocking its bundled GDAL DLLs. Do not try to fix it — Samartha owns
this. No Day-1 task needs it.

**`cv2.AKAZE_create()` does not exist in our pinned OpenCV 5.0.0.93.** AKAZE, KAZE and BRISK moved
into `cv2.xfeatures2d`. Use `cv2.xfeatures2d.AKAZE_create()`. Do not "fix" this by downgrading
OpenCV — that desynchronises the team's pinned versions and loses SIFT.

## The rule that overrides convenience

No number enters a slide, README, demo script or Q&A answer until it exists in
`evaluation/results_log.csv`. That file does not exist yet. Until then, write `[TBD — results_log.csv]`.
