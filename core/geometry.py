"""Archive geometry: image pixels <-> lunar south-polar stereographic metres.

Why this exists. A real cross-sensor pair can only be cut, scored and exported if
we know where each image sits on the Moon. Chandrayaan-2 OHRC ships a geolocation
grid (lat/lon every 100 px); an LROC NAC EDR ships nothing in its label, but LROC
publishes its four footprint corners; a Kaguya TC tile and anything we write here
are GeoTIFFs. `Frame` turns each of those into one object with `to_map` and
`from_map`, and `project` resamples any of them onto a shared map grid.

The map is the one the Kaguya TC tile on disk already uses (and LOLA's
ldem_60s_60m): polar stereographic, true scale at the pole, lat origin -90,
lon origin 0, on the IAU 2015 Moon sphere, R = 1737.4 km.
    x = rho * sin(lon),  y = rho * cos(lon),  rho = 2R * tan(45 deg + lat/2)
(`ops/fetch_lola_dem.latlon_to_pixel` uses the same formula.) Scale error vs the
true surface is (1 + sin|lat|)/2 - 1: -1.9 % at 74 S. Every image at the site is
projected the same way, so it cancels in any comparison between them; absolute
metre figures carry it and are labelled "map metres".

What this module does NOT do: orthorectification. There is no DEM in the loop,
so relief displacement stays in the images (both products at this site are
within 2 deg of nadir: a 500 m hill moves at most ~17 m). It is the reason a
homography cannot fit a real pair perfectly, and the reason residuals are
reported rather than assumed away.
"""
from __future__ import annotations

import math
import pathlib
from dataclasses import dataclass, field

import numpy as np

R_MOON_M = 1737400.0
PS_SOUTH_CRS = "Moon (2015) - Sphere / Ocentric / South Polar"

# GeoKeys copied from the GDAL-written Kaguya TC tile (TC1S2B0_01_03482S746E0433.tif):
# projected, PixelIsArea, user-defined polar stereographic, lat origin -90, lon 0,
# scale 1, sphere 1737400 m. Writing the identical block makes QGIS/GDAL treat our
# pairs and the TC tile as one CRS.
_GEOKEY_DIR = (1, 1, 0, 20, 1024, 0, 1, 1, 1025, 0, 1, 1, 1026, 34737, 46, 0,
               2048, 0, 1, 32767, 2049, 34737, 134, 46, 2050, 0, 1, 32767,
               2054, 0, 1, 9102, 2056, 0, 1, 32767, 2057, 34736, 1, 5,
               2058, 34736, 1, 6, 2061, 34736, 1, 7, 3072, 0, 1, 32767,
               3074, 0, 1, 32767, 3075, 0, 1, 15, 3076, 0, 1, 9001,
               3081, 34736, 1, 0, 3082, 34736, 1, 3, 3083, 34736, 1, 4,
               3092, 34736, 1, 2, 3095, 34736, 1, 1)
_GEO_DOUBLES = (-90.0, 0.0, 1.0, 0.0, 0.0, 1737400.0, 1737400.0, 0.0)
_GEO_ASCII = ("Moon (2015) - Sphere / Ocentric / South Polar|GCS Name = Moon (2015) - "
              "Sphere / Ocentric|Datum = Moon (2015) - Sphere|Ellipsoid = Moon (2015) - "
              "Sphere|Primem = Reference Meridian||")


# --- the projection ------------------------------------------------------------

def ps_south(lat_deg, lon_deg):
    """(lat, lon) degrees -> (x, y) map metres. Arrays welcome."""
    lat = np.radians(np.asarray(lat_deg, np.float64))
    lon = np.radians(np.asarray(lon_deg, np.float64))
    rho = 2.0 * R_MOON_M * np.tan(np.pi / 4.0 + lat / 2.0)
    return rho * np.sin(lon), rho * np.cos(lon)


