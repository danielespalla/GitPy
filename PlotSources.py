#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 18:00:25 2022

@author: daniele
"""
import os
import sys

from LibGit import Sources
from LibGit import EvtGit
from pathlib import Path


def usage(msg):
    print(msg)
    sys.exit()


def main():
    namefile = None
    sou = None
    Evt = None
    name_file_jpg = None
    graph = False
    if len(sys.argv) < 2:
        msg = "Usage: PlotSource.py dirname or filename [Output.jpg]"
        usage(msg)
    namedir: str = sys.argv[1]
    p1 = os.path.isdir(namedir)
    if p1:
        p1 = os.access(namedir, os.W_OK)
        if p1:
            msg = f" READING SOURCE FILE (*.source) FROM DIR: {namedir}"
            print(msg)
            sou = Sources(namedir)
            s1 = "Nsources: {:d}".format(sou.nevt)
            print(s1)
            if sou.nevt == 0:
                msg = f" FATAL ERROR, DIR: {namedir}.. 0 sources, Aborting"
                print(msg)
                sys.exit()
        else:
            msg = f" FATAL ERROR, CANNOT READ DIR: {namedir}.. Aborting"
            print(msg)
            sys.exit()
    else:
        p1 = os.path.isfile(namedir)
        if not p1:
            msg = f" FATAL ERROR, CANNOT READ DIR: {namedir}.. Aborting"
            print(msg)
            sys.exit()
        else:
            p1 = os.access(namedir, os.R_OK)
            if not p1:
                msg = f" FATAL ERROR, CANNOT READ FILE: {namedir}.. Aborting"
                print(msg)
                sys.exit()
            else:
                Evt = EvtGit(namedir)
    if len(sys.argv) > 2:
        name_file_jpg = sys.argv[2]
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
                    msg = f" ERROR, CANNOT WRITE FILE: {name_file_jpg}.. write jpg disabled"
                    graph = False
                    print(msg)
            else:
                path = Path(name_file_jpg)
                dir0 = path.parent.absolute()
                p1 = os.access(dir0, os.W_OK)
                if not p1:
                    msg = f" ERROR, CANNOT WRITE FILE: {name_file_jpg}.. write jpg disabled"
                    graph = False
                    print(msg)
    if not Evt:
        sou.plotSources(name_file_jpg, True, graph)
    else:
        Evt.plotSource(name_file_jpg, True, graph)
      #  Sta.plotStation(name_file_jpg, True, graph)


if __name__ == "__main__":
    main()

