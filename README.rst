bokodapviewer

-------------

A simple OpenDAP data viewer using Bokeh.
Run with the bokeh server at the command line: bokeh serve --show App.py

Display data with the following steps:
1. Enter an OpenDAP URL and press the 'Open URL' button. The DDS will be
loaded and displayed.
2. Select a variable (select a row in the DDS table) and press the
'Get variable details' button. The DAS and available dimensions will be
displayed.
3. Edit the data dimensions as required and press the 'Get plot options'
button.
4. Select the required plot option in the drop down and press the
'Get data' button. The data will be loaded and displayed under the
Data Visualisation tab.

When viewing the data the z axis limits can be fixed and all three axes
can be reversed using the controls below the plot. The 'Update Display'
button must be pressed to update the plot with the new settings.

The data can be saved to a NetCDF file using the 'Save to netCDF' button.
If no file path is specified the default one in the config file is used.
A time-stamped file name is assigned.

Attributes such as scale factors, offsets, missing and fill values are
automatically applied. The corresponding names are stored in the config
file. More than one can be stored, e.g. simply add a config line
<ScaleFactorName>new_scale_factor</ScaleFactorName> to add the scale factor
name new_scale_factor. More than one may be needed if different DAS have
different names for the same thing.

Other config file settings include the table and plot sizes and whether or
not a plot cursor readout is required. The app can cope with proxy servers:
create a simple text file with the proxy details (see the sodapclient
package for the structure) and include the file path in the config file.
