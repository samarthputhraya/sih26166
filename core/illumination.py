"""
Illumination normalisation - making a crater look the same at two sun angles.

    from core.illumination import normalize
    img_n = normalize(img)                      # pipeline entry point
    img_n = normalize(img, method="phase_congruency")

Canonical Facts Sec.6.4 locks the decision as *"phase congruency OR
sign-invariant gradient orientation - A/B test both."* Both live here behind one
contract so the A/B is a one-line change, not a rewrite.

WHY THIS MODULE EXISTS AT ALL
-----------------------------
The problem statement is registration across *different illumination*. The same
crater lit from the east and from the west casts shadows on opposite sides, so
raw pixel intensity is anti-correlated between the two views. A matcher keyed to
intensity is being asked to match a thing to its own negative. What survives a
change of sun angle is not brightness but STRUCTURE - where the edges are, not
which side of them is bright.

Both methods here discard brightness and keep structure. They differ in how.

  gradient_orientation  Edge DIRECTION modulo pi. Cheap (two finite-difference
                        passes), exactly invariant to I -> a*I + b for any
                        a != 0 - including a < 0, the shadow-reversal case.
  phase_congruency      Kovesi's measure of how well local Fourier phases align,
                        computed here on the monogenic signal. Invariant to the
                        same family, and additionally responds to structure that
                        gradients miss (soft shadow gradients, low-contrast
                        rims) because it keys on phase rather than amplitude.
                        Costs one FFT per scale.

THE CONTRACT - AND THE TRAP IN IT
---------------------------------
*** normalize() RETURNS AN ARRAY IN [0, 255], NOT [0, 1]. ***

`core.matcher._to_tensor` applies a fixed `a / 255.0` to whatever it is handed.
That is deliberate and documented there: LoFTR needs [0, 1] and the loader must
not rescale science data, so exactly one place divides. This module sits BETWEEN
the loader and the matcher, so it has to hand on something DN-shaped.

Return [0, 1] from here and the matcher divides by 255 a second time. Every
pixel lands in [0, 0.004], the image is flat to LoFTR, and you get zero matches
with NO exception - the same silent failure matcher.py's docstring calls "the
most dangerous behaviour in the whole pipeline". It would read as "illumination
normalisation broke the matcher" when the arithmetic is what broke.

Both methods below work in [0, 1] because that is natural for them. The
conversion to [0, 255] happens once, in `normalize()`, for the same reason the
division happens once in the matcher.

NOT CLAIMED HERE
----------------
Which method is better. That is what `core/bench_illumination.py` measures, and
the number goes into `evaluation/results_log.csv` before it goes into a slide.
"""
from __future__ import annotations

import numpy as np

DN_MAX = 255.0          # the matcher divides by exactly this
DEFAULT_METHOD = "gradient_orientation"

# --- phase congruency parameters (Kovesi's published defaults) --------------
PC_N_SCALES = 4
PC_MIN_WAVELENGTH = 3.0
PC_MULT = 2.1
PC_SIGMA_ON_F = 0.55    # log-Gabor bandwidth; 0.55 is about 2 octaves
PC_NOISE_K = 2.0        # noise threshold, in standard deviations


def _as_float(img: np.ndarray) -> np.ndarray:
    """(H, W) anything -> (H, W) float32. Rejects colour early and loudly."""
    a = np.asarray(img, dtype=np.float32)
    if a.ndim != 2:
        raise ValueError(
            f"illumination expects a 2-D single-band image, got shape {a.shape}. "
            "core.io_loader.load() returns 2-D; a 3-D array means a colour or "
            "multi-band product got this far by mistake."
        )
    return a


