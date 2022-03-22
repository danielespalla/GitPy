#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 09:19:02 2022

@author: daniele
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from plotnine import aes, ggplot, geom_point
from plotnine import theme_bw, xlab, ylab, scale_color_distiller, scale_x_continuous, annotation_logticks, ggtitle


def usageGit(msg):
    print(msg)
    sys.exit()


def PlotFAS(dtot1: object, f1: object, cmp: object, nevt: object, name_out: object, v1: object) -> object:
    s1 = "Freq: {:6.2f} Hz, CMP: {:s}, Nevt: {:d} Ndat: {:d}".format(f1, cmp, nevt, len(dtot1))
    br = [0.3, 1.0, 3.0, 10.0, 30.0, 40]
    dtot1['EW'] = dtot1['FAS_EW'] * dtot1['FAS_EW']
    dtot1['NS'] = dtot1['FAS_NS'] * dtot1['FAS_NS']
    dtot1['M'] = (dtot1['EW'] + dtot1['NS']) / 2
    dtot1['M'] = np.sqrt(dtot1['M'])
    dtot1['M'] = np.log(dtot1['M'])
    if cmp != 'H':
        dtot1['Z'] = np.log(dtot1['FAS_Z'])
        g = ggplot(dtot1, aes(x='Dipo', y='Z', color='Ml')) + geom_point(size=0.2)
    else:
        g = ggplot(dtot1, aes(x='Dipo', y='M', color='Ml')) + geom_point(size=0.2)
    g = g + scale_color_distiller(name='Ml ', palette=9, type='div')
    g = g + scale_x_continuous(trans='log10', breaks=br)
    g = g + annotation_logticks(sides="b")
    if cmp != 'H':
        g = g + xlab("Hypocentral [km]") + ylab("Log(Amplitude_Z)")
    else:
        g = g + xlab("Hypocentral [km]") + ylab("Log(Amplitude_H)")
    g = g + ggtitle(s1)
    g = g + theme_bw()
    print(g)
    if v1:
        if name_out:
            msg = f" saving graphic file: {name_out}"
            print(msg)
            g.save(filename=name_out, dpi=300)


def main():
    os.getcwd()
    nameFilejpg = ""
    graph = False
    if len(sys.argv) < 3:
        msg = "Usage: PlotFAS.py FasFile H,Z [Output.jpg]"
        usageGit(msg)
    nameFile = sys.argv[1]
    msg = f" FASfile: {nameFile}"
    print(msg)
    p1 = os.path.isdir(nameFile)
    if p1:
        msg = f" FATAL ERROR, FILE: {nameFile} is a dir.. Aborting"
        print(msg)
        sys.exit()
    p1 = os.access(nameFile, os.R_OK)
    if not p1:
        msg = f" FATAL ERROR, CANNOT READ FILE: {nameFile}.. Aborting"
        print(msg)
        sys.exit()
    cmp = sys.argv[2]
    if cmp != 'H' and cmp != 'Z':
        msg = f" FATAL ERROR, cmp: {cmp}..non allowed (H or Z), Aborting"
        print(msg)
        sys.exit()
    if len(sys.argv) > 3:
        nameFilejpg = sys.argv[3]
        msg = f" Graphic file: {nameFilejpg}"
        graph = True
        print(msg)
        p1 = os.path.isdir(nameFilejpg)
        if p1:
            msg = f" ERROR, FILE: {nameFilejpg} is a dir.. write jpg disabled"
            print(msg)
            graph = False
        if graph:
            p1 = os.path.isfile(nameFilejpg)
            if p1:
                msg = f" WARNING FILE: {nameFilejpg} exist !!!"
                print(msg)
                p1 = os.access(nameFilejpg, os.W_OK)
                if not p1:
                    msg = f' ERROR, CANNOT WRITE FILE: {nameFilejpg}.. write jpg disabled'
                    graph = False
                    print(msg)
            else:
                path = Path(nameFilejpg)
                dir0 = path.parent.absolute()
                p1 = os.access(dir0, os.W_OK)
                if not p1:
                    msg = f" ERROR, CANNOT WRITE FILE: {nameFilejpg}.. write jpg disabled"
                    graph = False
                    print(msg)
    data = pd.read_table(nameFile, header=0, delim_whitespace=True)
    f1 = data.iloc[0].Freq
    s1 = " Freq: {:6.2f} Hz, Ndat: {:d}".format(f1, len(data))
    print(s1)
    if len(data) == 0:
        msg = f" ERROR FAS File: {nameFile} Ndat=0. Aborting"
        print(msg)
        sys.exit()
    evt = data[['Id0', 'Ml', 'Lat', 'Lon', 'Dpt']]
    evt = evt.astype({'Id0': 'str'})
    evt = evt.drop_duplicates('Id0', keep='last')
    PlotFAS(data, f1, cmp, len(evt), nameFilejpg, graph)


if __name__ == "__main__":
    main()
