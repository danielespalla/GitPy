#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 30 18:28:32 2021

@author: daniele
"""
import glob
import math
import os
import sys

import numpy as np
import pandas as pd
from plotnine import aes, ggplot, geom_line, ggtitle, scale_x_log10
from plotnine import theme_bw, xlab, ylab, scale_color_distiller, annotation_logticks

from LibGit import EvtGit


class Sources:
    def __init__(self, *args):
        self.evtGit = list()
        self.freq = list()
        if len(args) == 4:
            self.dirname = args[2]
            self.freq = args[0]
            self.evtGit = args[1]
            self.progName = args[3]
            self.nevt = len(self.evtGit)
            self.nfreq = len(self.freq)
        elif len(args) == 1:
            self.FromDir(args[0])

    def FromDir(self, dirname):
        self.dirname = dirname
        self.evtGit = list()
        self.freq = list()
        self.nevt = 0
        os.chdir(self.dirname)
        fil = "*.source"
        print(" READING SOURCES, From:  ", self.dirname, end='')
        for file in glob.glob(fil):
            name = os.path.join(self.dirname, file)
            #  print(name)
            self.evtGit.append(EvtGit(name))
        self.nevt = len(self.evtGit)
        if self.nevt > 0:
            self.progName = self.evtGit[0].programName
            self.nfreq = self.evtGit[0].nfreq
            self.freq = list()
            for i in range(self.nfreq):
                self.freq.append(self.evtGit[0].freq[i])
        #  st="Inv: {:s}, Cmp: {:s}, Nstat: {:d} (Nref: {:d})".format(self.progName,self.staGit[0].cmp,self.nsta,count)

    def plotSources(self, name_out, v1, v2):
        dtot = None
        f1 = np.asarray(self.freq)
        st = "Inv: {:s}, Cmp: {:s}, Nevt: {:d} ".format(self.progName, self.evtGit[0].cmp, self.nevt)
        for i in range(self.nevt):
            #      print(i, " ",self.evtGit[i].nfreq)
            id0 = self.evtGit[i].Id0
            id1 = [id0 for i in range(self.nfreq)]
            m1 = round(self.evtGit[i].Ml, 2)
            #   m00=str(m1)
            s1 = []
            s1 = [m1 for i in range(self.nfreq)]
            d1 = {'x': f1, 'y': self.evtGit[i].val, 'TY': id1, 'FR': s1}
            d1 = pd.DataFrame(d1)
            if i == 0:
                dtot = d1
            else:
                dtot = dtot.append(d1)
        del f1
        del m1
        del s1
        if v1 != False or v2 != False:
            dtot = dtot.reset_index()
            g = ggplot(dtot, aes(x='x', y='y', group='TY', color='FR')) + geom_line(size=0.2)
            g = g + scale_color_distiller(name='Ml ', palette=9, type='div')
            g = g + scale_x_log10(breaks=[0.3, 1.0, 3.0, 10.0, 30.0])
            g = g + annotation_logticks(sides="b")
            g = g + xlab("Frequency [Hz]") + ylab("Log(Source)")
            g = g + ggtitle(st)
            g = g + theme_bw()
            if v1:
                print(g)
            if v2 != False:
                if name_out:
                    g.save(filename=name_out, dpi=300)

    def WriteSources(self):
        for i in range(self.nevt):
            id1 = self.evtGit[i].Id0
            name = os.path.join(self.dirname, id1)
            name = name + ".source"
            try:
                evt = open(name, "w")
            except FileNotFoundError:
                print(f"File {name} not found.  Aborting")
                sys.exit(1)
            except OSError:
                print(f"OS error occurred trying to open {name}")
                sys.exit(1)
            except Exception as err:
                print(f"Unexpected error opening {name} is", repr(err))
                sys.exit(1)
            s1 = self.evtGit[i].toString(self.progName, self.evtGit[0].cmp)
            evt.write(s1)
            evt.write("\n")
            for j in range(self.nfreq):
                s1 = "  {:7.2f} {:e}".format(self.freq[j], self.evtGit[i].val[j])
                evt.write(s1)
                evt.write("\n")
            evt.close()


def main():
    p1 = Sources("/home/daniele/Trento/OUT_GIT/SOURCES")
    p1.plotSources("/home/daniele/Sources.jpg", True, False)


if __name__ == "__main__":
    main()
