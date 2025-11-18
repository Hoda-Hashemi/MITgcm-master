#!/usr/bin/env python3
"""
Check advective and gravity-wave CFL numbers for initial condition.

Usage:
python check_cfl.py Ufile Vfile --H 4000 --dt 60 --nx 1440 --ny 720 [--precision float32] [--endian <]
"""
import sys
import argparse
import numpy as np
from grid_tools import latlon_arrays, dx_dy_arrays
from constants import g as GRAV

def read_fortran_binary(filename, shape, dtype=np.float32, endian='<'):
    # read single-record Fortran-unformatted file and return numpy array reshaped to `shape`
    import struct
    with open(filename,'rb') as f:
        rec1 = f.read(4)
        reclen = struct.unpack(endian + 'i', rec1)[0]
        data = f.read(reclen)
        rec2 = f.read(4)
    arr = np.frombuffer(data, dtype=dtype.newbyteorder(endian))
    arr = arr.reshape(shape)
    return arr

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('Ufile')
    parser.add_argument('Vfile')
    parser.add_argument('--H', type=float, default=4000.0)
    parser.add_argument('--dt', type=float, default=60.0)
    parser.add_argument('--nx', type=int, default=1440)
    parser.add_argument('--ny', type=int, default=720)
    parser.add_argument('--precision', choices=['float32','float64'], default='float32')
    parser.add_argument('--endian', choices=['<','>'], default='<')
    args = parser.parse_args()

    nx, ny = args.nx, args.ny
    dtype = np.dtype(args.precision)
    lon, lat = latlon_arrays(nx, ny)
    dx, dy = dx_dy_arrays(lon, lat)

    U = read_fortran_binary(args.Ufile, (nx,ny), dtype=dtype, endian=args.endian)
    V = read_fortran_binary(args.Vfile, (nx,ny), dtype=dtype, endian=args.endian)

    dt = args.dt
    adv_cfl = np.max(np.abs(U)*dt/dx + np.abs(V)*dt/dy)
    c = np.sqrt(GRAV * args.H)
    grav_cfl = np.max(c * dt / dx)

    print("Advective CFL (max(|u|dt/dx + |v|dt/dy)) =", adv_cfl)
    print("Gravity-wave CFL (max(c dt/dx)) =", grav_cfl)
    print("Recommended dt (for gravity CFL<0.5): dt <= {{:.1f}} s".format(0.5*np.min(dx)/c))

if __name__ == "__main__":
    main()