def ps_south_inv(x, y):
    """(x, y) map metres -> (lat, lon) degrees, lon in [0, 360)."""
    x = np.asarray(x, np.float64)
    y = np.asarray(y, np.float64)
    rho = np.hypot(x, y)
    lat = -(90.0 - 2.0 * np.degrees(np.arctan(rho / (2.0 * R_MOON_M))))
    return lat, np.degrees(np.arctan2(x, y)) % 360.0


def sun_direction(lat_deg, lon_deg, subsolar_lat_deg, subsolar_lon_deg):
    """Local incidence and azimuth (deg clockwise from north) of the Sun at a point."""
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    bs, ls = math.radians(subsolar_lat_deg), math.radians(subsolar_lon_deg)
    cos_i = math.sin(lat) * math.sin(bs) + math.cos(lat) * math.cos(bs) * math.cos(ls - lon)
    inc = math.degrees(math.acos(max(-1.0, min(1.0, cos_i))))
    az = math.degrees(math.atan2(math.sin(ls - lon) * math.cos(bs),
                                 math.cos(lat) * math.sin(bs)
                                 - math.sin(lat) * math.cos(bs) * math.cos(ls - lon))) % 360.0
    return inc, az


# --- one image's geometry ------------------------------------------------------

@dataclass
class Frame:
    """Pixel <-> map for one image, from a lattice of nodes.

    `xs`, `ys` are the node positions in image pixels (OpenCV convention: the
    centre of the top-left pixel is (0, 0)); `X`, `Y` are the map coordinates at
    every node, shape (len(ys), len(xs)). Forward mapping is bilinear on the
    lattice; the inverse is piecewise-linear on the triangulated node cloud.
    """
    name: str
    shape: tuple                      # (rows, cols) of the full image
    xs: np.ndarray
    ys: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    source: str = ""                  # where the geometry came from, for provenance
    _inv: object = field(default=None, repr=False)

    # constructors ---------------------------------------------------------------

    @classmethod
    def from_ohrc_grid(cls, csv_path, shape, name=None):
        """Chandrayaan-2 OHRC `*_g_grd_*.csv`: Longitude, Lattitude [sic], Pixel, Scan.

        Pixel = sample = x (0..11999), Scan = line = y. The grid is regular in
        pixel space, every 100 px plus the last row/column.
        """
        g = np.loadtxt(csv_path, delimiter=",", skiprows=1)
        lon, lat, px, sc = g.T
        xs, ys = np.unique(px), np.unique(sc)
        if len(xs) * len(ys) != len(g):
            raise ValueError(f"{csv_path}: grid is not a full lattice "
                             f"({len(xs)} x {len(ys)} != {len(g)} rows)")
        ix = np.searchsorted(xs, px)
        iy = np.searchsorted(ys, sc)
        LAT = np.empty((len(ys), len(xs)))
        LON = np.empty((len(ys), len(xs)))
        LAT[iy, ix], LON[iy, ix] = lat, lon
        X, Y = ps_south(LAT, LON)
        return cls(name or pathlib.Path(csv_path).stem, tuple(shape), xs.astype(float),
                   ys.astype(float), X, Y, source=f"OHRC geolocation grid {pathlib.Path(csv_path).name}")

    @classmethod
    def from_corners(cls, ul, ur, lr, ll, shape, name="", step=256, source="", fwd=None):
        """Four (lat, lon) corners of the image: UL = pixel (0, 0), UR = (cols-1, 0),
        LR = (cols-1, rows-1), LL = (0, rows-1). Bilinear in map metres between them.

        This is what LROC publishes for a NAC EDR, to 0.01 deg (~300 m in latitude).
        It is a coarse prior, not a georeference, and `source` says so.
        `fwd` is the (lat, lon) -> map metres projection; default south polar stereographic.
        """
        rows, cols = shape
        xs = np.unique(np.r_[np.arange(0, cols, step), cols - 1]).astype(float)
        ys = np.unique(np.r_[np.arange(0, rows, step), rows - 1]).astype(float)
        fwd = fwd or ps_south
        P = {k: np.array(fwd(*v)) for k, v in dict(ul=ul, ur=ur, lr=lr, ll=ll).items()}
        u = (xs / (cols - 1))[None, :]
        v = (ys / (rows - 1))[:, None]
        X = ((1 - u) * (1 - v) * P["ul"][0] + u * (1 - v) * P["ur"][0]
             + u * v * P["lr"][0] + (1 - u) * v * P["ll"][0])
        Y = ((1 - u) * (1 - v) * P["ul"][1] + u * (1 - v) * P["ur"][1]
             + u * v * P["lr"][1] + (1 - u) * v * P["ll"][1])
        return cls(name, tuple(shape), xs, ys, X, Y,
                   source=source or "four footprint corners, bilinear (coarse prior)")

    @classmethod
    def from_equirect(cls, max_lat, west_lon, ppd, shape, name="", step=64, source=""):
        """A PDS SIMPLE CYLINDRICAL map (Kaguya TC / MI map products): pixel CENTRE
        (col, row) at lat = max_lat - row/ppd, lon = west_lon + col/ppd - the label's
        corner latitudes/longitudes are pixel centres (e.g. LOWER_LEFT_LATITUDE =
        -74.999756 = -72 - 12287/4096). Nodes every `step` px; the map to polar
        stereographic is smooth on that scale."""
        rows, cols = shape
        xs = np.unique(np.r_[np.arange(0, cols, step), cols - 1]).astype(float)
        ys = np.unique(np.r_[np.arange(0, rows, step), rows - 1]).astype(float)
        LON, LAT = np.meshgrid(west_lon + xs / ppd, max_lat - ys / ppd)
        X, Y = ps_south(LAT, LON)
        return cls(name, tuple(shape), xs, ys, X, Y,
                   source=source or f"simple cylindrical map, {ppd} px/deg, from the PDS label")

    @classmethod
    def from_transform(cls, transform, shape, name="", source="GeoTIFF transform"):
        """A GDAL-order transform (x0, sx, 0, y0, 0, sy) in polar-stereographic metres."""
        x0, sx, rx, y0, ry, sy = transform
        if rx or ry:
            raise ValueError("rotated geotransforms are not supported")
        rows, cols = shape
        xs = np.array([0.0, cols - 1.0])
        ys = np.array([0.0, rows - 1.0])
        X = np.repeat((x0 + (xs + 0.5) * sx)[None, :], 2, axis=0)
        Y = np.repeat((y0 + (ys + 0.5) * sy)[:, None], 2, axis=1)
        return cls(name, tuple(shape), xs, ys, X, Y, source=source)

    # mappings -----------------------------------------------------------------

    def to_map(self, x, y):
        """Image pixel (x, y) -> map (X, Y). Bilinear on the node lattice."""
        x = np.asarray(x, np.float64)
        y = np.asarray(y, np.float64)
        ix = np.clip(np.searchsorted(self.xs, x, side="right") - 1, 0, len(self.xs) - 2)
        iy = np.clip(np.searchsorted(self.ys, y, side="right") - 1, 0, len(self.ys) - 2)
        fx = (x - self.xs[ix]) / (self.xs[ix + 1] - self.xs[ix])
        fy = (y - self.ys[iy]) / (self.ys[iy + 1] - self.ys[iy])

        def lerp(A):
            return ((1 - fx) * (1 - fy) * A[iy, ix] + fx * (1 - fy) * A[iy, ix + 1]
                    + (1 - fx) * fy * A[iy + 1, ix] + fx * fy * A[iy + 1, ix + 1])
        return lerp(self.X), lerp(self.Y)

    def from_map(self, X, Y):
        """Map (X, Y) -> image pixel (x, y); NaN outside the footprint."""
        if self._inv is None:
            from scipy.interpolate import LinearNDInterpolator
            gx, gy = np.meshgrid(self.xs, self.ys)
            pts = np.c_[self.X.ravel(), self.Y.ravel()]
            self._inv = LinearNDInterpolator(pts, np.c_[gx.ravel(), gy.ravel()])
        X = np.asarray(X, np.float64)
        Y = np.asarray(Y, np.float64)
        out = self._inv(np.c_[X.ravel(), Y.ravel()])
        x, y = out[:, 0].copy(), out[:, 1].copy()
        # The triangulated inverse is piecewise-LINEAR; the forward model is bilinear.
        # Two Newton steps against `to_map` make the pair self-consistent to ~1e-6 px
        # (without them the round trip was off by up to 0.06 px - not negligible for a
        # sub-pixel claim that rests on these projections).
        tx, ty = X.ravel(), Y.ravel()
        ok = np.isfinite(x)
        h = 0.5
        for _ in range(2):
            if not ok.any():
                break
            xo, yo = x[ok], y[ok]
            fx, fy = self.to_map(xo, yo)
            ax, ay = self.to_map(xo + h, yo)
            bx, by = self.to_map(xo, yo + h)
            j11, j21 = (ax - fx) / h, (ay - fy) / h
            j12, j22 = (bx - fx) / h, (by - fy) / h
            det = j11 * j22 - j12 * j21
            rx, ry = tx[ok] - fx, ty[ok] - fy
            with np.errstate(divide="ignore", invalid="ignore"):
                dx = (j22 * rx - j12 * ry) / det
                dy = (-j21 * rx + j11 * ry) / det
            good = np.isfinite(dx) & np.isfinite(dy)
            xo[good] += dx[good]
            yo[good] += dy[good]
            x[ok], y[ok] = xo, yo
        return x.reshape(X.shape), y.reshape(X.shape)

    def footprint(self):
        """Boundary polygon in map metres, (N, 2), following the image edges."""
        X, Y = self.X, self.Y
        ring = np.r_[np.c_[X[0, :], Y[0, :]], np.c_[X[1:, -1], Y[1:, -1]],
                     np.c_[X[-1, -2::-1], Y[-1, -2::-1]], np.c_[X[-2:0:-1, 0], Y[-2:0:-1, 0]]]
        return ring

    def gsd(self):
        """Mean map metres per pixel along x and y, from the lattice."""
        dx = np.hypot(np.diff(self.X, axis=1), np.diff(self.Y, axis=1)) / np.diff(self.xs)[None, :]
        dy = np.hypot(np.diff(self.X, axis=0), np.diff(self.Y, axis=0)) / np.diff(self.ys)[:, None]
        return float(np.mean(dx)), float(np.mean(dy))

    def corrected(self, M, note=""):
        """The same frame with an affine correction applied to its MAP coordinates:
        (X, Y) -> (X, Y) + A @ [X - cx, Y - cy, 1], with (cx, cy) = M["centre"].
        M is what `fit_affine_correction` returns."""
        A = np.asarray(M["A"], np.float64)
        cx, cy = M["centre"]
        u, v = self.X - cx, self.Y - cy
        dX = A[0, 0] * u + A[0, 1] * v + A[0, 2]
        dY = A[1, 0] * u + A[1, 1] * v + A[1, 2]
        return Frame(self.name, self.shape, self.xs, self.ys, self.X + dX, self.Y + dY,
                     source=self.source + (f"; affine-corrected {note}" if note else "; affine-corrected"))

    def shifted(self, dX, dY, note=""):
        """The same frame moved by (dX, dY) map metres - a correction to a coarse prior."""
        return Frame(self.name, self.shape, self.xs, self.ys, self.X + dX, self.Y + dY,
                     source=self.source + (f"; shifted ({dX:+.1f}, {dY:+.1f}) m" +
                                           (f" {note}" if note else "")))


