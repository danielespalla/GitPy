#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 07:33:01 2022

@author: daniele
"""

import sys
import os
from LibGit import Attenuation
from pathlib import Path


def usageGit(msg):
    print(msg)
    sys.exit()


def main():
    os.getcwd()
    name_file_jpg: str = ""
    graph = False
    if 2 > len(sys.argv):
        msg: str = "Usage: PlotAttenuation.py AttenuationFile [Output.jpg]"
        usageGit(msg)
    else:
        pass
    nameFile = sys.argv[1]
    msg = f" Attenuation file: {nameFile}"
    print(msg)
    p1 = os.path.isdir(nameFile)
    if p1:
        msg = f" FATAL ERROR, FILE: {nameFile} is a dir.. Aborting"
        print(msg)
        sys.exit()
    p1 = os.access(nameFile, os.R_OK)
    if p1:
        pass
    else:
        msg = f" FATAL ERROR, CANNOT READ FILE: {nameFile}.. Aborting"
        print(msg)
        sys.exit()
    if 2 < len(sys.argv):
        name_file_jpg = sys.argv[2]
        msg = f" Graphic file: {name_file_jpg}"
        graph = True
        print(msg)
        p1 = os.path.isdir(name_file_jpg)
        if p1:
            msg = f" ERROR, FILE: {name_file_jpg} is a dir.. write jpg disabled"
            print(msg)
            graph = False
        if graph:
            p1 = os.path.isfile(name_file_jpg)
            if not p1:
                path = Path(name_file_jpg)
                dir0 = path.parent.absolute()
                p1 = os.access(dir0, os.W_OK)
                if not p1:
                    msg = f" ERROR, CANNOT WRITE FILE: {name_file_jpg}.. write jpg disabled"
                    graph = False
                    print(msg)
            else:
                msg = f' WARNING FILE: {name_file_jpg} exist !!!'
                print(msg)
                p1 = os.access(name_file_jpg, os.W_OK)
                if not p1:
                    msg = f" ERROR, CANNOT WRITE FILE: {name_file_jpg}.. write jpg disabled"
                    graph = False
                    print(msg)
    Att = Attenuation(nameFile)
    Att.plotAttenuation(name_file_jpg, True, graph)


if __name__ == "__main__":
    main()
