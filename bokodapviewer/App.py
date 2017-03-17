import numpy

import xml.etree.ElementTree as et

from bokodapviewer import SaveNetCDF

from sodapclient import Handler

from bokcolmaps import ColourMap
from bokcolmaps import ColourMapLPSlider

from bokeh.models.widgets.tables import DataTable, TableColumn, IntEditor
from bokeh.models.widgets.markups import Paragraph, Div
from bokeh.models.widgets.panels import Panel, Tabs
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets.inputs import TextInput, Select
from bokeh.models.widgets import CheckboxGroup
from bokeh.models.layouts import WidgetBox, Row, Column
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import Figure
from bokeh.io import curdoc

from collections import OrderedDict
from numpy import float32

import os

class App():

    '''
    A simple OpenDAP data viewer using Bokeh. Run with the bokeh server at the command line:
    bokeh serve --show App.py

    Enter an OpenDAP URL and press the 'Open URL' button. The DDS will be loaded and displayed.
    Select a variable (select a row in the DDS table) and press the 'Get variable details' button.
    The DAS and available dimensions will be displayed. Edit the data dimensions as required and
    press the 'Get plot options' button. Select the required plot option in the drop down and
    press the 'Get data' button. The data will be loaded and displayed under the Data Visualisation
    tab.
    
    When viewing the data the z axis limits can be fixed and all three axes can be reversed using
    the controls below the plot. The 'Update Display' button must be pressed to update the plot with
    the new settings.
    
    The data can be saved to a NetCDF file using the 'Save to netCDF' button. If no file path is
    specified the default one in the config file is used. A time-stamped file name is assigned.

    Attributes such as scale factors, offsets, missing and fill values are automatically applied.
    The corresponding names are stored in the config file. More than one can be stored, e.g. simply
    add a config line <ScaleFactorName>new_scale_factor</ScaleFactorName> to add the scale factor
    name new_scale_factor. More than one may be needed if different DAS have different names for
    the same thing.

    Other config file settings include the table and plot sizes and whether or not a plot cursor
    readout is required. The app can cope with proxy servers - create a simple text file with
    the proxy details (see the sodapclient package for the structure) and include the file path
    in the config file.
    '''

    def __init__(self):

        self.configFile = 'Config.xml'

        # Plot sizes

        self.mainPlotSize = [None,None]
        self.linePlotSize = [None,None]

        # Dictionary of attribute names for scale factors etc.
        self.AttrNames = {'ScaleFactorName':[],'OffsetName':[],'FillValueName':[],'MissingValueName':[]}

        # Read the configuration file to get data sources etc
        self.GetConfig()

        # Set up the GUI
        self.SetUpGUI()

    def GetConfig(self):

        root = et.parse(self.configFile).getroot()

        for child in root:

            if child.tag == 'ProxyFileName': proxyFileName = child.text
            if proxyFileName == 'None': proxyFileName = None

            if child.tag == 'OutputFilePath': self.outputFilePath = child.text

            if child.tag == 'ColourMapPath': self.colMapPath = child.text

            if child.tag == 'TableSize':
                self.tableSize = [int(child.attrib['height']),int(child.attrib['width'])]
            if child.tag == 'MainPlotSize':
                self.mainPlotSize = [int(child.attrib['height']),int(child.attrib['width'])]
            if child.tag == 'LinePlotSize':
                self.linePlotSize = [int(child.attrib['height']),int(child.attrib['width'])]

            if child.tag in self.AttrNames.keys():
                if child.text not in self.AttrNames[child.tag]:
                    self.AttrNames[child.tag].append(child.text)

            if child.tag == 'CursorReadout2D':
                if child.text == 'Off': self.hoverdisp2D = False
                else: self.hoverdisp2D = True

            if child.tag == 'CursorReadout3D':
                if child.text == 'Off': self.hoverdisp3D = False
                else: self.hoverdisp3D = True

    def SetUpGUI(self):

        self.URL = TextInput(title = 'OpenDAP URL:')
        self.openBtn = Button(label = 'Open URL',button_type = 'primary')
        self.openBtn.on_click(self.OpenURL)

        # Set up the data and plot selection tables (initially blank)

        # DDS table

        od = OrderedDict()
        od['Variable Name'] = []
        od['Type'] = []
        od['Dimensions'] = []
        od['Dimension Names'] = []
        self.dsDDS = ColumnDataSource(od)

        cols = []
        for v in iter(od):
            cols.append(TableColumn(title = v,field = v))
        tDDS = DataTable(source = self.dsDDS, columns = cols, selectable = True, sortable = False,
                         height = self.tableSize[0], width = self.tableSize[1])

        # DAS table

        od = OrderedDict()
        od['Attribute Name'] = []
        od['Type'] = []
        od['Value'] = []
        self.dsDAS = ColumnDataSource(od)

        cols = []
        for v in iter(od):
            cols.append(TableColumn(title = v,field = v))
        tDAS = DataTable(source = self.dsDAS, columns = cols, selectable = False, sortable = False,
                         height = self.tableSize[0], width = self.tableSize[1])

        # Selection table

        od = OrderedDict()
        od['Dimension'] = []
        od['First Index'] = []
        od['Interval'] = []
        od['Last Index'] = []
        self.dsSel = ColumnDataSource(od)

        cols = []
        for v in iter(od):
            if v == 'Dimension':
                cols.append(TableColumn(title = v,field = v))
            else:
                cols.append(TableColumn(title = v,field = v,editor = IntEditor(step=1)))
        tSel = DataTable(source = self.dsSel,columns = cols,selectable = True,sortable = True,editable=True,
                         height = self.tableSize[0], width = self.tableSize[1])

        # Selection and Visualisation panels

        self.getVarBtn = Button(label = 'Get variable details',disabled = True)
        self.getVarBtn.on_click(self.GetVar)

        self.pSel = Paragraph(text='No variable selected.')
        
        self.getPlotsBtn = Button(label = 'Get plot options',disabled = True)
        self.getPlotsBtn.on_click(self.GetPlots)

        self.plotOpts = Select(options = [])

        self.getDataBtn = Button(label = 'Get data',button_type = 'primary',disabled = True)
        self.getDataBtn.on_click(self.GetData)
        
        self.endianCheckBox = CheckboxGroup(labels = ['Big Endian'], active = [0])

        self.revXCheckBox = CheckboxGroup(labels = ['Reverse x axis'], active = [])
        self.revYCheckBox = CheckboxGroup(labels = ['Reverse y axis'], active = [])
        self.revZCheckBox = CheckboxGroup(labels = ['Reverse z axis'], active = [])

        self.zMin = TextInput(title = 'z minimum:')
        self.zMax = TextInput(title = 'z maximum:')

        self.saveBtn = Button(label = 'Save to NetCDF',disabled = True)
        self.saveBtn.on_click(self.Save)

        self.statBox = Div(text = '<font color="green">Initialised OK</font>',width = 800)

        self.updateBtn = Button(label = 'Update Display')
        self.updateBtn.on_click(self.DisplayData)

        ws1 = Row(children=[Column(Div(text = '<font color="blue">Dataset Descriptor Structure'),
                                   tDDS),Div(),Column(self.getVarBtn,self.pSel)])
        ws2 = Row(children=[Column(Div(text = '<font color="blue">Dataset Attribute Structure'),
                                   tDAS),Div(),
                                   Column(Div(text = '<font color="blue">Dimensions'),tSel)])
        ws3 = Row(children=[self.getPlotsBtn,self.getDataBtn,self.endianCheckBox])
        ws4 = Row(children=[self.plotOpts])
        wp1 = Row(children=[self.zMin,self.zMax])
        wp2 = Row(children=[self.revXCheckBox,self.revYCheckBox,self.revZCheckBox])
        wp3 = Row(children=[self.updateBtn])
        wp4 = Row(self.saveBtn)

        selPanel = Panel(title = 'Data Selection',child = Column(ws1,ws2,ws3,ws4))

        plotPanel = Panel(title = 'Data Visualisation',
                          child = Column(Figure(toolbar_location = None),
                                         wp1,wp2,wp3,WidgetBox(Div(text = '<hr>',width = 1320)),wp4))

        self.Tabs = Tabs(tabs = [selPanel, plotPanel])

        self.GUI = Column(children = [WidgetBox(self.URL,width = 1450),
                                      WidgetBox(self.openBtn),
                                      WidgetBox(self.statBox),
                                      WidgetBox(Div(text = '<hr>',width = 1320)),
                                      self.Tabs])

    def OpenURL(self):

        self.statBox.text = '<font color="blue">Opening URL...</font>'

        try:
            self.odh = Handler(self.URL.value)
        except:
            self.statBox.text = '<font color="red">Error: could not open URL</font>'
            return

        if self.odh.DDS is None:
            self.statBox.text = '<font color="red">Error: no DDS found at URL</font>'
            return

        varNames,varTypes,varDims,dimNames = [],[],[],[]
        for v,a in sorted(self.odh.DDS.items()):
            varNames.append(v)
            varTypes.append(a[0])
            varDims.append(a[1])
            dimNames.append(a[2])
        self.dsDDS.data['Variable Name'] = varNames
        self.dsDDS.data['Type'] = varTypes
        self.dsDDS.data['Dimensions'] = varDims
        self.dsDDS.data['Dimension Names'] = dimNames

        self.getVarBtn.disabled = False
        self.getPlotsBtn.disabled = True # Disable these to avoid mismatch between DDS and stored data
        self.getDataBtn.disabled = True

        self.statBox.text = '<font color="green">URL opened OK.</font>'

        self.Tabs.active = 0

    def GetVar(self):

        sel = self.dsDDS.selected['1d']['indices']

        if len(sel) > 0:

            # Attributes

            self.varName = self.dsDDS.data['Variable Name'][sel[0]]
            das = self.odh.DAS[self.varName]
            aName,aType,aVal = [],[],[]
            for a in das:
                atrs = a.split()
                aName.append(atrs[1])
                aType.append(atrs[0])
                aVal.append(atrs[2])
            self.dsDAS.data['Attribute Name'] = aName
            self.dsDAS.data['Type'] = aType
            self.dsDAS.data['Value'] = aVal

            # Selection

            dvals = self.odh.DDS[self.varName][1]
            dMax = []
            for d in range(len(dvals)):
                dMax.append(dvals[d] - 1)
            dName = self.odh.DDS[self.varName][2]
            self.dsSel.data['Dimension'] = dName
            self.dsSel.data['First Index'] = [0]*len(dvals)
            self.dsSel.data['Interval'] = [1]*len(dvals)
            self.dsSel.data['Last Index'] = dMax

            self.pSel.text = 'Variable: ' + self.varName

            self.getPlotsBtn.disabled = False
            self.getDataBtn.disabled = True # Disable to avoid mismatch

            self.statBox.text = '<font color="green">Variable selected.</font>'

    def GetPlots(self):

        '''
        Get all the available plot options corresponding to the selected data dimensions.
        '''

        sel = self.dsDDS.selected['1d']['indices'][0]

        opts = []
        optDims = []
        nDims = len(self.dsSel.data['Dimension'])
        if nDims == 1:
            if self.dsDDS.data['Dimensions'][sel][0] > 1:
                opts.append(self.varName + ' against index (line plot)')
                optDims.append([0])
                nA = 1
            else:
                opts.append('None (single value)')
                nA = 0
        else:
            aDims = [False]*nDims
            nA = 0
            for d in range(nDims):
                rMin = self.dsSel.data['First Index'][d]
                rInt = self.dsSel.data['Interval'][d]
                rMax = self.dsSel.data['Last Index'][d] + 1
                if (rMax > rMin):
                    l = list(range(rMin,rMax,rInt))
                    if len(l) > 1:
                        aDims[d] = True
                        nA += 1
            if nA > 0:
                if (nA == 1):
                    a = aDims.index(True)
                    opts.append(self.varName + ' against ' + self.dsSel.data['Dimension'][a] + ' (line plot)')
                    optDims = [a]
                elif (nA == 2):
                    for a in range(nDims):
                        if aDims[a]:
                            for b in range(nDims):
                                if aDims[b] and (b != a):
                                    opts.append(self.varName + ' against ' + \
                                                self.dsSel.data['Dimension'][a] + ' and ' + \
                                                self.dsSel.data['Dimension'][b] + ' (colour map)')
                                    optDims.append([b,a])
                elif (nA == 3):
                    for a in range(nDims):
                        if aDims[a]: # a will be slider dimension
                            for b in range(nDims):
                                if aDims[b] and (b != a):
                                    for c in range(nDims):
                                        if aDims[c] and (c != b) and (c != a):
                                            optDims.append([a,c,b])
                                            opts.append(self.varName + ' against ' + \
                                                        self.dsSel.data['Dimension'][b] + ' and ' + \
                                                        self.dsSel.data['Dimension'][c] + ' with ' + \
                                                        self.dsSel.data['Dimension'][a] + ' as variable ' + \
                                                        '(colour map with slider)')
                else:
                    opts.append('None (maximum 3 dimensions - please reduce others to singletons)')
            else:
                opts.append('None (single value)')

        self.plotOpts.options = opts
        self.plotOpts.value = opts[0]
        self.optDims = optDims

        if nA > 0:
            self.getDataBtn.disabled = False

        self.statBox.text = '<font color="green">Plot options found.</font>'

    def GetData(self):

        self.statBox.text = '<font color="blue">Getting data...</font>'

        self.data = {} # Clear the data dictionary
        self.dimNames = [] # Clear the dimension names list

        if len(self.endianCheckBox.active) > 0:
            byteOrdStr = '>'
        else:
            byteOrdStr = '<'

        ndims = len(self.odh.DDS[self.varName][2])

        if ndims == 1: # Dimension variable

            dimS = numpy.ndarray(shape=(1,3),dtype=numpy.dtype('int'))
            dimS[0,0] = self.dsSel.data['First Index'][0]
            dimS[0,1] = self.dsSel.data['Interval'][0]
            dimS[0,2] = self.dsSel.data['Last Index'][0]
            self.odh.GetVariable(self.varName,dimS,byteOrdStr)
            self.data[self.varName] = numpy.ndarray(shape = self.odh.variables[self.varName].shape,dtype = numpy.dtype('float32'))
            self.data[self.varName][:] = self.odh.variables[self.varName][:]
            self.ApplyAttributes(self.varName) # Apply any attributes
            self.dimNames.append(self.varName)

        else: # Data variable

            dimS = numpy.ndarray(shape=(ndims,3),dtype=numpy.dtype('int'))

            for n in range(ndims):
                dimS[n,0] = self.dsSel.data['First Index'][n]
                dimS[n,1] = self.dsSel.data['Interval'][n]
                dimS[n,2] = self.dsSel.data['Last Index'][n]

            # Get the variable

            self.odh.GetVariable(self.varName,dimS,byteOrdStr)
            self.data[self.varName] = numpy.ndarray(shape = self.odh.variables[self.varName].shape,dtype = float32)
            self.data[self.varName][:] = self.odh.variables[self.varName][:]
            self.ApplyAttributes(self.varName) # Apply any attributes

            # Get the map variables over the ranges required

            dimSd = numpy.ndarray(shape=(1,3),dtype=numpy.dtype('int'))
            for n in range(ndims):
                dimSd[:] = dimS[n]
                dimName = self.odh.DDS[self.varName][2][n]
                self.odh.GetVariable(dimName,dimSd,byteOrdStr)
                self.data[dimName] = numpy.ndarray(shape = self.odh.variables[dimName].shape,dtype = float32)
                self.data[dimName][:] = self.odh.variables[dimName][:]
                self.ApplyAttributes(dimName) # Apply any attributes
                self.dimNames.append(dimName)

        ind = self.plotOpts.options.index(self.plotOpts.value)
        self.plotDims = self.optDims[ind]

        self.statBox.text = '<font color="green">Data downloaded.</font>'

        self.saveBtn.disabled = False

        self.DisplayData()

    def ApplyAttributes(self,varName):

        attrList = self.odh.DAS[varName]

        scaleFactor = numpy.nan
        offset = numpy.nan
        fillValue = numpy.nan
        missingValue = numpy.nan
        for a in attrList:
            aname = a.split()[1]
            aval = a.split()[2]
            if aname in self.AttrNames['ScaleFactorName']: scaleFactor = float(aval)
            if aname in self.AttrNames['OffsetName']: offset = float(aval)
            if aname in self.AttrNames['FillValueName']: fillValue = float(aval)
            if aname in self.AttrNames['MissingValueName']: missingValue = float(aval)

        d = self.data[varName]
        if not numpy.isnan(fillValue): d[d == fillValue] = numpy.nan
        if not numpy.isnan(missingValue): d[d == missingValue] = numpy.nan
        if not numpy.isnan(scaleFactor): d *= scaleFactor
        if not numpy.isnan(offset): d += offset

    def DisplayData(self):

        self.statBox.text = '<font color="blue">Displaying data...</font>'

        revX = revY = revZ = False
        if len(self.revXCheckBox.active) > 0: revX = True
        if len(self.revYCheckBox.active) > 0: revY = True
        if len(self.revZCheckBox.active) > 0: revZ = True

        # Find plot type

        if len(self.plotDims) == 1: # Line plot

            disp = Figure(x_axis_label = 'Index',y_axis_label = self.varName,
                           plot_height = self.linePlotSize[0],plot_width = self.linePlotSize[0],
                           tools=["reset,pan,resize,wheel_zoom,box_zoom,save"])

            disp.line(x = numpy.linspace(0,self.data[self.varName].size-1,self.data[self.varName].size),
                      y = self.data[self.varName],line_color='blue',line_width=2,line_alpha=1)
        
            disp.toolbar_location = 'above'

            disp.title_text_font = disp.xaxis.axis_label_text_font = disp.yaxis.axis_label_text_font = 'garamond'
            disp.xaxis.axis_label_text_font_size = disp.yaxis.axis_label_text_font_size = '10pt'
            disp.title_text_font_style = disp.xaxis.axis_label_text_font_style = disp.yaxis.axis_label_text_font_style = 'bold'
            disp.title_text_font_size = '8pt'
            disp.x_range.start = 0
            disp.x_range.end = self.data[self.varName].size - 1
            disp.y_range.start = self.data[self.varName][0]
            disp.y_range.end = self.data[self.varName][-1]
            if revX:
                disp.x_range.start,disp.x_range.end = disp.x_range.end,disp.x_range.start
            if revY:
                disp.y_range.start,disp.y_range.end = disp.y_range.end,disp.y_range.start

        else: # Colourmaps

            if len(self.plotDims) == 2:
                xName = self.dsSel.data['Dimension'][self.plotDims[1]]
                yName = self.dsSel.data['Dimension'][self.plotDims[0]]
            else:
                xName = self.dsSel.data['Dimension'][self.plotDims[2]]
                yName = self.dsSel.data['Dimension'][self.plotDims[1]]
                zName = self.dsSel.data['Dimension'][self.plotDims[0]]

            allDims = self.data[self.varName].shape
            tDims = [0]*len(allDims)
            pdCount = 0
            for n in range(len(tDims)):
                if allDims[n] == 1:
                    tDims[n] = n
                else:
                    tDims[n] = self.plotDims[pdCount]
                    pdCount += 1

            dataT = self.data[self.varName].copy().transpose(tDims)
            dataT = numpy.squeeze(dataT)

            xT = self.data[xName].copy()
            yT = self.data[yName].copy()
            if revX: xT = numpy.flipud(xT)
            if revY: yT = numpy.flipud(yT)

            if revX or revY:
                if len(self.plotDims) == 2:
                    if revX: dataT = numpy.fliplr(dataT)
                    if revY: dataT = numpy.flipud(dataT)
                else:
                    for n in range(dataT.shape[0]):
                        if revX: dataT[n] = numpy.fliplr(dataT[n])
                        if revY: dataT[n] = numpy.flipud(dataT[n])

            rminT,rmaxT = self.zMin.value,self.zMax.value
            rminV = rmaxV = None
            try:
                rminV = float(rminT)
            except ValueError:
                self.zMin.value = ''
            if rminV is not None:
                try:
                    rmaxV = float(rmaxT)
                except ValueError:
                    self.zMax.value = ''
                if rmaxV is not None:
                    if rmaxV == rminV: rmaxV += 0.1
                    if rmaxV < rminV: rminV,rmaxV = rmaxV,rminV

            cFile = self.colMapPath + '/jet.txt'
            if not os.path.exists(cFile):
                cFile = None
                print('App warning: colourmap file could not be found: reverting to default palette.')

            if len(self.plotDims) == 2: # Colourmap

                disp = ColourMap(xT,yT,numpy.array([0]),dataT,
                                 xlab = xName,ylab = yName,Dlab = self.varName,cfile = cFile,
                                 height = self.mainPlotSize[0],width = self.mainPlotSize[1],
                                 rMin = rminV,rMax = rmaxV,hover = self.hoverdisp2D)

            else: # Colourmap with slider

                disp = ColourMapLPSlider(xT,yT,self.data[zName],dataT,
                                         xlab = xName,ylab = yName,zlab = zName,Dlab = self.varName,cfile = cFile,
                                         cmheight = self.mainPlotSize[0],cmwidth = self.mainPlotSize[1],
                                         lpheight = self.linePlotSize[0],lpwidth = self.linePlotSize[1],
                                         revz = revZ,rMin = rminV,rMax = rmaxV,hoverdisp = self.hoverdisp3D)

        self.Tabs.tabs[1].child.children[0] = disp
        self.Tabs.active = 1

        self.statBox.text = '<font color="green">Finished.</font>'

    def Save(self):

        self.statBox.text = '<font color="blue">Saving netCDF file...</font>'
        msg = SaveNetCDF(self.data,self.dimNames,self.outputFilePath)
        self.statBox.text = msg

curdoc().add_root(App().GUI)
curdoc().title = 'bokodapviewer'