# --- map grids, overlap, projection ------------------------------------------------

def map_grid(x_min, y_max, width_m, height_m, gsd):
    """A north-up grid. Returns (transform, (rows, cols)); transform is GDAL order."""
    cols = int(round(width_m / gsd))
    rows = int(round(height_m / gsd))
    return (float(x_min), float(gsd), 0.0, float(y_max), 0.0, -float(gsd)), (rows, cols)


def grid_xy(transform, shape, step=1):
    """Map coordinates of pixel CENTRES of a grid, every `step` pixels (inclusive of the edge)."""
    x0, sx, _, y0, _, sy = transform
    rows, cols = shape
    cs = np.unique(np.r_[np.arange(0, cols, step), cols - 1]).astype(float)
    rs = np.unique(np.r_[np.arange(0, rows, step), rows - 1]).astype(float)
    C, Rr = np.meshgrid(cs, rs)
    return x0 + (C + 0.5) * sx, y0 + (Rr + 0.5) * sy, cs, rs


def overlap_mask(frames, res=10.0, pad=0.0):
    """Raster the intersection of the frames' footprints. Returns (mask, transform).

    Polygons are filled with cv2.fillPoly (a matplotlib point-in-polygon test on every
    cell took minutes for a 45 km NAC strip; this takes milliseconds)."""
    import cv2
    rings = [f.footprint() for f in frames]
    # the INTERSECTION of the bounding boxes: a 45 km NAC strip must not make us
    # rasterise its whole length when it shares 7 km with the other image
    x0 = max(r[:, 0].min() for r in rings) - pad
    y0 = max(r[:, 1].min() for r in rings) - pad
    x1 = min(r[:, 0].max() for r in rings) + pad
    y1 = min(r[:, 1].max() for r in rings) + pad
    if x1 <= x0 or y1 <= y0:
        transform, shape = map_grid(x0, y0 + res, res, res, res)
        return np.zeros(shape, bool), transform
    transform, shape = map_grid(x0, y1, x1 - x0, y1 - y0, res)
    mask = np.ones(shape, bool)
    for ring in rings:
        col = (ring[:, 0] - transform[0]) / res - 0.5
        row = (transform[3] - ring[:, 1]) / res - 0.5
        poly = np.round(np.c_[col, row] * 16).astype(np.int32)      # 4 fractional bits
        m = np.zeros(shape, np.uint8)
        cv2.fillPoly(m, [poly], 1, lineType=cv2.LINE_8, shift=4)
        mask &= m.astype(bool)
    return mask, transform


