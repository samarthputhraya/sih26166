"""
One-off: fetch and verify the LoFTR weights. Run once per machine, with network.

    <venv>/Scripts/python.exe core/fetch_weights.py

Why this exists as a script rather than a few lines in a chat log: `weights/` is
gitignored, so a fresh clone cannot run anything that needs the matcher until the
weights are rebuilt. Every teammate hits this, and so does any Gate-4 recovery on
a reimaged machine. It has to be reproducible.

Three things here are not obvious and cost time if rediscovered:

1. SSL. The upstream host's chain does not validate against the Windows store on
   this network - `LoFTR(pretrained="outdoor")` dies with CERTIFICATE_VERIFY_FAILED.
   Pointing at certifi's CA bundle fixes it.

2. Provenance. kornia fetches LoFTR's weights over PLAINTEXT http from a single
   researcher's personal university page, performs no hash or signature check of
   any kind, and then unpickles the result with weights_only=False. We verify the
   digest here and afterwards load only with weights_only=True.

3. What gets distributed. We re-serialise the checkpoint's state_dict to
   weights/loftr_outdoor.pt and ship THAT to the team via Drive, so nobody else
   has to depend on a personal academic webpage still being up in December.
"""
from __future__ import annotations

import hashlib
import pathlib
import shutil
import ssl
import sys
import time
import urllib.request

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from core.bench_loftr_cpu import (  # noqa: E402
    UPSTREAM_BYTES, UPSTREAM_CKPT, UPSTREAM_SHA256,
    WEIGHTS, WEIGHTS_BYTES, WEIGHTS_SHA256, no_network,
)

URL = "https://cmp.felk.cvut.cz/~mishkdmy/models/loftr_outdoor.ckpt"


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    print("Fetching LoFTR outdoor weights (one-off, needs network)\n")

    if UPSTREAM_CKPT.exists() and sha256(UPSTREAM_CKPT) == UPSTREAM_SHA256:
        print(f"  upstream checkpoint already cached and verified:\n    {UPSTREAM_CKPT}")
    else:
        try:
            import certifi
        except ImportError:
            print("  certifi is missing - pip install certifi (it ships with requests)")
            return 1

        UPSTREAM_CKPT.parent.mkdir(parents=True, exist_ok=True)
        tmp = UPSTREAM_CKPT.with_suffix(".partial")
        ctx = ssl.create_default_context(cafile=certifi.where())
        print(f"  downloading {URL}")
        print("    (plaintext-http upstream, no integrity check of its own - we verify below)")
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(URL, context=ctx, timeout=180) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f)
        except Exception as e:
            tmp.unlink(missing_ok=True)
            print(f"  DOWNLOAD FAILED: {type(e).__name__}: {e}")
            print("  If this host is down, ask a teammate for weights/loftr_outdoor.pt from Drive.")
            return 1
        # Move into place only once complete, so a killed download cannot leave a
        # truncated file that later looks cached.
        tmp.replace(UPSTREAM_CKPT)
        print(f"    {UPSTREAM_CKPT.stat().st_size / 1e6:.1f} MB in {time.perf_counter() - t0:.1f}s")

        n, d = UPSTREAM_CKPT.stat().st_size, sha256(UPSTREAM_CKPT)
        if (n, d) != (UPSTREAM_BYTES, UPSTREAM_SHA256):
            print(f"  INTEGRITY CHECK FAILED\n    expected {UPSTREAM_BYTES} / {UPSTREAM_SHA256}"
                  f"\n    got      {n} / {d}")
            print("  Do NOT use this file. The upstream content changed or the download was tampered with.")
            return 1
        print(f"  verified sha256 {d[:16]}...")

    # Build offline from the cache and re-serialise what we actually distribute.
    from kornia.feature import LoFTR
    print("\n  building LoFTR from the cached checkpoint (network blocked)...")
    with no_network():
        m = LoFTR(pretrained="outdoor").eval()
    WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
    torch.save(m.state_dict(), WEIGHTS)

    n, d = WEIGHTS.stat().st_size, sha256(WEIGHTS)
    print(f"  wrote {WEIGHTS}  ({n / 1e6:.1f} MB)")
    if (n, d) != (WEIGHTS_BYTES, WEIGHTS_SHA256):
        print(f"\n  NOTE: digest {d[:16]}... differs from the pin in bench_loftr_cpu.py.")
        print("  torch.save output depends on the torch version. If you upgraded torch")
        print("  deliberately, re-pin WEIGHTS_BYTES/WEIGHTS_SHA256 there. Otherwise stop")
        print("  and find out why before benchmarking - numbers must stay comparable.")
        return 1
    print(f"  verified sha256 {d[:16]}...")
    print("\n  Done. Upload weights/loftr_outdoor.pt to the Drive folder so nobody else")
    print("  has to depend on a personal academic webpage still being up in December.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
