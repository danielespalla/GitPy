#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 13:37:10 2022

@author: daniele
"""

import os
import sys
from pathlib import Path

from LibGit import StatGit
from LibGit import Stations


def usage(msg):
    print(msg)
    sys.exit()


def main():
    name_file_jpg = ""
    nameFile = None
    sites = None
    Sta = None
    graph = False
    # print(len(sys.argv))
    if 2 > len(sys.argv):
        msg = "Usage: PlotSites.py dirname or filename [Output.jpg]"
        usage(msg)
        sys.exit()
    nameDir = sys.argv[1]
    p1: bool = os.path.isdir(nameDir)
    # print(p1)
    if p1:
        p1 = os.access(nameDir, os.W_OK)
        if p1:
            msg = f" READING SITE FILE (*.site) FROM DIR: {nameDir}"
            print(msg)
            sites = Stations(nameDir)
            s1 = "Nsites: {:d}".format(sites.nsta)
            print(s1)
            if sites.nsta == 0:
                msg = f" FATAL ERROR, DIR: {nameDir}.. 0 sites, Aborting"
                print(msg)
                sys.exit()
        else:
            msg = f" FATAL ERROR, CANNOT READ DIR: {nameDir}.. Aborting"
            print(msg)
            sys.exit()
    else:
        p1 = os.path.isfile(nameDir)
        if not p1:
            msg = f" FATAL ERROR, CANNOT READ DIR: {nameDir}.. Aborting"
            print(msg)
            sys.exit()
        else:
            nameFile = nameDir
            p1 = os.access(nameFile, os.R_OK)
            if not p1:
                msg = f" FATAL ERROR, CANNOT READ FILE: {nameFile}.. Aborting"
                print(msg)
                sys.exit()
            else:
                Sta = StatGit(nameFile, False)
    if len(sys.argv) > 2:
        name_file_jpg: str = sys.argv[2]
        msg = f" Graphic file: {name_file_jpg}"
        graph = True
        print(msg)
        p1 = os.path.isdir(name_file_jpg)
        if p1:
            msg = f" ERROR, FILE: {name_file_jpg} is a dir.. write jpg disabled"
            print(msg)
            graph = False
        else:
            pass
        if graph:
            p1 = os.path.isfile(name_file_jpg)
            if p1:
                msg = f" WARNING FILE: {name_file_jpg} exist !!!"
                print(msg)
                p1 = os.access(name_file_jpg, os.W_OK)
                if not p1:
                    msg = f' ERROR, CANNOT WRITE FILE: {name_file_jpg}.. write jpg disabled'
                    graph = False
                    print(msg)
            else:
                path = Path(name_file_jpg)
                dir0 = path.parent.absolute()
                p1 = os.access(dir0, os.W_OK)
                if not p1:
                    msg = f' ERROR, CANNOT WRITE FILE: {name_file_jpg}.. write jpg disabled'
                    graph = False
                    print(msg)
    if not nameFile:
        sites.plotStations(name_file_jpg, True, graph)
    else:
        Sta.plotStation(name_file_jpg, True, graph)


if __name__ == "__main__":
    main()
