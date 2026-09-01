import numpy as np

def render_shaded_relief(dem, sun_azimuth_deg, sun_elevation_deg, pixel_size_m):
    """Render a DEM as a shaded-relief image lit from a given sun position.

    This is standard hillshade. The point: the SAME terrain lit from two different
    sun positions gives two images with genuinely different shadows -- and we know
    exactly how their pixels correspond, because it is the same grid.
    """
    dzdx, dzdy = np.gradient(dem.astype(np.float64), pixel_size_m)
    slope  = np.arctan(np.hypot(dzdx, dzdy))
    aspect = np.arctan2(-dzdy, dzdx)
    az = np.deg2rad(360.0 - sun_azimuth_deg + 90.0)
    ze = np.deg2rad(90.0 - sun_elevation_deg)
    shade = (np.cos(ze) * np.cos(slope)
             + np.sin(ze) * np.sin(slope) * np.cos(az - aspect))
    return np.clip(shade, 0, 1).astype(np.float32)