def gradient_orientation(img: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Sign-invariant gradient orientation, returned in [0, 1].

    theta = atan2(gy, gx) mod pi. Taking it modulo pi rather than 2*pi is the
    whole point: a bright-to-dark edge and a dark-to-bright edge differ by
    exactly pi in gradient direction, so the modulo makes a shadow and its
    mirror image identical. That is the sun-angle case.

    Two honest weaknesses, mitigated rather than hidden:

    1. WRAPAROUND. theta near 0 and near pi describe the same edge but land at
       opposite ends of the output range, so a near-horizontal edge can show a
       false discontinuity. This is unavoidable when compressing an angle into
       one channel; it costs a small number of spurious edge responses.
    2. FLAT REGIONS. Where there is no gradient, atan2 returns the orientation
       of the noise. Lunar maria are large and flat, so left alone this fills
       half the frame with high-contrast garbage. Fixed by blending toward a
       neutral 0.5 with weight mag / (mag + k), where k is the median gradient
       magnitude of THIS image - a scale that adapts to the terrain rather than
       a tuned constant that only ever suited the tile it was tuned on.
    """
    a = _as_float(img)
    gy, gx = np.gradient(a)
    gx = gx.astype(np.float32)
    gy = gy.astype(np.float32)

    theta = np.arctan2(gy, gx) % np.pi          # [0, pi)
    mag = np.hypot(gx, gy)

    k = float(np.median(mag))
    if k <= eps:                                # a constant image has no edges
        return np.full(a.shape, 0.5, dtype=np.float32)

    conf = mag / (mag + k)                      # in [0, 1), soft and scale-free
    out = 0.5 + conf * (theta / np.pi - 0.5)
    return out.astype(np.float32)


def _log_gabor_bank(h: int, w: int):
    """Radial log-Gabor filters plus the two Riesz kernels, in frequency space.

    Split out from phase_congruency() so the frequency geometry can be tested on
    its own - a wrong grid is invisible in the output image but silently wrecks
    scale selection.
    """
    fy = np.fft.fftfreq(h).reshape(-1, 1).astype(np.float32)
    fx = np.fft.fftfreq(w).reshape(1, -1).astype(np.float32)
    radius = np.sqrt(fx * fx + fy * fy)
    radius[0, 0] = 1.0                          # avoid log(0); DC is killed below

    # Butterworth lowpass - suppresses the corner artefacts that otherwise ring
    # along the diagonals of the frequency grid.
    lowpass = 1.0 / (1.0 + (radius / 0.45) ** 30)

    filters = []
    for s in range(PC_N_SCALES):
        wavelength = PC_MIN_WAVELENGTH * (PC_MULT ** s)
        f0 = 1.0 / wavelength
        lg = np.exp(-(np.log(radius / f0) ** 2) / (2 * np.log(PC_SIGMA_ON_F) ** 2))
        lg = lg * lowpass
        lg[0, 0] = 0.0                          # no DC: brightness is the thing we drop
        filters.append(lg.astype(np.float32))

    # Riesz transform - the 2-D generalisation of the Hilbert transform, which
    # turns an even bandpass filter into a quadrature (even, odd) pair without
    # looping over orientations. Kernel is -i * u / |u|.
    riesz_x = (-1j * fx / radius).astype(np.complex64)
    riesz_y = (-1j * fy / radius).astype(np.complex64)
    riesz_x[0, 0] = 0
    riesz_y[0, 0] = 0
    return filters, riesz_x, riesz_y


def phase_congruency(img: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Kovesi phase congruency on the monogenic signal, returned in [0, 1].

    Phase congruency asks: at this pixel, do the Fourier components across all
    scales agree on where they sit in their cycle? At an edge they do; in a
    smooth ramp they do not. Because the answer depends only on phase alignment
    and is divided by total amplitude, scaling or offsetting the image changes
    nothing - which is exactly the invariance a sun-angle change needs.

    The monogenic formulation (Felsberg) is used instead of Kovesi's original
    bank of oriented filters: it needs one FFT per scale rather than one per
    scale per orientation. On the CPU-only demo machine that is the difference
    between a step we can afford in the demo path and one we cannot.
    """
    a = _as_float(img)
    h, w = a.shape
    if h < 4 or w < 4:                          # too small for a 4-scale bank
        return np.zeros((h, w), dtype=np.float32)

    filters, riesz_x, riesz_y = _log_gabor_bank(h, w)
    F = np.fft.fft2(a)

    sum_e = np.zeros((h, w), np.float32)
    sum_o1 = np.zeros((h, w), np.float32)
    sum_o2 = np.zeros((h, w), np.float32)
    sum_amp = np.zeros((h, w), np.float32)
    tau = None

    for s, lg in enumerate(filters):
        bp = F * lg
        e = np.real(np.fft.ifft2(bp)).astype(np.float32)             # even
        o1 = np.real(np.fft.ifft2(bp * riesz_x)).astype(np.float32)  # odd
        o2 = np.real(np.fft.ifft2(bp * riesz_y)).astype(np.float32)
        amp = np.sqrt(e * e + o1 * o1 + o2 * o2).astype(np.float32)

        if s == 0:
            # Kovesi's noise estimate: filter responses to pure noise are
            # Rayleigh distributed, and the smallest scale is the most
            # noise-dominated, so its median amplitude fixes the noise scale for
            # every scale via the known geometric sum.
            tau = float(np.median(amp)) / np.sqrt(np.log(4.0))

        sum_e += e
        sum_o1 += o1
        sum_o2 += o2
        sum_amp += amp

    energy = np.sqrt(sum_e ** 2 + sum_o1 ** 2 + sum_o2 ** 2).astype(np.float32)

    if tau and tau > eps:
        inv = 1.0 / PC_MULT
        total_tau = tau * (1.0 - inv ** PC_N_SCALES) / (1.0 - inv)
        noise_mean = total_tau * np.sqrt(np.pi / 2.0)
        noise_sigma = total_tau * np.sqrt((4.0 - np.pi) / 2.0)
        energy = np.maximum(energy - (noise_mean + PC_NOISE_K * noise_sigma), 0.0)

    pc = energy / (sum_amp + eps)
    return np.clip(pc, 0.0, 1.0).astype(np.float32)


METHODS = {
    "gradient_orientation": gradient_orientation,
    "phase_congruency": phase_congruency,
}


def normalize(img: np.ndarray, method: str = DEFAULT_METHOD) -> np.ndarray:
    """Illumination-normalise one image. Returns float32 in [0, 255].

    The [0, 255] is not decoration - see the module docstring. `core.matcher`
    divides by 255 unconditionally, so this is the range that survives the trip.
    """
    if method not in METHODS:
        raise ValueError(
            f"unknown illumination method {method!r}; have {sorted(METHODS)}"
        )
    return (METHODS[method](img) * DN_MAX).astype(np.float32)
