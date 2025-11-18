"""
Grid and metric utilities for the lat-lon grid.

Functions:
- latlon_arrays(nx, ny): returns lon (deg east, shape (nx,)), lat (deg north, shape (ny,))
- f_cor(lat): Coriolis parameter f = 2*Omega*sin(phi) for latitudes in degrees.
- dx_dy_arrays(lon, lat): returns dx (m, shape (nx,ny)), dy (m, shape (nx,ny)) (dx varies with cos(lat))
- area_array(lon, lat): area of each grid cell [m^2]
"""

import numpy as np
from constants import R_EARTH as R

def latlon_arrays(nx, ny, lon0=0.0):
    """Return 1D lon (0..360) and lat (-90..90) in degrees for cell centers with equal angular spacing.
    lon0 is starting longitude in degrees (default 0.0)."""
    dlon = 360.0 / nx
    dlat = 180.0 / ny
    # cell-centered coordinates:
    lon = (lon0 + dlon*(0.5 + np.arange(nx))) % 360.0
    lat = -90.0 + dlat*(0.5 + np.arange(ny))
    return lon, lat

def f_cor(lat_deg):
    """Return Coriolis parameter f = 2*Omega*sin(phi) for latitudes in degrees."""
    from constants import OMEGA
    phi = np.deg2rad(lat_deg)
    return 2.0 * OMEGA * np.sin(phi)

def dx_dy_arrays(lon_deg, lat_deg):
    """Return dx, dy arrays (in meters) defined at cell centers.
    dx varies with latitude: dx = R * cos(phi) * dlon(rad)
dy = R * dlat(rad)"""
    nx = lon_deg.size
    ny = lat_deg.size
    dlon = 2.0 * np.pi / nx
    dlat = np.pi / ny
    lon2d = np.repeat(lon_deg[:,None], ny, axis=1)
    lat2d = np.repeat(lat_deg[None,:], nx, axis=0)
    dy = R * dlat * np.ones_like(lon2d)
    dx = R * np.cos(np.deg2rad(lat2d)) * dlon
    return dx, dy

def area_array(lon_deg, lat_deg):
    """Area of each cell (approx): dx*dy at cell center."""
    dx, dy = dx_dy_arrays(lon_deg, lat_deg)
    return dx*dy
