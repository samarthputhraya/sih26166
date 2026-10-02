"""Where the Sun stands over the Moon at a given time: the sub-solar point, from first principles.

PRADAN's footprint catalogue carries no Sun (its incidence/emission/phase fields are all zero), so a
tool that picks a reference by its Sun has to compute it. This does, with no ephemeris file and no
dependency: J. Meeus, *Astronomical Algorithms* (2nd ed., 1998) -
  ch. 22  nutation in longitude (the four largest terms),
  ch. 25  the Sun's apparent longitude and distance (low precision, ~0.01 deg),
  ch. 47  the Moon's longitude, latitude and distance (the leading terms of tables 47.A/47.B),
  ch. 53  the Sun's selenographic position (heliocentric Moon, then the optical-libration formulae).
Physical libration (< 0.04 deg) is ignored, and Delta T is taken as 69 s. The result is checked
against LROC's own published sub-solar points (ops/test_lunar_sun.py); it is good to ~0.1 deg, far
finer than the tens of degrees that separate a good reference from a bad one.

    from ops.lunar_sun import subsolar, sun_at
    lat, lon = subsolar("2020-07-27T03:24:37")          # selenographic, degrees, lon east 0-360
    inc, az = sun_at("2020-07-27T03:24:37", -14.44, 25.24)   # at a site: incidence, azimuth from north
"""
from __future__ import annotations

import datetime as _dt
import math

DELTA_T_S = 69.0
AU_KM = 149_597_870.7
I_DEG = 1.54242                      # inclination of the mean lunar equator to the ecliptic

# Meeus table 47.A: (D, M, M', F, sum_l coefficient 1e-6 deg, sum_r coefficient 1e-3 km)
_LR = ((0, 0, 1, 0, 6288774, -20905355), (2, 0, -1, 0, 1274027, -3699111), (2, 0, 0, 0, 658314, -2955968),
       (0, 0, 2, 0, 213618, -569925), (0, 1, 0, 0, -185116, 48888), (0, 0, 0, 2, -114332, -3149),
       (2, 0, -2, 0, 58793, 246158), (2, -1, -1, 0, 57066, -152138), (2, 0, 1, 0, 53322, -170733),
       (2, -1, 0, 0, 45758, -204586), (0, 1, -1, 0, -40923, -129620), (1, 0, 0, 0, -34720, 108743),
       (0, 1, 1, 0, -30383, 104755), (2, 0, 0, -2, 15327, 10321), (0, 0, 1, 2, -12528, 0),
       (0, 0, 1, -2, 10980, 79661), (4, 0, -1, 0, 10675, -34782), (0, 0, 3, 0, 10034, -23210),
       (4, 0, -2, 0, 8548, -21636), (2, 1, -1, 0, -7888, 24208), (2, 1, 0, 0, -6766, 30824),
       (1, 0, -1, 0, -5163, -8379), (1, 1, 0, 0, 4987, -16675), (2, -1, 1, 0, 4036, -12831),
       (2, 0, 2, 0, 3994, -10445), (4, 0, 0, 0, 3861, -11650), (2, 0, -3, 0, 3665, 14403),
       (0, 1, -2, 0, -2689, -7003), (2, 0, -1, 2, -2602, 0), (2, -1, -2, 0, 2390, 10056),
       (1, 0, 1, 0, -2348, 6322), (2, -2, 0, 0, 2236, -9884))
# Meeus table 47.B: (D, M, M', F, sum_b coefficient 1e-6 deg)
_B = ((0, 0, 0, 1, 5128122), (0, 0, 1, 1, 280602), (0, 0, 1, -1, 277693), (2, 0, 0, -1, 173237),
      (2, 0, -1, 1, 55413), (2, 0, -1, -1, 46271), (2, 0, 0, 1, 32573), (0, 0, 2, 1, 17198),
      (2, 0, 1, -1, 9266), (0, 0, 2, -1, 8822), (2, -1, 0, -1, 8216), (2, 0, -2, -1, 4324),
      (2, 0, 1, 1, 4200), (2, 1, 0, -1, -3359), (2, -1, -1, 1, 2463), (2, -1, 0, 1, 2211),
      (2, -1, -1, -1, 2065))


def _sin(d):
    return math.sin(math.radians(d))


def _cos(d):
    return math.cos(math.radians(d))


def julian_ephemeris_day(t) -> float:
    """JDE of a UTC time given as a datetime or an ISO string (a trailing Z is allowed)."""
    if isinstance(t, str):
        s = t.strip().replace("Z", "+00:00")
        t = _dt.datetime.fromisoformat(s)
    if t.tzinfo is not None:
        t = t.astimezone(_dt.timezone.utc).replace(tzinfo=None)
    j2000 = _dt.datetime(2000, 1, 1, 12, 0, 0)
    return 2451545.0 + (t - j2000).total_seconds() / 86400.0 + DELTA_T_S / 86400.0


