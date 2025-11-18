"""
Write Fortran-unformatted binary files expected by MITgcm initial condition readers.

Functions:
- write_fortran_binary(filename, array, precision='float32', order='C', endian='<')

By default writes little-endian float32 with 4-byte Fortran record markers.
"""
import numpy as np
import struct
import sys

def write_fortran_binary(filename, array, precision='float32', endian='<'):
    """Write `array` to `filename` as a single Fortran unformatted record.
    - precision: 'float32' or 'float64'
    - endian: '<' little-endian, '>' big-endian
    The array is written in C order (last index fastest). MITgcm expects records framed by 4-byte integers.
    """
    dtype = np.dtype(precision).newbyteorder(endian)
    a = np.asarray(array, dtype=dtype, order='C')
    # ensure contiguous
    data = a.tobytes()
    reclen = len(data)
    # Fortran record marker: 4-byte signed integer
    # Write: int32(reclen), data, int32(reclen)
    with open(filename, 'wb') as f:
        f.write(struct.pack(endian + 'i', reclen))
        f.write(data)
        f.write(struct.pack(endian + 'i', reclen))

if __name__ == "__main__":
    # simple CLI: write a sample file if executed directly
    import numpy as np
    arr = np.arange(12.0, dtype=np.float32).reshape((3,4))
    write_fortran_binary('test_field.bin', arr)
    print("Wrote test_field.bin (3x4 float32) in Fortran-unformatted framing.")
"""
