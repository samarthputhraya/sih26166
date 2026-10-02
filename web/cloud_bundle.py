"""Assemble a self-contained folder that hosts the live workbench in a container.

    python -m web.build_console --site --live-url <service url>     # the page it serves
    python -m web.cloud_bundle <out_dir>
    gcloud run deploy lunaxx --source <out_dir> --region asia-south1 --port 7860 --cpu 2 --memory 4Gi \
        --max-instances 1 --min-instances 0 --concurrency 20 --timeout 300 --no-cpu-throttling \
        --allow-unauthenticated

The container runs `python -m web.server --public` (at most 3 jobs at once, 24 MB per request):
the same code, LoFTR weights and page as the laptop, plus the showcase pairs so "re-run a real
pair live" works there too. `--no-cpu-throttling` matters: a registration runs in a background
thread that the page polls, and Cloud Run's default throttles the CPU between requests.
`--max-instances 1` keeps every poll on the instance that holds the job and caps the cost.

Not on the demo path: the demo runs offline on the laptop (`python -m web.server`). Everything
copied is in git or already on disk (weights/ and data/pairs/ are gitignored but required).
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# the console's showcase pairs, plus the 749 nm twin its 1548 nm refusal is compared against
PAIRS = ["sac_ohrc_nac_w06", "sac_ohrclroc_nacm1356313970le_c17", "siten_ohrc2031_tmc20200607_c03",
         "siten_nacm1282456834re_tmc20200607_c00", "chain_tmc20200607_iirs1555_w05", "siten_ohrc2031_ohrc2229_c15",
         "site_tc_morning_mi1548_w01", "site_tc_morning_mi749_w01", "sac_ohrc_tmc_w01", "sac_tmcfore_tmcaft_w04"]

REQUIREMENTS = """--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.13.0+cpu
kornia==0.8.3
numpy==2.5.2
opencv-contrib-python-headless==5.0.0.93
scipy==1.18.1
pillow==12.3.0
tifffile==2026.8.23
pds4_tools==1.4
pvl==1.3.2
certifi==2026.7.22
psutil==7.2.2
"""

DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libglib2.0-0 && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 user
WORKDIR /home/user/app
COPY --chown=user requirements-cloud.txt .
RUN pip install --no-cache-dir -r requirements-cloud.txt
COPY --chown=user . .
USER user
ENV PYTHONUNBUFFERED=1 OMP_NUM_THREADS=2 LUNAXX_COMMIT={commit}
EXPOSE 7860
CMD ["python", "-m", "web.server", "--host", "0.0.0.0", "--port", "7860", "--public"]
"""


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    out = pathlib.Path(argv[0]).resolve()
    page = ROOT / "web" / "dist" / "mission-console.html"
    weights = ROOT / "weights" / "loftr_outdoor.pt"
    for need in (page, weights, *(ROOT / "data" / "pairs" / p for p in PAIRS)):
        if not need.exists():
            print(f"missing {need}")
            return 2
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    for d in ("core", "evaluation", "web"):
        (out / d).mkdir(exist_ok=True)
        for p in (ROOT / d).glob("*.py"):
            if not p.name.startswith("test_"):
                shutil.copy(p, out / d / p.name)
    (out / "web" / "dist").mkdir(exist_ok=True)
    shutil.copy(page, out / "web" / "dist" / page.name)
    shutil.copytree(ROOT / "web" / "fonts", out / "web" / "fonts", dirs_exist_ok=True)
    (out / "weights").mkdir(exist_ok=True)
    shutil.copy(weights, out / "weights" / weights.name)
    for pid in PAIRS:
        dst = out / "data" / "pairs" / pid
        dst.mkdir(parents=True, exist_ok=True)
        for f in (ROOT / "data" / "pairs" / pid).iterdir():
            if f.is_file() and f.suffix in (".tif", ".json"):
                shutil.copy(f, dst / f.name)
    for f in ("LICENSE", "NOTICE"):
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, out / f)
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    (out / "requirements-cloud.txt").write_text(REQUIREMENTS, encoding="utf-8")
    (out / "Dockerfile").write_text(DOCKERFILE.format(commit=commit), encoding="utf-8")
    files = [p for p in out.rglob("*") if p.is_file()]
    print(f"{out}: {len(files)} files, {sum(p.stat().st_size for p in files) / 1048576:.1f} MB, commit {commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
