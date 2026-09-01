"""Find and select Tier A pairs from the LROC NAC PDS index.

WHY THIS EXISTS
---------------
The planned Tier A route was ODE's `EDRNAC4` metadata. The live ODE route is
unavailable, so the PDS CUMINDEX is used as the canonical static source.

The PDS index contains PRODUCT_ID, center latitude/longitude,
INCIDENCE/EMISSION/PHASE_ANGLE, resolution, footprint corners, and the
FILE_SPECIFICATION_NAME.

A NAC EDR is large, but it is uncompressed 8-bit with fixed-size records and
supports HTTP byte ranges. A 640-line crop can therefore be fetched without
downloading the complete product.

THE TEXTURE TEST
----------------
Do not use a raw-EDR `std > 10` threshold. NAC EDR imagery is raw and companded,
so useful frames can have a raw standard deviation around 4-6.

The useful discriminator is row-to-row correlation:

    good terrain: high row correlation
    sensor/noise: low row correlation

`looks_like_terrain()` therefore checks row correlation and DN span.

IMPORTANT GEOMETRY LIMITATION
-----------------------------
The raw-EDR footprint interpolation in `ground_to_pixel()` is suitable only for
selecting a region of interest.

It is NOT accurate enough to claim that two raw EDR crops are co-registered.
A NAC frame is a long pushbroom strip and four footprint corners cannot model
all ground-track curvature and attitude variation.

Genuine map-aligned Tier A crops still require LROC map-projected products
(`LRO-L-LROC-5-RDR-V1.0`) or SPICE/ISIS georeferencing.

This script therefore completes the candidate-selection portion of Day 2.
"""

from __future__ import annotations

import argparse
import csv
import math
import pathlib
import re
import urllib.request
from collections import defaultdict

import numpy as np


PDS = "https://pds.lroc.im-ldi.com/data/"

CUMINDEX = (
    PDS
    + "LRO-L-LROC-2-EDR-V1.0/"
      "LROLRC_0003/INDEX/CUMINDEX.TAB"
)

REC = 901


# Field names and their fixed-width positions in CUMINDEX.TAB.
FIELDS = {
    "file_spec": (16, 75),
    "product_id": (122, 13),
    "emission": (725, 5),
    "incidence": (731, 6),
    "phase": (738, 6),
    "sub_solar_az": (752, 6),
    "lat": (806, 6),
    "lon": (813, 6),
    "scaled_px_width": (702, 7),
    "resolution": (717, 7),
    "altitude": (876, 7),
    "north_azimuth": (745, 6),

    # Footprint corners.
    "ul_lat": (862, 6),
    "ul_lon": (869, 6),
    "ur_lat": (820, 6),
    "ur_lon": (827, 6),
    "ll_lat": (848, 6),
    "ll_lon": (855, 6),
    "lr_lat": (834, 6),
    "lr_lon": (841, 6),
}


def _field(rec: bytes, key: str) -> str:
    """Extract one fixed-width CUMINDEX field."""
    start, n = FIELDS[key]

    return (
        rec[start - 1:start - 1 + n]
        .decode("ascii", "replace")
        .strip()
        .strip('"')
    )


def scan_index(
    out_csv: pathlib.Path,
    inc_range=(20.0, 80.0),
):
    """Stream CUMINDEX and write a compact local catalogue."""

    kept = 0
    total = 0

    with (
        urllib.request.urlopen(CUMINDEX, timeout=900) as stream,
        open(out_csv, "w", newline="", encoding="utf-8") as fh,
    ):
        writer = csv.writer(fh)

        writer.writerow(list(FIELDS))

        buf = b""

        while True:
            chunk = stream.read(REC * 512)

            if not chunk:
                break

            buf += chunk

            while len(buf) >= REC:
                rec, buf = buf[:REC], buf[REC:]

                total += 1

                try:
                    incidence = float(
                        _field(rec, "incidence")
                    )

                    float(_field(rec, "lat"))
                    float(_field(rec, "lon"))

                except ValueError:
                    continue

                if not (
                    inc_range[0]
                    <= incidence
                    <= inc_range[1]
                ):
                    continue

                writer.writerow(
                    [_field(rec, key) for key in FIELDS]
                )

                kept += 1

    return total, kept


