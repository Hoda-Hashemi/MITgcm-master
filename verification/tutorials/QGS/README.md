# QGS — Quasi‑Geostrophic‑like Single‑Layer Shallow‑Water Tutorial

This tutorial sets up a single-layer rotating shallow‑water experiment on a global spherical lat–lon grid (nlat=720, nlon=1440) with constant depth (no bathymetry). The initial condition is a small-amplitude, QG-consistent Gaussian streamfunction (so the flow starts near geostrophic balance). A Python initializer writes Fortran-unformatted (Fortran record framed) binary files for U, V and ETA initial fields and the constant depth.

Quick overview
- Grid: 1440 (lon) × 720 (lat), equal angular spacing 0.25°.
- Physical: R = 6.371e6 m, Ω = 7.2921159e-5 s⁻1, g = 9.81 m s⁻2, H = 4000 m (default).
- Time step: dt = 60 s (default).
- Initial flow: Gaussian streamfunction -> geostrophic-balanced η and geostrophic u,v.
- Binary format: Fortran-unformatted record markers, float32 by default (see init_qgs.py for flags).

Files in this folder
- data — model control / parameter template (edit to match your local MITgcm build and I/O variable names)
- data.pkg — package switches (template)
- diag_table — diagnostics output template
- run.sh — small helper to build inputs and (optionally) run MITgcm (you must set MITGCM_BIN)
- init_qgs.py — Python initializer that creates initial U, V, ETA and depth binary files
- write_mitgcm_bin.py — helper to write Fortran-unformatted binary arrays used by init_qgs.py
- grid_tools.py — grid and metric utilities (lat/lon arrays, dx/dy, f)
- check_cfl.py — compute CFL numbers for the initial condition
- plot_initial.py — quick plotting script for initial fields
- constants.py — canonical constants (g, R, Omega, default H)
- slurm.sh.template — optional job script template for HPC runs

How to create inputs (quick)
1. Ensure you have Python 3 with numpy (and matplotlib if you want plotting).
2. Generate initial condition:
   python init_qgs.py --nx 1440 --ny 720 --H 4000 --dt 60 --L 1e6 --U0 0.1 --center-lon 180 --center-lat 0 --outdir ./input
   This writes float32 Fortran-unformatted files: U_init.bin, V_init.bin, ETA_init.bin, DEPTH.bin in `./input`.
3. Inspect CFL and plots:
   python check_cfl.py ./input/U_init.bin ./input/V_init.bin --H 4000 --dt 60 --nx 1440 --ny 720
   python plot_initial.py ./input/U_init.bin ./input/V_init.bin ./input/ETA_init.bin --nx 1440 --ny 720
4. Configure `data` to point to these filenames (and ensure your MITgcm build expects float32/unformatted Fortran records). Then run MITgcm as usual.

Notes
- The initializer writes arrays in NX (lon) × NY (lat) ordering consistent with the scripts here; if your MITgcm configuration uses a different ordering, swap axes accordingly before running.
- Default precision is float32; if your MITgcm build is double precision, re-run `init_qgs.py --precision float64`.
- The `data` and `data.pkg` files are templates: adjust package names and exact parameter keys to match the conventions of your MITgcm build / the `tutorial_global_oce_latlon` you already have.

Contact and next steps
- If you want me to adjust the data file to match a specific MITgcm `data` template you have (e.g., exact variable names, restart filenames, or precision details), paste that `data` and `data.pkg` and I will produce an exact patch.