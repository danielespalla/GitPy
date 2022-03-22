# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 08:56:55 2022

@author: daniele
"""
import sys

import numpy as np
import pandas as pd
from plotnine import aes, ggplot, geom_line, coord_cartesian, ggtitle, \
    scale_color_manual
from plotnine import theme_bw, xlab, ylab, annotation_logticks, \
    scale_x_log10


class EvtGit:
    def __init__(self, f):
        results = isinstance(f, str)
        resultl = isinstance(f, list)
        # result = isinstance(f,FAS)
        if results:
            self.name = f
            self.nsamp = 0
            fr = list()
            amp = list()
            filename = f
            try:
                f = open(filename, "r")
            except FileNotFoundError:
                print(f"File {filename} not found.  Aborting")
                sys.exit(1)
            except OSError:
                print(f"OS error occurred trying to open {filename}")
                sys.exit(1)
            except Exception as err:
                print(f"Unexpected error opening {filename} is", repr(err))
                sys.exit(1)
            line = f.readline()
            p1 = line.split()
            self.programName = p1[0]
            self.cmp = p1[1]
            self.Id0 = p1[2]
            self.Ml = float(p1[3])
            self.Lat = float(p1[4])
            self.Lon = float(p1[6])
            self.Dpt = float(p1[6])
            Lines = f.readlines()
            ncount = 0
            for line1 in Lines:
                ncount += 1
                if ncount > 1:
                    line1 = line1.rstrip()
                    p1 = line1.split()
                    fr.append(float(p1[0]))
                    amp.append(float(p1[1]))
            self.freq = np.asarray(fr)
            self.val = np.asarray(amp)
            self.nfreq = len(self.freq)
            f.close()
            del fr
            del amp
        elif resultl == True:
            self.Id0 = f[0]
            self.Ml = float(f[1])
            self.Lat = float(f[2])
            self.Lon = float(f[3])
            self.Dpt = float(f[4])
            self.cmp = f[5]
            self.nsamp = 0
            self.name = ""
            self.nfreq = 0
        else:
            self.Id0 = f.Id0
            self.Ml = f.Ml
            self.Lat = f.Lat
            self.Lon = f.Lon
            self.Dpt = f.Dpt
            self.nsamp = 0
            self.name = ""
            self.nfreq = 0

    def set_val(self, nf):
        self.nfreq = nf
        self.val = np.empty(self.nfreq)
        self.val[:] = np.NaN

    def toString(self, name: object, cm: object) -> object:
        if name:
            s1 = "{:s} {:s} {:12s} {:5.2f} {:8.3f} {:8.3f} {:8.2f}".format(name, cm, self.Id0, self.Ml, self.Lat,
                                                                           self.Lon, self.Dpt)
        else:
            s1 = "{:12s} {:5.2f} {:8.3f} {:8.3f} {:8.2f}".format(self.Id0, self.Ml, self.Lat, self.Lon, self.Dpt)
        return s1

    def plotSource(self, name_out, v1, v2):
        f1 = np.asarray(self.freq)
        s1 = "Inv: {:s}, Cmp: {:s} Id: {:s}, Ml: {:5.1f}".format(self.programName, self.cmp,self.Id0,self.Ml)
        d1 = {'x': f1, 'y': self.val}
        d1 = pd.DataFrame(d1)
        d1 = d1.reset_index()
        if v1 != False or v2 != False:
            g = ggplot(d1, aes(x='x', y='y')) + geom_line(size=0.6,color='dodgerblue')
            g = g + scale_x_log10(breaks=[0.3, 1.0, 3.0, 10.0, 30.0])
            g = g + annotation_logticks(sides="b")
            g = g + xlab("Frequency [Hz]") + ylab("Log(Source)")
            g = g + ggtitle(s1)
            g = g + theme_bw()
            if v1:
                print(g)
            if v2:
                if name_out:
                    g.save(filename=name_out, dpi=300)