def find_pairs(
    catalogue_csv,
    min_inc_diff=15.0,
    max_sep_deg=0.02,
    modes=("LE", "RE"),
    max_res_ratio=1.25,
):
    """Find co-located frames with sufficiently different incidence angles.

    The resolution-ratio limit prevents the pair from becoming a mixed
    illumination-plus-scale experiment.
    """

    rows = []

    with open(
        catalogue_csv,
        newline="",
        encoding="utf-8",
    ) as fh:

        for row in csv.DictReader(fh):

            product_id = row["product_id"]

            if product_id[-2:] not in modes:
                continue

            try:
                resolution = float(
                    row["resolution"]
                )
            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                resolution = float("nan")

            try:
                lat = float(row["lat"])
                lon = float(row["lon"])
                incidence = float(row["incidence"])
            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

            row["res"] = resolution
            row["latf"] = lat
            row["lonf"] = lon
            row["inc"] = incidence

            rows.append(row)

    # Spatial bins reduce the number of pairwise comparisons.
    cells = defaultdict(list)

    for row in rows:
        cells[
            (
                round(row["latf"] / 0.05),
                round(row["lonf"] / 0.05),
            )
        ].append(row)

    pairs = []

    for group in cells.values():

        for i in range(len(group)):

            for j in range(i + 1, len(group)):

                a = group[i]
                b = group[j]

                # Ignore the same NAC product.
                if (
                    a["product_id"][:10]
                    == b["product_id"][:10]
                ):
                    continue

                d_inc = abs(
                    a["inc"] - b["inc"]
                )

                if d_inc < min_inc_diff:
                    continue

                # Approximate angular separation.
                sep = math.hypot(
                    a["latf"] - b["latf"],
                    (
                        a["lonf"] - b["lonf"]
                    )
                    * math.cos(
                        math.radians(a["latf"])
                    ),
                )

                if sep > max_sep_deg:
                    continue

                ra = a["res"]
                rb = b["res"]

                if (
                    ra > 0
                    and rb > 0
                ):
                    ratio = (
                        max(ra, rb)
                        / min(ra, rb)
                    )
                else:
                    ratio = float("inf")

                if ratio > max_res_ratio:
                    continue

                pairs.append(
                    {
                        "a": a["product_id"],
                        "b": b["product_id"],
                        "inc_a": a["inc"],
                        "inc_b": b["inc"],
                        "d_inc": d_inc,
                        "res_a": ra,
                        "res_b": rb,
                        "res_ratio": ratio,
                        "sep_km": sep * 30.3,
                        "lat": a["latf"],
                        "lon": a["lonf"],
                        "file_a": a["file_spec"],
                        "file_b": b["file_spec"],
                    }
                )

    pairs.sort(
        key=lambda pair: (
            -pair["d_inc"],
            pair["sep_km"],
        )
    )

    return pairs


def ground_to_pixel(
    row,
    lat,
    lon,
    lines,
    samples,
):
    """Estimate where (lat, lon) falls in a frame.

    This is ONLY suitable for selecting a region of interest.

    It is NOT accurate enough to claim two raw EDR crops are co-registered.
    """

    ul = (
        float(row["ul_lat"]),
        float(row["ul_lon"]),
    )

    ur = (
        float(row["ur_lat"]),
        float(row["ur_lon"]),
    )

    ll = (
        float(row["ll_lat"]),
        float(row["ll_lon"]),
    )

    lr = (
        float(row["lr_lat"]),
        float(row["lr_lon"]),
    )

    u = 0.5
    v = 0.5

    for _ in range(60):

        top = (
            ul[0] + u * (ur[0] - ul[0]),
            ul[1] + u * (ur[1] - ul[1]),
        )

        bottom = (
            ll[0] + u * (lr[0] - ll[0]),
            ll[1] + u * (lr[1] - ll[1]),
        )

        current = (
            top[0] + v * (bottom[0] - top[0]),
            top[1] + v * (bottom[1] - top[1]),
        )

        r_lat = lat - current[0]
        r_lon = lon - current[1]

        d_du = (
            (ur[0] - ul[0]) * (1 - v)
            + (lr[0] - ll[0]) * v,

            (ur[1] - ul[1]) * (1 - v)
            + (lr[1] - ll[1]) * v,
        )

        d_dv = (
            bottom[0] - top[0],
            bottom[1] - top[1],
        )

        det = (
            d_du[0] * d_dv[1]
            - d_du[1] * d_dv[0]
        )

        if abs(det) < 1e-12:
            break

        du = (
            r_lat * d_dv[1]
            - r_lon * d_dv[0]
        ) / det

        dv = (
            d_du[0] * r_lon
            - d_du[1] * r_lat
        ) / det

        u += du
        v += dv

        if (
            abs(du) < 1e-9
            and abs(dv) < 1e-9
        ):
            break

    return (
        v * (lines - 1),
        u * (samples - 1),
    )


