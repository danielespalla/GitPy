#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 10:31:51 2022

@author: daniele
"""

import gc
import glob
import os
import sys

import pandas as pd


class FasName:
    def __init__(self, nm, f0):
        self.freq = float(f0)
        self.name = nm


class InputFas:
    def __init__(self, cfg, logf, GitR, progname):
        self.log = logf
        self.GitRes = GitR
        fas = list()
        s1 = "....... START reading FAS Dir: {:s} ".format(cfg.fas_dir)
        logf.write(s1)
        logf.write("\n")
        print(s1)
        self.Tables = list()
        os.chdir(cfg.fas_dir)
        #  fil = "FAS_*"
        fil = "*.fas"
        print("READING FAS: ")
        nskip = 0
        dmax = cfg.dist_bin[cfg.nbin_dist - 1]
        dmin = cfg.dist_bin[0]
        for file in glob.glob(fil):
            gc.collect()
            name = os.path.join(cfg.fas_dir, file)
            data = pd.read_table(name, header=0, delim_whitespace=True, nrows=1)
            if len(data) >= 1:
                f1 = data.iloc[0].Freq
                if f1 > cfg.fmin and f1 < cfg.fmax:
                    fas.append(FasName(name, f1))
                else:
                    nskip = nskip + 1
            else:
                nskip = nskip + 1
        self.nf = len(fas)
        if self.nf == 0:
            msg = f" ERROR FAS files = 0 (*.fas), FAS Dir {cfg.fas_dir} Aborting"
            logf.write(msg)
            logf.write("\n")
            print(msg)
            sys.exit()
        fas.sort(key=lambda x: x.freq, reverse=False)
        self.GitRes.make_list_freq(fas)
        nread = 0
        for i in range(len(fas)):
            name = fas[i].name
            f1 = fas[i].freq
            data = pd.read_table(name, header=0, delim_whitespace=True)
            data = data.loc[(data['Dipo'] > dmin) & (data['Dipo'] < dmax)]
            #   data=data.loc[(data['MLDib'] > cfg.mmin) & (data['MLDib'] < cfg.mmax)]
            data = data.loc[(data['Ml'] > cfg.mmin) & (data['Ml'] < cfg.mmax)]
            ndat = len(data)
            s1 = "FAS: {:5d} {:s} {:6.3f} Hz Ndat: {:10d}".format(nread + 1, name, f1, ndat)
            logf.write(s1)
            logf.write("\n")
            print(s1)
            self.Tables.append(data)
            if nread == 0:
                evt = data[['Id0', 'Ml', 'Lat', 'Lon', 'Dpt']]
                sta = data[['Stat', 'CMP', 'Net', 'StLat', 'StLon', 'StElev']]
            else:
                evt = evt.append(data[['Id0', 'Ml', 'Lat', 'Lon', 'Dpt']])
                sta = sta.append(data[['Stat', 'CMP', 'Net', 'StLat', 'StLon', 'StElev']])
            nread = nread + 1
        evt = evt.drop_duplicates('Id0', keep='last')
        ev3 = evt.drop_duplicates()
        ev3 = ev3[["Id0", "Ml", "Lat", "Lon", "Dpt"]].astype(str, float)
        self.GitRes.make_list_evt(ev3, cfg.cmp)
        s1 = "....... TOTAL NUMBER OF EVENTS: {:d}".format(len(self.GitRes.evtGit))
        logf.write(s1)
        logf.write("\n")
        print(s1)
        s1 = "    Id        Ml     Lat      Lon      Dpt"
        logf.write(s1)
        logf.write("\n")
        print(s1)
        for i in range(len(self.GitRes.evtGit)):
            s1 = self.GitRes.evtGit[i].toString(None, None)
            logf.write(s1)
            logf.write("\n")
            print(s1)
        s1 = "...................................................................."
        logf.write(s1)
        logf.write("\n")
        print(s1)
        sta = sta.drop_duplicates('Stat', keep='last')
        sta3 = sta.drop_duplicates()
        sta3 = sta3[['Stat', 'CMP', 'Net', 'StLat', 'StLon', 'StElev']].astype(str, float)
        self.GitRes.make_list_sta(sta3, cfg.cmp)
        s1 = "....... TOTAL NUMBER OF STATIONS: {:d} -----------".format(len(self.GitRes.staGit))
        logf.write(s1)
        logf.write("\n")
        print(s1)
        s1 = "Code  CMP   Net   Lat      Lon      Elev   RefSite"
        logf.write(s1)
        logf.write("\n")
        print(s1)
        for i in range(len(self.GitRes.staGit)):
            if (cfg.iref == 0):
                self.GitRes.staGit[i].ref = True
            else:
                val = (self.GitRes.staGit[i].Stat in cfg.REF_SITE)
                if val == True:
                    self.GitRes.staGit[i].ref = True
                else:
                    self.GitRes.staGit[i].ref = False
            s1 = self.GitRes.staGit[i].toString0(None)
            # s1 = self.GitRes.staGit[i].toString0()
            logf.write(s1)
            logf.write("\n")
            if (cfg.iref == 0):
                cfg.REF_SITE.append(self.GitRes.staGit[i].Stat)
            print(s1)
        s1 = "..................................................................."
        if (cfg.iref == 0):
            cfg.nsites = len(self.GitRes.staGit)
        logf.write(s1)
        logf.write("\n")
        print(s1)
        self.GitRes.set_inc()
        del evt
        del fas
        del sta
