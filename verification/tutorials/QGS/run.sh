#!/usr/bin/env bash
# Simple run helper for the QGS tutorial
# Usage: ./run.sh [--init-only]
# Requires: Python3 with numpy, and a compiled MITgcm binary if you want to run the model.

set -e

# configuration
NX=1440
NY=720
H=4000
DT=60
L=1e6
U0=0.1
CENTER_LON=180
CENTER_LAT=0
OUTDIR=./input
MITGCM_BIN=${MITGCM_BIN:-/path/to/mitgcmuv}  # set this env var to run MITgcm

# create input directory
mkdir -p "${OUTDIR}"

echo "Generating initial condition (NX=${NX}, NY=${NY}, H=${H}, dt=${DT})..."
python3 init_qgs.py --nx ${NX} --ny ${NY} --H ${H} --dt ${DT} --L ${L} --U0 ${U0} --center-lon ${CENTER_LON} --center-lat ${CENTER_LAT} --outdir ${OUTDIR}

echo "Checking CFL..."
python3 check_cfl.py ${OUTDIR}/U_init.bin ${OUTDIR}/V_init.bin --H ${H} --dt ${DT} --nx ${NX} --ny ${NY}

echo "Plotting initial fields..."
python3 plot_initial.py ${OUTDIR}/U_init.bin ${OUTDIR}/V_init.bin ${OUTDIR}/ETA_init.bin --nx ${NX} --ny ${NY}

if [ "$1" = "--init-only" ]; then
  echo "Initialization complete. Exiting (init-only)."
  exit 0
fi

if [ ! -x "${MITGCM_BIN}" ]; then
  echo "MITgcm binary not found or not executable: ${MITGCM_BIN}"
  echo "Set MITGCM_BIN to your compiled MITgcm executable to run the model."
  exit 1
fi

echo "Running MITgcm: ${MITGCM_BIN}"
# Note: replace run command below with your usual MPI launcher and configuration.
# Example: mpirun -np 48 ${MITGCM_BIN} > mitgcm.log
${MITGCM_BIN}
