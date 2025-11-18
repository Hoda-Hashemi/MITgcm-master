#!/usr/bin/env python3
"""
Initializer for the QGS tutorial.

Generates:
- U_init.bin
- V_init.bin
- ETA_init.bin
- DEPTH.bin

All are Fortran-unformatted single-record float32 by default. See write_mitgcm_bin.write_fortran_binary options.

Usage example:
python init_qgs.py --nx 1440 --ny 720 --H 4000 --dt 60 --L 1e6 --U0 0.1 --center-lon 180 --center-lat 0 --outdir ./input --precision float32
"""
import os
import argparse
import numpy as np
from write_mitgcm_bin import write_fortran_binary
import grid_tools as gt
from constants import g as GRAV, DEFAULT_H

def build_streamfunction(lon_deg, lat_deg, lon0, lat0, L, psi0):
    """Return psi on (nx,ny) grid (lon major axis first).
    lon_deg: 1D array nx
    lat_deg: 1D array ny
    psi0: amplitude [m^2/s], L: scale [m]
    """
    nx = lon_deg.size
    ny = lat_deg.size
    lon2d = np.repeat(lon_deg[:,None], ny, axis=1)
    lat2d = np.repeat(lat_deg[None,:], nx, axis=0)
    # compute local separation in meters (use approximate local coordinates: dx ~ R cos(lat0)*(dlon), dy ~ R*(dlat))
    R = 6.371e6
    # Great-circle differences in radians:
    dlon = np.deg2rad(lon2d - lon0)
    dlat = np.deg2rad(lat2d - lat0)
    # projected distances (approx, using lat0's cos factor for zonal scale)
    x = R * np.cos(np.deg2rad(lat0)) * dlon
    y = R * dlat
    r2 = x**2 + y**2
    psi = psi0 * np.exp(-0.5 * r2 / (L**2))
    return psi

def compute_uv_eta_from_psi(psi, lon_deg, lat_deg):
    """Compute geostrophic u = -dpsi/dy, v = dpsi/dx (account metrics), and eta = f * psi / g.
    psi is shape (nx,ny). Returns u,v,eta arrays same shape (nx,ny) with zonal-major axis first.
    """
    nx, ny = psi.shape
    # compute dx,dy arrays (meters)
    dx, dy = gt.dx_dy_arrays(lon_deg, lat_deg)
    f = gt.f_cor(lat_deg)
    # derivatives: dpsi/dx (zonal), dpsi/dy (meridional)
    # central differences interior; forward/back at edges (periodic in lon assumed)
    dpsi_dx = np.zeros_like(psi)
    # periodic in lon
    dpsi_dx[1:-1,:] = (psi[2:,:] - psi[0:-2,:]) / (dx[1:-1,:]*2.0)
    # edges (use periodic neighbors)
    dpsi_dx[0,:] = (psi[1,:] - psi[-1,:]) / ( (dx[0,:] + dx[-1,:]) / 2.0 * 2.0 )
    dpsi_dx[-1,:] = (psi[0,:] - psi[-2,:]) / ( (dx[0,:] + dx[-1,:]) / 2.0 * 2.0 )

    dpsi_dy = np.zeros_like(psi)
    # non-periodic in lat; use one-sided at boundaries
    dpsi_dy[:,1:-1] = (psi[:,2:] - psi[:,0:-2]) / (dy[:,1:-1]*2.0)
    dpsi_dy[:,0] = (psi[:,1] - psi[:,0]) / dy[:,0]
    dpsi_dy[:,-1] = (psi[:,-1] - psi[:,-2]) / dy[:,-1]

    # geostrophic velocities
    # u = -dpsi/dy, v = +dpsi/dx
    u = - dpsi_dy
    v =   dpsi_dx

    # compute eta = f * psi / g ; f depends on latitude only (shape ny), broadcast to shape (nx,ny)
    f2d = np.repeat(f[None,:], nx, axis=0)
    eta = (f2d * psi) / GRAV

    return u, v, eta

def find_psi0_for_U0(lon_deg, lat_deg, lon0, lat0, L, U0):
    """Find psi0 amplitude necessary to get peak speed ~ U0.
    Use finite-difference estimate: derive psi, compute u,v, get max speed, scale psi0.
    """
    psi0_test = 1.0
    psi = build_streamfunction(lon_deg, lat_deg, lon0, lat0, L, psi0_test)
    u_test, v_test, _ = compute_uv_eta_from_psi(psi, lon_deg, lat_deg)
    Umax = np.max(np.sqrt(u_test**2 + v_test**2))
    if Umax == 0:
        return 0.0
    scale = U0 / Umax
    return psi0_test * scale

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nx', type=int, default=1440)
    parser.add_argument('--ny', type=int, default=720)
    parser.add_argument('--H', type=float, default=DEFAULT_H)
    parser.add_argument('--dt', type=float, default=60.0)
    parser.add_argument('--L', type=float, default=1e6)
    parser.add_argument('--U0', type=float, default=0.1)
    parser.add_argument('--center-lon', type=float, default=180.0)
    parser.add_argument('--center-lat', type=float, default=0.0)
    parser.add_argument('--outdir', type=str, default='./input')
    parser.add_argument('--precision', type=str, choices=['float32','float64'], default='float32')
    parser.add_argument('--endian', type=str, choices=['<','>'], default='<', help='endianness for binary (default little)')
    args = parser.parse_args()

    nx = args.nx; ny = args.ny
    os.makedirs(args.outdir, exist_ok=True)

    lon, lat = gt.latlon_arrays(nx, ny)
    # compute psi0 required for approximate U0
    psi0 = find_psi0_for_U0(lon, lat, args.center_lon, args.center_lat, args.L, args.U0)
    print("Computed psi0 amplitude:", psi0)

    psi = build_streamfunction(lon, lat, args.center_lon, args.center_lat, args.L, psi0)
    u, v, eta = compute_uv_eta_from_psi(psi, lon, lat)

    # depth field: constant H everywhere
    depth = np.ones_like(eta) * args.H

    # write files in NX x NY order (lon-major axis first)
    Ufile = os.path.join(args.outdir, 'U_init.bin')
    Vfile = os.path.join(args.outdir, 'V_init.bin')
    ETfile = os.path.join(args.outdir, 'ETA_init.bin')
    Hfile = os.path.join(args.outdir, 'DEPTH.bin')

    print("Writing files to:", args.outdir)
    write_fortran_binary(Ufile, u.astype(args.precision), precision=args.precision, endian=args.endian)
    write_fortran_binary(Vfile, v.astype(args.precision), precision=args.precision, endian=args.endian)
    write_fortran_binary(ETfile, eta.astype(args.precision), precision=args.precision, endian=args.endian)
    write_fortran_binary(Hfile, depth.astype(args.precision), precision=args.precision, endian=args.endian)

    # write metadata
    meta = {
        'nx': nx, 'ny': ny, 'lon0': float(lon[0]), 'lat0': float(lat[0]),
        'dlon_deg': 360.0/nx, 'dlat_deg': 180.0/ny,
        'H': args.H, 'g': GRAV, 'Omega': 7.2921159e-5,
        'psi0': float(psi0), 'L': args.L, 'U0_target': args.U0,
        'precision': args.precision, 'endian': args.endian
    }
    import json
    with open(os.path.join(args.outdir, 'init_meta.json'), 'w') as f:
        json.dump(meta, f, indent=2)
    print("Wrote init_meta.json")

if __name__ == "__main__":
    main()
