#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 09:02:18 2022

@author: daniele
"""
import os
import sys

import numpy as np
import pandas as pd
from plotnine import aes, ggplot, geom_line, coord_cartesian, ggtitle, \
    scale_color_manual
from plotnine import theme_bw, xlab, ylab, annotation_logticks, \
    scale_x_log10


class StatGit:
    def __init__(self, f, cm):
        results = isinstance(f, str)
        resultl = isinstance(f, list)
        if results == True:
            self.name = f
            self.nsamp = 0
            fr = list()
            amp = list()
            fname = f
            try:
                f = open(fname, "r")
            except FileNotFoundError:
                print(f"File {fname} not found.  Aborting")
                sys.exit(1)
            except OSError:
                print(f"OS error occurred trying to open {fname}")
                sys.exit(1)
            except Exception as err:
                print(f"Unexpected error opening {fname} is", repr(err))
                sys.exit(1)
            line = f.readline()
            p1 = line.split()
            self.programName = p1[0]
            self.Stat = p1[1]
            self.CMP = p1[2]
            self.Net = p1[3]
            self.cmp = p1[4]
            self.StLat = float(p1[5])
            self.StLon = float(p1[6])
            self.StElev = float(p1[7])
            ref = p1[8]
            if ref != 'True':
                self.ref = False
            else:
                self.ref = True
            Lines = f.readlines()
            ncount = 0
            for line1 in Lines:
                ncount += 1
                if ncount >= 1:
                    line1 = line1.rstrip()
                    p1 = line1.split()
                    fr.append(float(p1[0]))
                    amp.append(float(p1[1]))
            #    print(ncount)
            self.freq = np.asarray(fr)
            self.val = np.asarray(amp)
            self.nfreq = len(self.freq)
            f.close()
            del fr
            del amp
        elif resultl == True:
            self.Stat = f[0]
            self.CMP = f[1]
            self.Net = f[2]
            self.StLat = float(f[3])
            self.StLon = float(f[4])
            self.StElev = float(f[5])
            self.nsamp = 0
            self.nfreq = 0
            self.cmp = cm
            self.ref = False
            self.name = ""
        else:
            self.Stat = f.Stat
            self.Net = f.Net
            self.StLat = f.StLat
            self.StLon = f.StLon
            self.StElev = f.StElev
            self.nsamp = 0
            self.nfreq = 0
            self.cmp = cm
            self.CMP = f.CMP
            self.ref = False
            self.name = ""

    def set_val(self, nf):
        self.nfreq = nf
        self.val = np.empty(self.nfreq)
        self.val[:] = np.NaN

    def toString(self, name: object) -> object:
        if name:
            s1 = "{:s} {:6s} {:2s} {:2s} {:1s} {:8.3f} {:8.3f} {:7.3f}  {:s}".format(name, self.Stat, self.CMP,
                                                                                     self.Net, self.cmp, self.StLat,
                                                                                     self.StLon, self.StElev,
                                                                                     str(self.ref))
        else:
            s1 = "{:6s} {:2s} {:2s} {:1s} {:8.3f} {:8.3f} {:7.3f}  {:s}".format(self.Stat, self.CMP, self.Net, self.cmp,
                                                                                self.StLat, self.StLon, self.StElev,
                                                                                str(self.ref))
        return s1

    def toString0(self, name: object) -> object:
        if name:
            s1 = "{:s} {:6s}  {:2s} {:2s}  {:8.3f} {:8.3f} {:7.3f}  {:s}".format(name, self.Stat, self.CMP, self.Net,
                                                                                 self.StLat, self.StLon, self.StElev,
                                                                                 str(self.ref))
        else:
            s1 = "{:6s}  {:2s} {:2s}  {:8.3f} {:8.3f} {:7.3f}  {:s}".format(self.Stat, self.CMP, self.Net, self.StLat,
                                                                            self.StLon, self.StElev, str(self.ref))
        return s1

    def WriteStation(self, freq, dirname, progname):
        nm = self.cmp + "_" + self.Net + "." + self.Stat + "." + self.CMP
        nm = nm + ".site"
        name = os.path.join(dirname, nm)
        try:
            sta = open(name, "w")
        except FileNotFoundError:
            print(f"Cannot open file: {name}.  Aborting")
            sys.exit(1)
        except OSError:
            print(f"OS error occurred trying to open {name}")
            sys.exit(1)
        except Exception as err:
            print(f"Unexpected error opening {name} is", repr(err))
            sys.exit(1)
        s1 = self.toString(progname)
        sta.write(s1)
        sta.write("\n")
        for j in range(self.nfreq):
            s1 = "  {:7.2f} {:7.3f}".format(freq[j], self.val[j])
            sta.write(s1)
            sta.write("\n")
        sta.close()

    def plotStation(self, name_out, v1, v2):
        nm = self.Net + "." + self.Stat + "." + self.CMP
        f1 = np.asarray(self.freq)
        if self.ref == True:
            st = "Inv: {:s}, {:s}, Cmp: {:s},  Ref: True ".format(self.programName, nm, self.cmp)
            s1 = ["RefS" for i in range(self.nfreq)]
        else:
            st = "Inv: {:s}, {:s}, Cmp: {:s},  Ref: False".format(self.programName, nm, self.cmp)
            s1 = ["No RefS" for i in range(self.nfreq)]
        y1 = np.asarray(self.val)
        d1 = {'x': f1, 'y': y1, 'Site': s1}
        d1 = pd.DataFrame(d1)
        d1 = d1.reset_index()
        if v1 != False or v2 != False:
            g = ggplot()
            if self.ref == True:
                g = g + geom_line(d1, aes(x='x', y='y', colour='Site'), size=1.3, alpha=.9)
                g = g + scale_color_manual(values=['dodgerblue'])
            else:
                g = g + geom_line(d1, aes(x='x', y='y', colour='Site'), size=.7, alpha=.9)
                g = g + scale_color_manual(values=['darkgray'])
            g = g + scale_x_log10(breaks=[0.3, 1.0, 3.0, 10.0, 30.0])
            g = g + annotation_logticks(sides="b")
            g = g + coord_cartesian(ylim=[0.0, 8])
            g = g + xlab("Frequency [Hz]") + ylab("Amplitude")
            g = g + ggtitle(st)
            g = g + theme_bw()
            print(g)
            if v2:
                if name_out:
                    g.save(filename=name_out, dpi=300)