def common_ground(row_a, row_b):
    """Return centre of the two frames' overlapping footprint."""

    def box(row):

        lats = [
            float(row[key])
            for key in (
                "ul_lat",
                "ur_lat",
                "ll_lat",
                "lr_lat",
            )
        ]

        lons = [
            float(row[key])
            for key in (
                "ul_lon",
                "ur_lon",
                "ll_lon",
                "lr_lon",
            )
        ]

        return (
            min(lats),
            max(lats),
            min(lons),
            max(lons),
        )

    a = box(row_a)
    b = box(row_b)

    lat_lo = max(a[0], b[0])
    lat_hi = min(a[1], b[1])

    lon_lo = max(a[2], b[2])
    lon_hi = min(a[3], b[3])

    if (
        lat_lo >= lat_hi
        or lon_lo >= lon_hi
    ):
        return None

    return (
        (lat_lo + lat_hi) / 2.0,
        (lon_lo + lon_hi) / 2.0,
    )


def _label(url):
    """Read PDS image-label fields needed for byte-range cropping."""

    request = urllib.request.Request(
        url,
        headers={
            "Range": "bytes=0-20000"
        },
    )

    text = (
        urllib.request.urlopen(
            request,
            timeout=180,
        )
        .read()
        .replace(b"\x00", b"")
        .decode("ascii", "replace")
    )

    def get_int(key):
        match = re.search(
            key + r"\s*=\s*(\d+)",
            text,
        )

        if not match:
            raise ValueError(
                f"could not find {key} in PDS label"
            )

        return int(match.group(1))

    return (
        get_int("RECORD_BYTES"),
        get_int(r"\^IMAGE"),
        get_int("LINES"),
        get_int("LINE_SAMPLES"),
    )


def crop(
    file_spec,
    line0=None,
    n_lines=640,
    n_cols=640,
):
    """Range-fetch a crop from a NAC EDR."""

    url = PDS + file_spec

    (
        rec_bytes,
        image_rec,
        lines,
        samples,
    ) = _label(url)

    if (
        lines < n_lines
        or samples < n_cols
    ):
        raise ValueError(
            f"frame {file_spec} is smaller than "
            f"requested {n_lines}x{n_cols}: "
            f"{lines}x{samples}"
        )

    if line0 is None:
        line0 = (
            lines // 2
            - n_lines // 2
        )

    line0 = max(
        0,
        min(
            line0,
            lines - n_lines,
        ),
    )

    offset = (
        image_rec - 1
    ) * rec_bytes

    first = (
        offset
        + line0 * rec_bytes
    )

    last = (
        offset
        + (line0 + n_lines)
        * rec_bytes
        - 1
    )

    request = urllib.request.Request(
        url,
        headers={
            "Range": (
                f"bytes={first}-{last}"
            )
        },
    )

    raw = (
        urllib.request.urlopen(
            request,
            timeout=600,
        )
        .read()
    )

    expected = (
        n_lines * rec_bytes
    )

    if len(raw) < expected:
        raise RuntimeError(
            f"short range response for "
            f"{file_spec}: "
            f"{len(raw)} bytes, "
            f"expected {expected}"
        )

    arr = (
        np.frombuffer(
            raw,
            np.uint8,
        )[:expected]
        .reshape(
            n_lines,
            rec_bytes,
        )[:, :samples]
    )

    mid = samples // 2

    return arr[
        :,
        max(
            0,
            mid - n_cols // 2,
        ):mid + n_cols // 2,
    ]


def looks_like_terrain(
    arr,
    min_row_corr=0.80,
    min_dn_span=15,
):
    """Determine whether a raw EDR crop contains usable terrain."""

    x = arr.astype(
        np.float64
    )

    corrs = []

    step = max(
        1,
        len(x) // 32,
    )

    for i in range(
        0,
        len(x) - 1,
        step,
    ):
        corr = np.corrcoef(
            x[i],
            x[i + 1],
        )[0, 1]

        corrs.append(corr)

    row_corr = float(
        np.nanmedian(corrs)
    )

    dn_span = float(
        np.percentile(x, 99)
        - np.percentile(x, 1)
    )

    return {
        "row_corr": row_corr,
        "dn_span": dn_span,
        "raw_std": float(x.std()),
        "ok": bool(
            row_corr >= min_row_corr
            and dn_span >= min_dn_span
        ),
    }


