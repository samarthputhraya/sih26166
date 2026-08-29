# [Day 1] Samrudh — `evaluation/shaded_relief.py`

**Time: 2 hrs.** Read `day01_00_SHARED_SETUP.md` first.

> **Your row in `TEAM_TASK_GUIDE.md` says "Download one SLDEM tile." That is not doable today.**
> The 512 ppd float tile is ~1.4 GB and the obvious reader (`rasterio`) is broken on the demo
> machine. Corrected below: fetch a 512×512 window by HTTP Range in well under a minute, using
> numpy and the standard library only.

## Goal, in one sentence
`evaluation/shaded_relief.py` renders a real SLDEM elevation window as a hillshade at any sun
azimuth/elevation, and two opposite azimuths produce visibly opposite shading.

## Signature
```python
def fetch_sldem_window(row0: int = 7000, col0: int = 10000, n: int = 512) -> np.ndarray:
    """Fetch an n x n window of SLDEM2015 512ppd as float64 METRES, via HTTP Range."""

def render_shaded_relief(dem: np.ndarray, sun_azimuth_deg: float,
                         sun_elevation_deg: float, pixel_size_m: float) -> np.ndarray:
    """Lambertian hillshade of a DEM. Returns float32 in [0, 1], same shape as dem."""
```

## Install
```bash
pip install numpy==2.5.2 opencv-contrib-python==5.0.0.93 scikit-image==0.26.0 matplotlib==3.11.1 pandas==3.0.5
```

## Acceptance criteria
1. **Input to `render_shaded_relief`:** `dem` = numpy float, HxW, in **metres** (not km, not raw
   counts); `pixel_size_m = 59.2252938` for this tile.
2. **Output:** numpy **float32**, same HxW, every value within `[0.0, 1.0]`.
3. `fetch_sldem_window(7000, 10000, 512)` returns float64 `(512, 512)`.
4. A `if __name__ == "__main__":` block prints the three test results.

## Test cases
1. `render_range` — output is float32, `min >= 0.0`, `max <= 1.0`.
2. `azimuth_flips_shading` — render at azimuth 45 and at 225, then
   `np.corrcoef(A.ravel(), B.ravel())[0,1]` is **strongly negative** (expect around −0.9 or lower).
   *A strong negative correlation is the entire point* — the same terrain lit from opposite sides.
   A correlation near +1 means your azimuth is not being used at all.
3. `deterministic` — calling twice with identical arguments gives `np.array_equal(A, C) is True`.

> Record the exact numbers you measure in your own docstring. Do not copy expected values from
> anyone's chat message — including this spec — into a slide. They reach a slide only via
> `results_log.csv`.

## Starter
```python
# evaluation/shaded_relief.py
import ssl, urllib.request
import certifi
import numpy as np

# SLDEM2015, 512 pixels/degree. From the PDS3 label:
#   LINE_SAMPLES=23040  SAMPLE_TYPE=PC_REAL  SAMPLE_BITS=32
#   UNIT=KILOMETER      MAP_SCALE=0.0592252938 <km/pix>
SLDEM_URL = ("https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/"
             "lrolol_1xxx/data/sldem2015/tiles/float_img/"
             "sldem2015_512_00n_30n_000_045_float.img")
LINE_SAMPLES = 23040
ROW_BYTES = 92160          # LINE_SAMPLES * 4 bytes
PIXEL_SIZE_M = 59.2252938


def fetch_sldem_window(row0=7000, col0=10000, n=512):
    """Fetch an n x n window as float64 METRES. Range request, tens of MB."""
    # TODO: Request with header Range = f"bytes={row0*ROW_BYTES}-{(row0+n)*ROW_BYTES-1}"
    # TODO: assert the response status is 206  (206 = server honoured the range)
    # TODO: np.frombuffer(buf, dtype="<f4").reshape(n, LINE_SAMPLES)[:, col0:col0+n]
    # TODO: .astype(np.float64) * 1000.0     # the label says UNIT = KILOMETER
    ...


def render_shaded_relief(dem, sun_azimuth_deg, sun_elevation_deg, pixel_size_m):
    """Standard Lambertian hillshade. Same terrain, two sun positions, exact
    pixel correspondence -- which is precisely why this is our ground truth."""
    dzdx, dzdy = np.gradient(dem.astype(np.float64), pixel_size_m)
    slope = np.arctan(np.hypot(dzdx, dzdy))
    aspect = np.arctan2(-dzdy, dzdx)
    az = np.deg2rad(360.0 - sun_azimuth_deg + 90.0)
    ze = np.deg2rad(90.0 - sun_elevation_deg)
    shade = (np.cos(ze) * np.cos(slope)
             + np.sin(ze) * np.sin(slope) * np.cos(az - aspect))
    return np.clip(shade, 0, 1).astype(np.float32)
```

## Dependencies
- Needs **nothing from any teammate**. `evaluation/` exists in commit `7644b4c`.
- Delivers to: yourself Day 2 (`synthetic_data.py` builds on this); Risheeth Day 3.

## Do not
- **Do not `import rasterio`** — Application Control blocks its DLLs on the demo machine. The `.img`
  is a raw little-endian float32 array; `numpy.frombuffer` is all you need and is faster.
- **Do not use `>f4` (big-endian).** `SAMPLE_TYPE = PC_REAL` means **little-endian** → `<f4`.
  Big-endian parses with no error and returns silent garbage around 1e-38. This is the single most
  likely way to lose an hour.
- **Do not download the full ~1.4 GB tile**, and do not use the `.jp2` tiles — JPEG-2000 needs a
  decoder we do not have working.
- **Do not forget the `* 1000.0`.** `UNIT = KILOMETER`. Skipping it makes terrain 1000× flatter and
  the hillshade nearly uniform.
- **Do not call this "real shadows".** `np.clip(shade, 0, 1)` is Lambertian *self*-shading; it does
  not ray-trace cast shadows. Say "shaded relief" until we add them. This matters at Gate 5.

## You are BLOCKED if
The server returns HTTP 200 instead of 206 (range ignored) → **ping Samartha.** Fallback: generate a
synthetic crater DEM in numpy (a few parabolic bowls plus a sinusoidal ramp) and develop
`render_shaded_relief` against that; it gives the same qualitative negative correlation. Swap in
real SLDEM tomorrow.

## The ONE thing most likely to make your Day 1 fail
**You `import rasterio` out of habit, hit the Application Control DLL error, and spend two hours on
a GDAL install.** You do not need rasterio today, tomorrow, or for this file at all.
