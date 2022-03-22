#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 30 18:28:32 2021

@author: daniele
"""
import math
import sys

import numpy as np
import pandas as pd
from plotnine import aes, ggplot, annotation_logticks, ggtitle
from plotnine import geom_line
from plotnine import theme_bw, xlab, ylab, scale_color_distiller, scale_x_continuous, coord_cartesian


class Attenuation:
    nfreq: int

    def WriteAttenuation(self, fname):
        try:
            att_file = open(fname, "w")
        except FileNotFoundError:
            print(f"File {fname} not found.  Aborting")
            sys.exit(1)
        except OSError:
            print(f"OS error occurred trying to open {fname}")
            sys.exit(1)
        except Exception as err:
            print(f"Unexpected error opening {fname} is", repr(err))
            sys.exit(1)
        s1 = "{:s} {:s} ".format(self.progname, self.cmp)
        att_file.write(s1)
        att_file.write("\n")
        s1 = " Dist_[km]"
        att_file.write(s1)
        for i in range(self.nfreq):
            freq = self.freq[i]
            s1 = "  {:7.2f} ".format(freq)
            att_file.write(s1)
        att_file.write("\n")
        for j in range(self.ndist):
            s1 = " {:7.1f} ".format(self.dist[j])
            att_file.write(s1)
            for i in range(self.nfreq):
                s1 = " {:8.4f} ".format(self.att[j][i])
                att_file.write(s1)
            att_file.write("\n")
        att_file.close()

    def FromData(self, dist, freq, at, dr, name, cm):
        self.fname = ""
        self.dist = dist
        self.freq = freq
        self.nfreq = len(self.freq)
        self.ndist = len(self.dist)
        self.att = at
        self.dref = dr
        self.progname = name
        self.cmp = cm

    def FromFile(self, fname):
        self.fname = fname
        self.freq = list()
        self.dist = list()
        self.dref = math.nan
        str0 = list()
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
        line = line.rstrip('\n')
        p1 = line.split()
        self.progname = p1[0]
        self.cmp = p1[1]
        line = f.readline()
        ncount = 0
        self.ndist = 0
        while line:
            ncount = ncount + 1
            if ncount == 1:
                p1 = line.split()
                self.nfreq = len(p1) - 1
                cnt = 1
                while cnt <= self.nfreq:
                    self.freq.append(float(p1[cnt]))
                    cnt = cnt + 1
            else:
                p1 = line.split()
                self.dist.append(float(p1[0]))
                str0.append(p1)
            #  print("Ciao")
            line = f.readline()
        f.close()
        initial_val = 0.0
        self.ndist = len(str0)
        self.att = [[initial_val] * self.nfreq for _ in range(self.ndist)]
        for j in range(self.ndist):
            p1 = str0[j]
            v = 0;
            for i in range(self.nfreq):
                self.att[j][i] = float(p1[i + 1])
                v = v + float(p1[i + 1])
            if abs(v) < 0.1:
                self.dref = self.dist[j]

    def __init__(self, *args):
        if len(args) == 1:
            self.fname = str(args[0])
            self.FromFile(args[0])
        elif len(args) == 6:
            self.FromData(args[0], args[1], args[2], args[3], args[4], args[5])

    def plotAttenuation(self, name_out, v1, v2):
        st = "Inv: {:s}, Cmp: {:s}, Nfreq: {:d} ".format(self.progname, self.cmp, self.nfreq)
        for i in range(self.nfreq):
            y1 = np.empty(self.ndist, dtype=float)
            for j in range(self.ndist):
                y1[j] = self.att[j][i]
            fr = round(self.freq[i], 2)
            f1 = []
            f1 = [fr for i in range(self.ndist)]
            frr = str(fr)
            s1 = []
            s1 = [frr for i in range(self.ndist)]
            d1 = {'x': self.dist, 'y': y1, 'TY': s1, 'FR': f1}
            d1 = pd.DataFrame(d1)
            if i == 0:
                dtot = d1
            else:
                dtot = dtot.append(d1)
        # dtot = dtot.reset_index()
        xmax = self.dist[self.ndist - 1]
        xmax = math.log10(xmax)

        br = []
        br = [5.0, 10, 20, 50, 100]
        c1 = []
        c1 = [0.6, xmax]
        vdref = math.isnan(self.dref)
        if vdref == False:
            dtot = dtot[(dtot["x"] >= self.dref)]
            unox = [[self.dref, 0, 'T'], [10 + self.dref, -1, 'T'], [100 + self.dref, -2, 'T']]
        else:
            unox = [[1, 0], [10, -1], [100, -2]]
        unox = pd.DataFrame(unox, columns=['X', 'Y', 'TY'])
        dtot = dtot.reset_index()
        if v1 != False or v2 != False:
            g = ggplot(dtot, aes(x='x', y='y', group='TY', color='FR')) + geom_line(size=0.9)
            #     g=g+geom_line(unox, aes(x='X', y='Y',group='TY'),color="red")
            g = g + scale_color_distiller(name='Freq  [Hz]', palette=9, type='div')
            #  g=g+xlim(-100, 200)
            g = g + coord_cartesian(xlim=c1)
            g = g + scale_x_continuous(trans='log10', breaks=br)
            #   g=g+scale_x_continuous(trans='log10')
            g = g + annotation_logticks(sides="b")
            g = g + xlab("Hypocentral Distance [km]") + ylab("Log(Attenuation)")
            g = g + ggtitle(st)
            g = g + theme_bw()
            if v1 != False:
                print(g)
            if v2 != False:
                if name_out:
                    msg = f" saving graphic file: {name_out} \n"
                    print(msg)
                    g.save(filename=name_out, dpi=300)
        del dtot
    #   ggsave(filename = "/home/lara/Attenuation.jpg",g,width = 6, height = 4, dpi = 300, units = "in", device='png')


def main():
    #  p1=Attenuation("/home/lara/Attenuation.txt")
    p1 = Attenuation("/home/daniele/Trento/OUT_GIT/Attenuation.txt")
    # p1.plotAttenuation(None)
    p1.plotAttenuation("/home/daniele/Attenuation.jpg", True, True)


if __name__ == "__main__":
    main()
