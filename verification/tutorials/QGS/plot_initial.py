#!/usr/bin/env python3
"""
Quick plotting script for initial condition.

python plot_initial.py Ufile Vfile ETAfile --nx 1440 --ny 720 --outdir ./figs
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
from grid_tools import latlon_arrays
from check_cfl import read_fortran_binary

def plot_quiver(lon, lat, U, V, subs=8, outname='uv.png'):
    lon2d = np.repeat(lon[:,None], lat.size, axis=1)
    lat2d = np.repeat(lat[None,:], lon.size, axis=0)
    fig, ax = plt.subplots(figsize=(12,6))
    q = ax.quiver(lon2d[::subs,::subs], lat2d[::subs,::subs], U[::subs,::subs].T, V[::subs,::subs].T, scale=1.0)
    ax.set_xlabel('lon')
    ax.set_ylabel('lat')
    ax.set_title('Initial velocity vectors (subset)')
    fig.savefig(outname, dpi=150)
    plt.close(fig)

def plot_eta(lon, lat, ETA, outname='eta.png'):
    lon2d = np.repeat(lon[:,None], lat.size, axis=1)
    lat2d = np.repeat(lat[None,:], lon.size, axis=0)
    fig, ax = plt.subplots(figsize=(12,6))
    im = ax.pcolormesh(lon2d, lat2d, ETA.T, shading='auto')
    fig.colorbar(im, ax=ax)
    ax.set_xlabel('lon')
    ax.set_ylabel('lat')
    ax.set_title('Initial ETA')
    fig.savefig(outname, dpi=150)
    plt.close(fig)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('Ufile')
    parser.add_argument('Vfile')
    parser.add_argument('ETAfile')
    parser.add_argument('--nx', type=int, default=1440)
    parser.add_argument('--ny', type=int, default=720)
    parser.add_argument('--precision', choices=['float32','float64'], default='float32')
    parser.add_argument('--endian', choices=['<','>'], default='<')
    parser.add_argument('--outdir', type=str, default='./figs')
    args = parser.parse_args()
    import os
    os.makedirs(args.outdir, exist_ok=True)

    dtype = np.dtype(args.precision)
    lon, lat = latlon_arrays(args.nx, args.ny)
    U = read_fortran_binary(args.Ufile, (args.nx, args.ny), dtype=dtype, endian=args.endian)
    V = read_fortran_binary(args.Vfile, (args.nx, args.ny), dtype=dtype, endian=args.endian)
    ETA = read_fortran_binary(args.ETAfile, (args.nx, args.ny), dtype=dtype, endian=args.endian)

    plot_eta(lon, lat, ETA, outname=os.path.join(args.outdir, 'ETA_init.png'))
    plot_quiver(lon, lat, U, V, outname=os.path.join(args.outdir, 'UV_init.png'))

if __name__ == "__main__":
    main()
