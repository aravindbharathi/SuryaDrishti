import os
import sys

from astropy.io import ascii, fits
from astropy.table import Table


def fits_convert(fits_path, ext):
    filename, file_ext = os.path.splitext(fits_path)
    fits_data = fits.open(fits_path)

    data = Table([fits_data[1].data['Time'], fits_data[1].data['Rate']], names=['TIME', 'RATE'])
    if ext == 'ascii':
        ascii.write(data, filename + '.ascii', delimiter='\t', overwrite=True)
    elif ext == 'csv':
        ascii.write(data, filename + '.csv', format='csv', overwrite=True)
    elif ext == 'hdf5':
        data.write(filename + '.hdf5', format='hdf5', overwrite=True)
    else:
        print('Error: Invalid file extension')
        print('Please use one of the following:')
        print('ascii, csv, hdf5')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python format_conversion.py <path to fits file> <format>')

    fits_convert(sys.argv[1], sys.argv[2])
