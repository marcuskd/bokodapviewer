from netCDF4 import Dataset
from datetime import datetime

def SaveNetCDF(data,dimNames,outputFilePath):

    '''
    Function to save variables to a NetCDF4 file.
    '''

    dt = datetime.now()
    fname = outputFilePath + '/' + 'bokodapviewer-' + str(dt.year) + '-' + '{:02}'.format(dt.month) + '-' + \
    '{:02}'.format(dt.day) + '-' + '{:02}'.format(dt.hour) + '-' + '{:02}'.format(dt.minute) + '-' + \
    '{:02}'.format(dt.second) + '.nc'

    try:
        rootGrp = Dataset(fname,'w',format='NETCDF4')
    except:
        msg = '<font color="red">Error: output file could not be opened</font>'
        return msg

    # Create dimensions and coordinate variables
    for d in dimNames:
        dims = data[d].size
        rootGrp.createDimension(d,dims)
        var = rootGrp.createVariable(d,data[d].dtype,(d),endian = 'native')
        var[:] = data[d].copy()

    # Create data variable
    for d in data:
        if d not in dimNames:
            dims = data[d].size
            var = rootGrp.createVariable(d,data[d].dtype,tuple(dimNames),endian = 'native')
            var[:] = data[d].copy()

    rootGrp.close()

    msg = '<font color="green">Finished.</font>'
    return msg
