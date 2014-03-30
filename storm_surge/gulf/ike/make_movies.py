#!/usr/bin/env python

import subprocess

delay = 15
frame_template = "frame*fig"
figures = {"gulf_surface":1,
           "gulf_currents":2,
           "latex_surface":4,
           "latex_currents":5,
           "galveston_surface":6,
           "galveston_currents":7,
           "pressure":8,
           "winds":9}

frames_per_second = 8
# command = r"ffmpeg -qscale 0 -r 1 -i _plots/frame%04dfig" + fig_num + r".png -r 24 " + fig_name +".mpg"

for (fig_name,fig_num) in figures.iteritems():
    # command = "convert -delay %s _plots/%s%s.png %s.gif"  \
                                    # % (delay, frame_template, fig_num, fig_name)
    command = "".join((r"ffmpeg -y -q:v 1 -r ", str(frames_per_second), 
                       r" -i _plots/frame%04dfig", str(fig_num), 
                       r".png -r 24 ", 
                       r"-vcodec mpeg4 -vb 20M",
                       r" ", fig_name, ".mp4"))
    print command
    process = subprocess.Popen(command, shell=True)
    process.wait()
