bokodapviewer

-------------

A simple OpenDAP data viewer using Bokeh.
Run with the bokeh server at the command line: bokeh serve --show App.py

Display data with the following steps:

1. Enter an OpenDAP URL and press the 'Open URL' button. The DDS will be loaded and displayed.
2. Select a variable (i.e. select a row in the DDS table) and press the 'Get variable details' button. The DAS and available dimensions will be displayed.
3. Edit the data dimensions (if required) and press the 'Get plot options' button.
4. Select the required plot option in the drop down and enter an interpolation interval if required (see below).
5. Press the 'Get data' button. The data will be loaded and displayed under the Data Visualisation tab.

NB: In order to avoid errors, all steps must be followed in order, i.e.:

- After opening a new URL, repeat all of steps 2-5 in order.
- After the selected variable is changed, repeat all of steps 3-5 in order.
- After selecting new dimensions, press the 'Get plot options' button and repeat step 4 then step 5.

For 2D images both axes must be on a uniform grid so interpolation will be
done if one of them is not. If a value is entered into the
Interpolation Interval box it will be used; otherwise the minimum interval
in the relevant axis grid will be used (this may be slow). For a 2D plot
with a slider (i.e. 3D volume slices), the slider axis can be non-uniform;
only the axes for the image itself must be uniform. A non-uniformity
tolerance percentage can be set: this allows for slight non-uniformity
in an axis grid (e.g. precision errors) without invoking interpolation.

When viewing the data the z axis limits can be fixed and all three axes
can be reversed using the controls below the plot. The 'Update Display'
button must be pressed to update the plot with the new settings.

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