def _upsample(A, rs, cs, rows, cols):
    """Bilinear upsampling of a tensor-product lattice (rs x cs nodes) to every pixel,
    as two small interpolation-weight matrices: out = Wr @ A @ Wc.T. NaN nodes stay
    NaN (propagated by the weights they touch)."""
    def weights(nodes, n):
        full = np.arange(n, dtype=np.float64)
        i = np.clip(np.searchsorted(nodes, full, side="right") - 1, 0, len(nodes) - 2)
        t = (full - nodes[i]) / (nodes[i + 1] - nodes[i])
        W = np.zeros((n, len(nodes)))
        W[np.arange(n), i] = 1 - t
        W[np.arange(n), i + 1] = t
        return W
    Wr, Wc = weights(rs, rows), weights(cs, cols)
    nan = ~np.isfinite(A)
    A0 = np.where(nan, 0.0, A)
    out = Wr @ A0 @ Wc.T
    if nan.any():
        bad = (Wr @ nan.astype(np.float64) @ Wc.T) > 1e-9
        out[bad] = np.nan
    return out


def project(frame: Frame, read_window, transform, shape, coarse=16, fill=np.nan,
            order="linear"):
    """Resample an image onto a map grid through its Frame.

    read_window(x, y, w, h) -> array returns a window of the SOURCE image (so a
    93,693-line OHRC strip is never loaded whole). The inverse mapping is evaluated
    every `coarse` output pixels and interpolated between - the lattice geometry is
    smooth on that scale. Returns (image float32, valid bool).
    """
    import cv2
    X, Y, cs, rs = grid_xy(transform, shape, step=coarse)
    sx, sy = frame.from_map(X, Y)
    rows, cols = shape
    # upsample the coarse coordinate maps to every output pixel (separable bilinear)
    mx, my = _upsample(sx, rs, cs, rows, cols), _upsample(sy, rs, cs, rows, cols)
    ok = np.isfinite(mx) & np.isfinite(my)
    img = np.full(shape, fill, np.float32)
    if not ok.any():
        return img, ok
    x_lo = max(int(np.floor(np.nanmin(mx[ok]))) - 2, 0)
    y_lo = max(int(np.floor(np.nanmin(my[ok]))) - 2, 0)
    x_hi = min(int(np.ceil(np.nanmax(mx[ok]))) + 3, frame.shape[1])
    y_hi = min(int(np.ceil(np.nanmax(my[ok]))) + 3, frame.shape[0])
    if x_hi <= x_lo or y_hi <= y_lo:
        return img, np.zeros(shape, bool)
    src = np.asarray(read_window(x_lo, y_lo, x_hi - x_lo, y_hi - y_lo), np.float32)
    interp = {"linear": cv2.INTER_LINEAR, "cubic": cv2.INTER_CUBIC,
              "nearest": cv2.INTER_NEAREST}[order]
    mxl = np.where(ok, mx - x_lo, -1).astype(np.float32)
    myl = np.where(ok, my - y_lo, -1).astype(np.float32)
    # Border value 0, and validity decided GEOMETRICALLY (every kernel tap inside the crop).
    # With a NaN border value OpenCV 5.0's cubic remap returned NaN for whole blocks of
    # interior samples - the last row of any window under ~30 px, 2 rows of a 200-px one
    # (core/test_geometry.py) - which cut_* then nearest-filled as "edge_pixels_filled".
    # NaN in the SOURCE (invalid pixels) still propagates, so isfinite(out) stays.
    lo, hi = {"linear": (0, 1), "cubic": (1, 2), "nearest": (0, 0)}[order]
    out = cv2.remap(src, mxl, myl, interpolation=interp, borderMode=cv2.BORDER_CONSTANT,
                    borderValue=0.0)
    valid = ok & (mxl >= lo) & (myl >= lo) & (mxl <= src.shape[1] - 1 - hi) \
        & (myl <= src.shape[0] - 1 - hi) & np.isfinite(out)
    img[valid] = out[valid]
    return img, valid


