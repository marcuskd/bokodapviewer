'''SaveNetCDF function definition'''

from netCDF4 import Dataset
from datetime import datetime


def SaveNetCDF(data, dim_names, output_file_path):

    '''
    Function to save variables to a NetCDF4 file.
    '''

    dat = datetime.now()
    fname = output_file_path + '/' + 'bokodapviewer-' + str(dat.year) + '-' + \
        '{:02}'.format(dat.month) + '-' + \
        '{:02}'.format(dat.day) + '-' + '{:02}'.format(dat.hour) + '-' + \
        '{:02}'.format(dat.minute) + '-' + \
        '{:02}'.format(dat.second) + '.nc'

    try:
        root_grp = Dataset(fname, 'w', format='NETCDF4')
    except:
        msg = '<font color="red">Error: output file could not be opened</font>'
        return msg

    # Create dimensions and coordinate variables
    for dim in dim_names:
        dims = data[dim].size
        root_grp.createDimension(dim, dims)
        var = root_grp.createVariable(dim, data[dim].dtype,
                                      (dim), endian='native')
        var[:] = data[dim].copy()

    # Create data variable
    for var in data:
        if var not in dim_names:
            dims = data[var].size
            vari = root_grp.createVariable(var, data[var].dtype,
                                           tuple(dim_names), endian='native')
            vari[:] = data[var].copy()

    root_grp.close()

    msg = '<font color="green">Finished.</font>'
    return msg