def stretch(
    arr,
    lo_pct=2,
    hi_pct=98,
):
    """Percentile stretch for visual inspection only."""

    x = arr.astype(
        np.float32
    )

    lo, hi = np.percentile(
        x,
        (
            lo_pct,
            hi_pct,
        ),
    )

    return np.clip(
        (
            x - lo
        )
        * 255.0
        / max(
            hi - lo,
            1,
        ),
        0,
        255,
    ).astype(np.uint8)


def evaluate_pair(pair):
    """Download and test both frames in a candidate pair."""

    results = {}

    for tag, file_spec in (
        ("A", pair["file_a"]),
        ("B", pair["file_b"]),
    ):

        try:
            arr = crop(
                file_spec
            )

            results[tag] = (
                looks_like_terrain(arr)
            )

        except Exception as exc:

            results[tag] = {
                "row_corr": float("nan"),
                "dn_span": 0.0,
                "raw_std": float("nan"),
                "ok": False,
                "error": str(exc),
            }

    pair["terrain_a"] = results["A"]
    pair["terrain_b"] = results["B"]

    pair["valid"] = bool(
        results["A"]["ok"]
        and results["B"]["ok"]
    )

    return pair


def save_selected(
    path,
    selected,
):
    """Save selected Tier-A candidates as a compact CSV."""

    fields = [
        "rank",
        "a",
        "b",
        "inc_a",
        "inc_b",
        "d_inc",
        "res_a",
        "res_b",
        "res_ratio",
        "sep_km",
        "lat",
        "lon",
        "terrain_a_row_corr",
        "terrain_a_dn_span",
        "terrain_b_row_corr",
        "terrain_b_dn_span",
        "status",
    ]

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8",
    ) as fh:

        writer = csv.DictWriter(
            fh,
            fieldnames=fields,
        )

        writer.writeheader()

        for rank, pair in enumerate(
            selected,
            1,
        ):

            writer.writerow(
                {
                    "rank": rank,
                    "a": pair["a"],
                    "b": pair["b"],
                    "inc_a": f"{pair['inc_a']:.3f}",
                    "inc_b": f"{pair['inc_b']:.3f}",
                    "d_inc": f"{pair['d_inc']:.3f}",
                    "res_a": f"{pair['res_a']:.6f}",
                    "res_b": f"{pair['res_b']:.6f}",
                    "res_ratio": f"{pair['res_ratio']:.4f}",
                    "sep_km": f"{pair['sep_km']:.4f}",
                    "lat": f"{pair['lat']:.5f}",
                    "lon": f"{pair['lon']:.5f}",
                    "terrain_a_row_corr": (
                        f"{pair['terrain_a']['row_corr']:.4f}"
                    ),
                    "terrain_a_dn_span": (
                        f"{pair['terrain_a']['dn_span']:.2f}"
                    ),
                    "terrain_b_row_corr": (
                        f"{pair['terrain_b']['row_corr']:.4f}"
                    ),
                    "terrain_b_dn_span": (
                        f"{pair['terrain_b']['dn_span']:.2f}"
                    ),
                    "status": "candidate_valid",
                }
            )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Find LROC NAC Tier-A candidates "
            "and select the strongest "
            "terrain-valid pairs."
        )
    )

    parser.add_argument(
        "--catalogue",
        default="nac_catalogue.csv",
        help=(
            "local CUMINDEX-derived "
            "catalogue"
        ),
    )

    parser.add_argument(
        "--output",
        default="tier_a_selected.csv",
        help=(
            "CSV containing selected "
            "Tier-A candidates"
        ),
    )

    parser.add_argument(
        "--count",
        type=int,
        default=6,
        help=(
            "number of valid pairs "
            "to select"
        ),
    )

    parser.add_argument(
        "--min-inc-diff",
        type=float,
        default=15.0,
        help=(
            "minimum incidence-angle "
            "difference"
        ),
    )

    parser.add_argument(
        "--max-sep-deg",
        type=float,
        default=0.02,
        help=(
            "maximum centre separation "
            "in degrees"
        ),
    )

    parser.add_argument(
        "--max-res-ratio",
        type=float,
        default=1.25,
        help=(
            "maximum pixel-resolution "
            "ratio"
        ),
    )

    args = parser.parse_args()

    catalogue = pathlib.Path(
        args.catalogue
    )

    if not catalogue.exists():

        print(
            f"streaming CUMINDEX -> "
            f"{catalogue} "
            "(~203 MB over the wire, "
            "not stored) ..."
        )

        total, kept = scan_index(
            catalogue
        )

        print(
            f"scanned {total} records, "
            f"kept {kept}"
        )

    pairs = find_pairs(
        catalogue,
        min_inc_diff=args.min_inc_diff,
        max_sep_deg=args.max_sep_deg,
        max_res_ratio=args.max_res_ratio,
    )

    print(
        f"\n{len(pairs)} "
        "Tier A candidate pairs\n"
    )

    print(
        f"{'d_inc':>7} "
        f"{'sep_km':>7}  "
        f"{'A':13}"
        f"{'incA':>6}  "
        f"{'B':13}"
        f"{'incB':>6}  "
        f"{'lat':>7}"
        f"{'lon':>8}"
    )

    for pair in pairs[:10]:

        print(
            f"{pair['d_inc']:6.1f}d "
            f"{pair['sep_km']:7.1f}  "
            f"{pair['a']:13}"
            f"{pair['inc_a']:6.1f}  "
            f"{pair['b']:13}"
            f"{pair['inc_b']:6.1f}  "
            f"{pair['lat']:7.2f}"
            f"{pair['lon']:8.2f}"
        )

    if not pairs:

        print(
            "\nNo Tier A candidates found."
        )

        raise SystemExit(1)

    print(
        "\nEvaluating all candidates "
        "for usable terrain..."
    )

    valid = []

    for index, pair in enumerate(
        pairs,
        1,
    ):

        print(
            f"\n[{index}/{len(pairs)}] "
            f"{pair['a']} / "
            f"{pair['b']} "
            f"(d_inc="
            f"{pair['d_inc']:.1f}d)"
        )

        evaluated = evaluate_pair(
            pair
        )

        for tag in (
            "A",
            "B",
        ):

            terrain = evaluated[
                f"terrain_{tag.lower()}"
            ]

            if "error" in terrain:

                print(
                    f"  {tag}: ERROR "
                    f"{terrain['error']}"
                )

            else:

                print(
                    f"  {tag}: "
                    f"row_corr="
                    f"{terrain['row_corr']:.3f} "
                    f"dn_span="
                    f"{terrain['dn_span']:.0f} "
                    f"raw_std="
                    f"{terrain['raw_std']:.1f} "
                    f"-> "
                    f"{'terrain' if terrain['ok'] else 'REJECT'}"
                )

        if evaluated["valid"]:

            valid.append(
                evaluated
            )

            print(
                "  PAIR -> VALID"
            )

        else:

            print(
                "  PAIR -> REJECT"
            )

    valid.sort(
        key=lambda pair: (
            -pair["d_inc"],
            pair["sep_km"],
        )
    )

    selected = valid[
        :args.count
    ]

    print(
        f"\n{len(valid)} "
        "terrain-valid pairs found."
    )

    print(
        f"Selecting the best "
        f"{len(selected)}."
    )

    if selected:

        print(
            "\nSelected Tier A candidates:\n"
        )

        print(
            f"{'rank':>4} "
            f"{'d_inc':>7} "
            f"{'sep_km':>7}  "
            f"{'A':13} "
            f"{'B':13}"
        )

        for rank, pair in enumerate(
            selected,
            1,
        ):

            print(
                f"{rank:4d} "
                f"{pair['d_inc']:6.1f}d "
                f"{pair['sep_km']:7.3f}  "
                f"{pair['a']:13} "
                f"{pair['b']:13}"
            )

    save_selected(
        args.output,
        selected,
    )

    print(
        f"\nSaved selection to: "
        f"{args.output}"
    )

    if len(selected) < args.count:

        print(
            f"WARNING: only "
            f"{len(selected)} valid pairs "
            f"were available; "
            f"{args.count} requested."
        )

    print(
        "\nNOTE: these are "
        "terrain-valid raw-EDR "
        "Tier-A candidates, "
        "not yet map-aligned crops."
    )


if __name__ == "__main__":
    main()