def fill_invalid(img, valid):
    """Nearest-valid fill for the few edge pixels a projection leaves empty, so a window
    that is 99.9 % covered can still be matched. Returns (filled, n_filled)."""
    from scipy.ndimage import distance_transform_edt
    bad = ~valid
    if not bad.any():
        return img, 0
    idx = distance_transform_edt(bad, return_distances=False, return_indices=True)
    out = img[tuple(idx)]
    return out.astype(img.dtype), int(bad.sum())


def block_mean(read_window, full_shape, factor, band_rows=4096):
    """Downsample a large image by an integer factor, reading it in bands.

    Area averaging, like cv2.INTER_AREA, without ever holding the full image. Used
    for the coarse overview on which the prior is checked.
    """
    rows, cols = full_shape
    r_out, c_out = rows // factor, cols // factor
    out = np.empty((r_out, c_out), np.float32)
    band = max(factor, (band_rows // factor) * factor)
    for r0 in range(0, r_out * factor, band):
        h = min(band, r_out * factor - r0)
        a = np.asarray(read_window(0, r0, c_out * factor, h), np.float32)
        out[r0 // factor:(r0 + h) // factor] = a.reshape(h // factor, factor, c_out, factor).mean(axis=(1, 3))
    return out


# --- writing -------------------------------------------------------------------

def geotiff_tags(transform, nodata=None):
    """tifffile `extratags` for a north-up polar-stereographic GeoTIFF."""
    x0, sx, _, y0, _, sy = transform
    tags = [(33550, 12, 3, (float(sx), float(-sy), 0.0), True),
            (33922, 12, 6, (0.0, 0.0, 0.0, float(x0), float(y0), 0.0), True),
            (34735, 3, len(_GEOKEY_DIR), _GEOKEY_DIR, True),
            (34736, 12, len(_GEO_DOUBLES), _GEO_DOUBLES, True),
            (34737, 2, 0, _GEO_ASCII, True)]
    if nodata is not None:
        tags.append((42113, 2, 0, str(nodata), True))
    return tags


def write_geotiff(path, img, transform, nodata=None):
    """Write a single-band GeoTIFF (uncompressed; imagecodecs is not installed)."""
    import tifffile
    tifffile.imwrite(str(path), np.asarray(img), photometric="minisblack",
                     extratags=geotiff_tags(transform, nodata))
    return pathlib.Path(path)


# --- coarse alignment of two map-projected images ----------------------------------------

def coarse_offset(a, b, valid_a=None, valid_b=None, erode_px=12):
    """Translation of `a` relative to `b` on a shared map grid, by phase correlation of
    gradient-orientation images (illumination-robust; `core/illumination.py`).

    Returns (dx, dy, peak) in grid pixels: a feature at (x, y) in `b` is at
    (x + dx, y + dy) in `a`. Used ONLY to correct a coarse archive prior before
    windows are cut - never as a registration result.
    """
    import cv2
    from core.illumination import normalize

    # One shared support for both images, ERODED after normalisation: gradient
    # orientation is computed on a median-filled image, so the fill boundary itself
    # produces strong structure - identical in both images, at zero shift. Without
    # the erosion the peak is the mask correlating with itself.
    va = np.isfinite(a) if valid_a is None else (valid_a & np.isfinite(a))
    vb = np.isfinite(b) if valid_b is None else (valid_b & np.isfinite(b))
    support = cv2.erode((va & vb).astype(np.uint8), np.ones((erode_px * 2 + 1,) * 2, np.uint8)) > 0

    def prep(img, v):
        img = np.asarray(img, np.float32).copy()
        fillv = float(np.nanmedian(img[v])) if v.any() else 0.0
        img[~v] = fillv
        n = normalize(img, method="gradient_orientation").astype(np.float32)
        n = (n - n[support].mean()) if support.any() else n
        n[~support] = 0.0
        return n * cv2.createHanningWindow(n.shape[::-1], cv2.CV_32F)
    A, B = prep(a, va), prep(b, vb)
    (dx, dy), peak = cv2.phaseCorrelate(B.astype(np.float64), A.astype(np.float64))
    return float(dx), float(dy), float(peak)


def fit_affine_correction(points_m, disp_m, thresh_m=8.0, iters=2000, seed=0):
    """Robust affine displacement field d(X, Y) = A @ [X - cx, Y - cy, 1] from scattered
    offsets (e.g. box-wise correlation peaks). RANSAC on 3-point samples, then least
    squares on the inliers. Returns {"A", "centre", "inliers", "n", "rms_m", "p90_m"}."""
    P = np.asarray(points_m, np.float64)
    D = np.asarray(disp_m, np.float64)
    n = len(P)
    if n < 3:
        return None
    c = P.mean(0)
    U = np.c_[P - c, np.ones(n)]
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(iters):
        idx = rng.choice(n, 3, replace=False)
        A = np.linalg.lstsq(U[idx], D[idx], rcond=None)[0].T
        r = np.hypot(*(U @ A.T - D).T)
        inl = r <= thresh_m
        if best is None or inl.sum() > best.sum():
            best = inl
    if best is None or best.sum() < 3:
        return None
    A = np.linalg.lstsq(U[best], D[best], rcond=None)[0].T
    r = np.hypot(*(U @ A.T - D).T)
    inl = r <= thresh_m
    return {"A": A.tolist(), "centre": c.tolist(), "inliers": int(inl.sum()), "n": int(n),
            "rms_m": float(np.sqrt(np.mean(r[inl] ** 2))), "p90_m": float(np.percentile(r[inl], 90))}
