#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 16:54:26 2022

@author: daniele
"""

import glob
import os

import numpy as np
import pandas as pd
from plotnine import aes, ggplot, geom_line, coord_cartesian, ggtitle
from plotnine import scale_color_manual, scale_x_log10
from plotnine import theme_bw, xlab, ylab, annotation_logticks

from LibGit import StatGit


class Stations:

    def FromDir(self, dir0):
        assert isinstance(dir0, object)
        self.dirname = dir0
        self.staGit = list()
        self.freq = list()
        os.chdir(self.dirname)
        fil = "*.site"
        print(" READING SITES, From:  ", self.dirname, end='')
        for file in glob.glob(fil):
            name = os.path.join(self.dirname, file)
            #        print(name)
            self.staGit.append(StatGit(name, False))
        self.nsta = len(self.staGit)
        if self.nsta > 0:
            self.progname = self.staGit[0].programName
            self.nfreq = self.staGit[0].nfreq
            self.freq = list()
            for i in range(self.nfreq):
                self.freq.append(self.staGit[0].freq[i])

    def __init__(self, *args: object):
        self.staGit = list()
        self.freq = list()
        if len(args) == 4:
            self.dirname = args[2]
            self.freq = args[0]
            self.staGit = args[1]
            self.progname = args[3]
            self.nsta = len(self.staGit)
            self.nfreq = len(self.freq)
        elif len(args) == 1:
            self.FromDir(args[0])

    def toAmp(self):
        for i in range(self.nsta):
            for j in range(self.nfreq):
                self.staGit[i].val[j] = pow(10, self.staGit[i].val[j])

    def WriteStations(self):
        for i in range(self.nsta):
            self.staGit[i].WriteStation(self.freq, self.dirname, self.progname)

    def plotStations(self, name_out, v1, v2):
        f1 = np.asarray(self.freq)
        count = 0
        for i in range(self.nsta):
            #     print(self.staGit[i].ref)
            if self.staGit[i].ref == True:
                #  print(self.staGit[i].ref)
                count = count + 1
        st = "Inv: {:s}, Cmp: {:s}, Nstat: {:d} (Nref: {:d})".format(self.progname, self.staGit[0].cmp, self.nsta,
                                                                     count)
        for i in range(self.nsta):
            #        print(i, " ",self.staGit[i].Stat)
            y1 = np.asarray(self.staGit[i].val)
            #     y1=np.asarray(self.staGit[i].val)
            st0 = self.staGit[i].Stat
            st1 = [st0 for i in range(self.nfreq)]
            ref = self.staGit[i].ref
            if ref == True:
                #  print(self.staGit[i].Stat)
                s1 = ["RefS" for i in range(self.nfreq)]
            else:
                s1 = ["No RefS" for i in range(self.nfreq)]
            d1 = {'x': f1, 'y': y1, 'TY': st1, 'Site': s1}
            d1 = pd.DataFrame(d1)
            if i == 0:
                dtot = d1
            else:
                dtot = dtot.append(d1)
            del y1
        dtot = dtot.reset_index()
        dr = dtot[(dtot['Site'] == 'RefS')]
        dr = dr.reset_index()
        dnr = dtot[(dtot['Site'] == 'No RefS')]
        dnr = dnr.reset_index()
        if v1 != False or v2 != False:
            g = ggplot()
            g = g + geom_line(dnr, aes(x='x', y='y', group='TY', colour='Site'), size=.4, alpha=.9)
            g = g + geom_line(dr, aes(x='x', y='y', group='TY', colour='Site'), size=1.3, alpha=.9)
            g = g + scale_color_manual(values=['darkgray', 'dodgerblue'])
            g = g + scale_x_log10(breaks=[0.3, 1.0, 3.0, 10.0, 30.0])
            g = g + annotation_logticks(sides="b")
            g = g + coord_cartesian(ylim=[0.0, 8])
            g = g + xlab("Frequency [Hz]") + ylab("Amplitude")
            g = g + ggtitle(st)
            g = g + theme_bw()
            print(g)
            if v2 == True:
                if name_out:
                    g.save(filename=name_out, dpi=300)


def main():
    p1 = Stations("/home/lara/Trento/OUT_GIT/SITES")
    p1.plotStations("/home/lara/Sites.jpg", True, True)


if __name__ == "__main__":
    main()
