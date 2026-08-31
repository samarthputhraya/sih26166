import shapefile
import csv
import math
import re
from shapely.geometry import Polygon


# ============================================================
# CONFIGURATION
# ============================================================

LROC_SHP = r"lroc_coverage\moon_lro_lroc_edrnac4_sa.shp"

OHRC_CSV = (
    r"C:\Users\Rohan R Shahare\Downloads\LROC_EDR\ch2_test"
    r"\geometry\calibrated\20260103"
    r"\ch2_ohr_ncp_20260103T1005176450_g_grd_d18.csv"
)

OUTPUT_CSV = "lroc_ohrc_matches.csv"

MOON_RADIUS = 1737400.0


# ============================================================
# MOON SOUTH-POLAR STEREOGRAPHIC
# ============================================================

def moon_south_pole_stereo(lon_deg, lat_deg):
    """
    Moon 2000 South Pole Stereographic.

    Parameters:
        lon_deg : longitude in degrees
        lat_deg : latitude in degrees

    Returns:
        x, y in metres
    """

    lon = math.radians(lon_deg)
    lat = math.radians(lat_deg)

    # Angular distance from South Pole.
    #
    # At latitude -90:
    #     rho = 0
    #
    # At latitude -85:
    #     rho ~ 152 km
    #
    rho = 2.0 * MOON_RADIUS * math.tan(
        (math.pi / 2.0 + lat) / 2.0
    )

    # South-polar orientation used by the LROC coverage.
    x = rho * math.sin(lon)
    y = -rho * math.cos(lon)

    return x, y


# ============================================================
# READ OHRC GEOMETRY
# ============================================================

print()
print("=" * 70)
print("READING OHRC GEOMETRY")
print("=" * 70)

points = []

with open(OHRC_CSV, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        lon = float(row["Longitude"])
        lat = float(row["Latitude"])

        x, y = moon_south_pole_stereo(lon, lat)

        points.append((x, y))

print("OHRC points:", len(points))

if len(points) < 3:
    raise RuntimeError("Not enough OHRC geometry points.")


# Convex hull
ohrc_polygon = Polygon(points).convex_hull

print(
    "OHRC convex hull area:",
    f"{ohrc_polygon.area:,.2f}",
    "m²"
)

xmin, ymin, xmax, ymax = ohrc_polygon.bounds

print("OHRC projected bounds:")
print(f"  X: {xmin:,.2f} to {xmax:,.2f}")
print(f"  Y: {ymin:,.2f} to {ymax:,.2f}")


# ============================================================
# READ LROC COVERAGE
# ============================================================

print()
print("=" * 70)
print("READING LROC COVERAGE")
print("=" * 70)

reader = shapefile.Reader(LROC_SHP)

fields = [field[0] for field in reader.fields[1:]]
field_index = {name: i for i, name in enumerate(fields)}

print("LROC records:", len(reader))
print("Shape type:", reader.shapeType)


# ============================================================
# SCAN LROC FOOTPRINTS
# ============================================================

print()
print("=" * 70)
print("SCANNING LROC FOOTPRINTS")
print("=" * 70)

candidates = []

for number, (record, shape) in enumerate(
    zip(reader.iterRecords(), reader.iterShapes()),
    start=1
):

    # Fast bounding-box rejection first.
    sxmin, symin, sxmax, symax = shape.bbox

    if sxmax < xmin:
        continue

    if sxmin > xmax:
        continue

    if symax < ymin:
        continue

    if symin > ymax:
        continue

    # Only create a Shapely polygon for bbox candidates.
    footprint = Polygon(shape.points)

    if not footprint.is_valid:
        footprint = footprint.buffer(0)

    if footprint.intersects(ohrc_polygon):

        candidates.append({
            "record": record,
            "shape": shape
        })

    if number % 50000 == 0:
        print(f"  Scanned {number:,} / {len(reader):,}")


# ============================================================
# RESULTS
# ============================================================

print()
print("=" * 70)
print("RESULTS")
print("=" * 70)

print("Candidates:", len(candidates))


# ============================================================
# IDENTIFY STEREO PAIRS
# ============================================================

print()
print("=" * 70)
print("STEREO PAIRS")
print("=" * 70)

# LROC NAC products normally look like:
#
# nac.m1416248489le
# nac.m1416248489re
#
# The numeric observation ID is shared between LE and RE.

pairs = {}

for item in candidates:

    record = item["record"]

    product_id = str(
        record[field_index["ProductId"]]
    ).strip()

    match = re.search(
        r"\.m(\d+)(le|re)$",
        product_id,
        re.IGNORECASE
    )

    if not match:
        continue

    observation_id = match.group(1)
    side = match.group(2).upper()

    if observation_id not in pairs:
        pairs[observation_id] = {}

    pairs[observation_id][side] = item


complete_pairs = []

for observation_id, sides in pairs.items():

    if "LE" in sides and "RE" in sides:

        complete_pairs.append(
            (
                observation_id,
                sides["LE"],
                sides["RE"]
            )
        )

print("Complete LE/RE pairs:", len(complete_pairs))


# ============================================================
# DISPLAY MATCHES
# ============================================================

print()
print("--- FIRST 50 CANDIDATES ---")

for i, item in enumerate(candidates[:50], start=1):

    record = item["record"]

    product_id = str(
        record[field_index["ProductId"]]
    ).strip()

    utc_start = str(
        record[field_index["UTCstart"]]
    ).strip()

    utc_end = str(
        record[field_index["UTCend"]]
    ).strip()

    center_lat = record[field_index["CenterLat"]]
    center_lon = record[field_index["CenterLon"]]

    print(
        f"{i:3d}. "
        f"{product_id} | "
        f"{utc_start} -> {utc_end} | "
        f"Center: {center_lat}, {center_lon}"
    )


# ============================================================
# WRITE CSV
# ============================================================

print()
print("Writing:", OUTPUT_CSV)

with open(
    OUTPUT_CSV,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "ProductId",
        "UTCstart",
        "UTCend",
        "CenterLat",
        "CenterLon",
        "MinLat",
        "MaxLat",
        "WestLon",
        "EastLon",
        "ExtURL",
        "ProdURL",
        "FilesURL",
        "LabelURL"
    ])

    for item in candidates:

        record = item["record"]

        writer.writerow([
            str(record[field_index["ProductId"]]).strip(),
            str(record[field_index["UTCstart"]]).strip(),
            str(record[field_index["UTCend"]]).strip(),
            record[field_index["CenterLat"]],
            record[field_index["CenterLon"]],
            record[field_index["MinLat"]],
            record[field_index["MaxLat"]],
            record[field_index["WestLon"]],
            record[field_index["EastLon"]],
            str(record[field_index["ExtURL"]]).strip(),
            str(record[field_index["ProdURL"]]).strip(),
            str(record[field_index["FilesURL"]]).strip(),
            str(record[field_index["LabelURL"]]).strip()
        ])


print()
print("=" * 70)
print("DONE")
print("=" * 70)
print("Saved:", OUTPUT_CSV)