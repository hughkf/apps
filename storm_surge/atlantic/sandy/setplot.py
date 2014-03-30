
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
"""
import os

import numpy
# import matplotlib

import matplotlib.pyplot as plt
import datetime

from clawpack.visclaw import colormaps
import clawpack.clawutil.data
import clawpack.amrclaw.data
import clawpack.geoclaw.data

import clawpack.geoclaw.surge as surge

try:
    from setplotfg import setplotfg
except:
    setplotfg = None

days2seconds = lambda days: days * 60.0**2 * 24.0
date2seconds = lambda date: days2seconds(date.days) + date.seconds
seconds2days = lambda secs: secs / (24.0 * 60.0**2)
FT2METERS = 0.3048

def convert_time2seconds(time):
    new_year = datetime.datetime(2012,1,1,0,0)
    dt = time - new_year
    return days2seconds(dt.days)

def read_gauge_file(path):
    with open(path, 'r') as gauge_file:
        # Header
        gauge_file.readline()
        
        # Data format:
        # date, elevation MLLW (ft), astro tide MLLW (ft), obs. surge (ft) NYHOPS-predicted MLLW (ft), Predicted surge (ft)
        t = []
        eta = []
        for line in gauge_file:
            data = line.split(',')
            time = datetime.datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S")
            t.append(convert_time2seconds(time))
            eta.append([float(value) for value in data[1:]])

    t = numpy.array(t)
    eta = numpy.array(eta) * FT2METERS

    return t, eta


def setplot(plotdata):
    r"""Setplot function for surge plotting"""
    

    plotdata.clearfigures()  # clear any old figures,axes,items data

    fig_num_counter = surge.plot.figure_counter()

    # Load data from output
    clawdata = clawpack.clawutil.data.ClawInputData(2)
    clawdata.read('claw.data')
    physics = clawpack.geoclaw.data.GeoClawData()
    physics.read(os.path.join(plotdata.outdir,'geoclaw.data'))
    surge_data = surge.data.SurgeData()
    surge_data.read(os.path.join(plotdata.outdir,'surge.data'))
    friction_data = clawpack.geoclaw.surge.data.FrictionData()
    friction_data.read(os.path.join(plotdata.outdir,'friction.data'))

    # Load storm track
    track = surge.plot.track_data(os.path.join(plotdata.outdir,'fort.track'))

    # Calculate landfall time, off by a day, maybe leap year issue?
    landfall_dt = datetime.datetime(2012,10,29,8,0) - datetime.datetime(2012,1,1,0)
    landfall = (landfall_dt.days) * 24.0 * 60**2 + landfall_dt.seconds

    # Set afteraxes function
    surge_afteraxes = lambda cd: surge.plot.surge_afteraxes(cd, 
                                        track, landfall, plot_direction=False)
    # Limits for plots
    region_data = {'full':([clawdata.lower[0],clawdata.upper[0]],
                           [clawdata.lower[1],clawdata.upper[1]],
                           0.8),
                   'Region':([-74.5,-71.0], [40.0,41.5], 0.5),
                   'NYC':([-74.2,-73.8], [40.55,40.85], 0.5)
                  }

    # Color limits
    surface_range = 1.5
    speed_range = 1.0
    # speed_range = 1.e-2

    eta = physics.sea_level
    if not isinstance(eta,list):
        eta = [eta]
    surface_limits = [eta[0]-surface_range,eta[0]+surface_range]
    speed_limits = [0.0,speed_range]
    
    wind_limits = [0,55]
    pressure_limits = [966,1013]
    friction_bounds = [0.01,0.04]

    surface_ticks = [-5,-4,-3,-2,-1,0,1,2,3,4,5]
    surface_labels = [str(value) for value in surface_ticks]
    surface_contours = [-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]

    def pcolor_afteraxes(current_data):
        surge_afteraxes(current_data)
        surge.plot.gauge_locations(current_data)
    
    def contour_afteraxes(current_data):
        surge_afteraxes(current_data)

    def add_custom_colorbar_ticks_to_axes(axes, item_name, ticks, tick_labels=None):
        axes.plotitem_dict[item_name].colorbar_ticks = ticks
        axes.plotitem_dict[item_name].colorbar_tick_labels = tick_labels

    
    # ==========================================================================
    # ==========================================================================
    #   Plot specifications
    # ==========================================================================
    # ==========================================================================
    for (region, values) in region_data.iteritems():
        # ========================================================================
        #  Surface Elevations
        # ========================================================================
        plotfigure = plotdata.new_plotfigure(name='Surface - %s' % region,  
                                         figno=fig_num_counter.get_counter())
        plotfigure.show = True

        # Set up for axes in this figure:
        plotaxes = plotfigure.new_plotaxes()
        plotaxes.title = 'Surface'
        plotaxes.scaled = True
        plotaxes.xlimits = values[0]
        plotaxes.ylimits = values[1]
        plotaxes.afteraxes = pcolor_afteraxes
    
        surge.plot.add_surface_elevation(plotaxes,bounds=surface_limits,shrink=values[2])
        surge.plot.add_land(plotaxes)


        # ========================================================================
        #  Water Speed
        # ========================================================================
        plotfigure = plotdata.new_plotfigure(name='Currents - %s' % region,  
                                         figno=fig_num_counter.get_counter())
        plotfigure.show = True

        # Set up for axes in this figure:
        plotaxes = plotfigure.new_plotaxes()
        plotaxes.title = 'Currents'
        plotaxes.scaled = True
        plotaxes.xlimits = values[0]
        plotaxes.ylimits = values[1]
        plotaxes.afteraxes = pcolor_afteraxes

        # Speed
        surge.plot.add_speed(plotaxes,bounds=speed_limits,shrink=values[2])

        # Land
        surge.plot.add_land(plotaxes)


    # ========================================================================
    # Hurricane forcing - Entire Atlantic
    # ========================================================================
    # Friction field
    plotfigure = plotdata.new_plotfigure(name='Friction',
                                         figno=fig_num_counter.get_counter())
    plotfigure.show = friction_data.variable_friction and True

    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = region_data['full'][0]
    plotaxes.ylimits = region_data['full'][1]
    plotaxes.title = "Manning's N Coefficients"
    plotaxes.afteraxes = surge_afteraxes
    plotaxes.scaled = True

    surge.plot.add_friction(plotaxes,bounds=friction_bounds)

    # Pressure field
    plotfigure = plotdata.new_plotfigure(name='Pressure',  
                                         figno=fig_num_counter.get_counter())
    plotfigure.show = surge_data.pressure_forcing and True
    
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = region_data['full'][0]
    plotaxes.ylimits = region_data['full'][1]
    plotaxes.title = "Pressure Field"
    plotaxes.afteraxes = surge_afteraxes
    plotaxes.scaled = True
    
    surge.plot.add_pressure(plotaxes,bounds=pressure_limits)
    # add_pressure(plotaxes)
    surge.plot.add_land(plotaxes)
    
    # Wind field
    plotfigure = plotdata.new_plotfigure(name='Wind Speed', 
                                         figno=fig_num_counter.get_counter())
    plotfigure.show = surge_data.wind_forcing and True
    
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = region_data['full'][0]
    plotaxes.ylimits = region_data['full'][1]
    plotaxes.title = "Wind Field"
    plotaxes.afteraxes = surge_afteraxes
    plotaxes.scaled = True
    
    surge.plot.add_wind(plotaxes,bounds=wind_limits,plot_type='imshow')
    # add_wind(plotaxes,bounds=wind_limits,plot_type='contour')
    # add_wind(plotaxes,bounds=wind_limits,plot_type='quiver')
    surge.plot.add_land(plotaxes)

    # ==========================================================================
    #  Depth
    # ==========================================================================
    plotfigure = plotdata.new_plotfigure(name='Depth - Entire Domain', 
                                         figno=fig_num_counter.get_counter())
    plotfigure.show = False

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = 'Topography'
    plotaxes.scaled = True
    plotaxes.xlimits = region_data['full'][0]
    plotaxes.ylimits = region_data['full'][1]
    plotaxes.afteraxes = surge_afteraxes

    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = 0
    plotitem.imshow_cmin = 0
    plotitem.imshow_cmax = 200
    plotitem.imshow_cmap = plt.get_cmap("terrain")
    plotitem.add_colorbar = True
    plotitem.amr_celledges_show = [0,0,0]
    plotitem.amr_patchedges_show = [1,1,1,1,1,1,1,1,1]

    # ========================================================================
    #  Figures for gauges
    # ========================================================================
    stations = {4:["Kings Point", "kings_point_gauge.csv"], 
                3:["Battery Park", "battery_gauge.csv"]}
    # new_year = datetime.datetime(2012,1,1,0)
    sandy_landfall = datetime.datetime(2012,10,29,8,0) - datetime.datetime(2012,1,1,0)
    gauge_landfall = [sandy_landfall, 
                      sandy_landfall, 
                      sandy_landfall ]
    gauge_surface_offset = [0.0, 0.0]

    plotfigure = plotdata.new_plotfigure(name='Surface, Speeds',   
                                         figno=fig_num_counter.get_counter(),
                                         type='each_gauge')
    plotfigure.show = True
    plotfigure.clf_each_gauge = True

    def gauge_after_axes(cd):

        if cd.gaugeno in [3,4]:
            axes = plt.gca()
            axes.cla()

            # Add Davidson observations
            t, eta = read_gauge_file(stations[cd.gaugeno][1])
            # axes.plot(seconds2days(t), 
            import pdb; pdb.set_trace()
            axes.plot(t, eta[:,2], 'k-', label='Gauge Data')

            # Add GeoClaw gauge data
            # geoclaw_gauge = cd.gaugesoln
            # axes.plot(seconds2days(geoclaw_gauge.t),
            #       geoclaw_gauge.q[3,:] + gauge_surface_offset[0], 'b--', 
            #       label="GeoClaw")

            # Add Davidson predicted
            # axes.plot(seconds2days(t),
            axes.plot(t, eta[:,4], 'r-.', label="Stevens")

            # Fix up plot
            axes.set_title(stations[cd.gaugeno][0])
            axes.set_xlabel('Days relative to landfall')
            axes.set_ylabel('Surface (m)')
            # axes.set_xlim([-2,1])
            # axes.set_ylim([-1,5])
            # axes.set_xticks([-2,-1,0,1])
            # axes.set_xticklabels([r"$-2$",r"$-1$",r"$0$",r"$1$"])
            axes.grid(True)
            axes.legend()

            plt.hold(False)

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    # plotaxes.xlimits = [-2,1]
    # plotaxes.xlabel = "Days from landfall"
    # plotaxes.ylabel = "Surface (m)"
    # plotaxes.ylimits = [-1,5]
    plotaxes.title = 'Surface'
    plotaxes.afteraxes = gauge_after_axes

    # Plot surface as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'b-'

    # Gauge locations
    gauge_xlimits = [-74, -73]
    gauge_ylimits = [40.15, 40.95]
    gauge_location_shrink = 0.75
    def gauge_after_axes(cd):
        plt.subplots_adjust(left=0.12, bottom=0.06, right=0.97, top=0.97)
        surge_afteraxes(cd)
        surge.plot.gauge_locations(cd, gaugenos=[1, 2, 3, 4])
        plt.title("Gauge Locations")

    plotfigure = plotdata.new_plotfigure(name='Gauge Locations',  
                                         figno=fig_num_counter.get_counter())
    plotfigure.show = True

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = 'Surface'
    plotaxes.scaled = True
    plotaxes.xlimits = gauge_xlimits
    plotaxes.ylimits = gauge_ylimits
    plotaxes.afteraxes = gauge_after_axes
    
    surge.plot.add_surface_elevation(plotaxes, plot_type='contourf', 
                                               contours=surface_contours,
                                               shrink=gauge_location_shrink)
    # surge.plot.add_surface_elevation(plotaxes, plot_type="contourf")
    add_custom_colorbar_ticks_to_axes(plotaxes, 'surface', surface_ticks, surface_labels)
    surge.plot.add_land(plotaxes)
    # plotaxes.plotitem_dict['surface'].amr_patchedges_show = [0,0,0,0,0,0,0]
    # plotaxes.plotitem_dict['surface'].add_colorbar = False
    # plotaxes.plotitem_dict['surface'].pcolor_cmap = plt.get_cmap('jet')
    # plotaxes.plotitem_dict['surface'].pcolor_cmap = plt.get_cmap('gist_yarg')
    # plotaxes.plotitem_dict['surface'].pcolor_cmin = 0.0
    # plotaxes.plotitem_dict['surface'].pcolor_cmax = 5.0
    plotaxes.plotitem_dict['surface'].amr_patchedges_show = [0,0,0,0,0,0,0]
    plotaxes.plotitem_dict['land'].amr_patchedges_show = [0,0,0,0,0,0,0]



    #-----------------------------------------
    
    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via pyclaw.plotters.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_gaugenos = 'all'          # list of gauges to print
    plotdata.print_fignos = 'all'            # list of figures to print
    plotdata.html = True                     # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.latex = True                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?

    return plotdata