def _arguments(T):
    Lp = 218.3164477 + 481267.88123421 * T - 0.0015786 * T ** 2 + T ** 3 / 538841 - T ** 4 / 65194000
    D = 297.8501921 + 445267.1114034 * T - 0.0018819 * T ** 2 + T ** 3 / 545868 - T ** 4 / 113065000
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T ** 2 + T ** 3 / 24490000
    Mp = 134.9633964 + 477198.8675055 * T + 0.0087414 * T ** 2 + T ** 3 / 69699 - T ** 4 / 14712000
    F = 93.2720950 + 483202.0175233 * T - 0.0036539 * T ** 2 - T ** 3 / 3526000 + T ** 4 / 863310000
    Om = 125.0445479 - 1934.1362891 * T + 0.0020754 * T ** 2 + T ** 3 / 467441 - T ** 4 / 60616000
    return Lp, D, M, Mp, F, Om


def moon(T):
    """The Moon's geometric ecliptic longitude, latitude (deg) and distance (km), mean equinox of date."""
    Lp, D, M, Mp, F, _ = _arguments(T)
    E = 1 - 0.002516 * T - 0.0000074 * T ** 2
    sl = sr = sb = 0.0
    for d, m, mp, f, cl, cr in _LR:
        e = E ** abs(m)
        arg = d * D + m * M + mp * Mp + f * F
        sl += cl * e * _sin(arg)
        sr += cr * e * _cos(arg)
    for d, m, mp, f, cb in _B:
        sb += cb * E ** abs(m) * _sin(d * D + m * M + mp * Mp + f * F)
    A1, A2, A3 = 119.75 + 131.849 * T, 53.09 + 479264.290 * T, 313.45 + 481266.484 * T
    sl += 3958 * _sin(A1) + 1962 * _sin(Lp - F) + 318 * _sin(A2)
    sb += (-2235 * _sin(Lp) + 382 * _sin(A3) + 175 * _sin(A1 - F) + 175 * _sin(A1 + F)
           + 127 * _sin(Lp - Mp) - 115 * _sin(Lp + Mp))
    return (Lp + sl / 1e6) % 360.0, sb / 1e6, 385000.56 + sr / 1000.0


def nutation_longitude(T) -> float:
    Om = 125.04452 - 1934.136261 * T
    L, Lp = 280.4665 + 36000.7698 * T, 218.3165 + 481267.8813 * T
    return (-17.20 * _sin(Om) - 1.32 * _sin(2 * L) - 0.23 * _sin(2 * Lp) + 0.21 * _sin(2 * Om)) / 3600.0


def sun(T):
    """The Sun's apparent ecliptic longitude (deg) and its distance (km)."""
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T ** 2
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T ** 2
    e = 0.016708634 - 0.000042037 * T - 0.0000001267 * T ** 2
    C = ((1.914602 - 0.004817 * T - 0.000014 * T ** 2) * _sin(M) + (0.019993 - 0.000101 * T) * _sin(2 * M)
         + 0.000289 * _sin(3 * M))
    nu = M + C
    R = 1.000001018 * (1 - e ** 2) / (1 + e * _cos(nu))
    om = 125.04 - 1934.136 * T
    return (L0 + C - 0.00569 - 0.00478 * _sin(om)) % 360.0, R * AU_KM


def subsolar(t) -> tuple[float, float]:
    """Selenographic latitude and east longitude (0-360) of the sub-solar point at UTC time `t`."""
    T = (julian_ephemeris_day(t) - 2451545.0) / 36525.0
    lam, beta, delta = moon(T)
    dpsi = nutation_longitude(T)
    lam += dpsi                                      # apparent
    lam0, R = sun(T)
    # Meeus ch. 53: the heliocentric position of the Moon...
    lam_h = lam0 + 180.0 + (delta / R) * 57.296 * _cos(beta) * _sin(lam0 - lam)
    beta_h = (delta / R) * beta
    # ...then the optical-libration formulae (53.1) with it in place of the geocentric position.
    _, _, _, _, F, Om = _arguments(T)
    W = lam_h - dpsi - Om
    A = math.degrees(math.atan2(_sin(W) * _cos(beta_h) * _cos(I_DEG) - _sin(beta_h) * _sin(I_DEG),
                                _cos(W) * _cos(beta_h)))
    lon = (A - F) % 360.0
    lat = math.degrees(math.asin(-_sin(W) * _cos(beta_h) * _sin(I_DEG) - _sin(beta_h) * _cos(I_DEG)))
    return lat, lon


def sun_at(t, lat: float, lon: float) -> tuple[float, float]:
    """(incidence, azimuth from north, clockwise) of the Sun at selenographic (lat, lon east) at `t`."""
    slat, slon = subsolar(t)
    p, q = math.radians(lat), math.radians(slat)
    dl = math.radians(slon - lon)
    cos_i = math.sin(p) * math.sin(q) + math.cos(p) * math.cos(q) * math.cos(dl)
    inc = math.degrees(math.acos(max(-1.0, min(1.0, cos_i))))
    az = math.degrees(math.atan2(math.sin(dl) * math.cos(q),
                                 math.cos(p) * math.sin(q) - math.sin(p) * math.cos(q) * math.cos(dl))) % 360.0
    return inc, az


def sun_angle_between(t1, t2, lat: float, lon: float) -> float:
    """Angle (deg) between the Sun directions at one site at two times: 0 = the same light."""
    def vec(t):
        inc, az = sun_at(t, lat, lon)
        e = math.radians(90.0 - inc)
        a = math.radians(az)
        return (math.cos(e) * math.sin(a), math.cos(e) * math.cos(a), math.sin(e))
    u, v = vec(t1), vec(t2)
    return math.degrees(math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(u, v))))))
