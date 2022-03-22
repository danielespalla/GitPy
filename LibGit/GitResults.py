#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 16:43:13 2021

@author: daniele
"""

import os
import sys

from LibGit import Attenuation
from LibGit import EvtGit
from LibGit import Sources
from LibGit import StatGit
from LibGit import Stations


class GitResults:          
    def __init__(self,prog): 
        self.evtGit=list()       
        self.staGit=list() 
        self.STA_ID=list()
        self.EVT_ID=list()
        self.LSQR_RES=list()
        self.LSQR_FREQ=list()
        self.progname=prog
    def make_list_freq(self, freqlist):
        for i in range(len(freqlist)):
            self.LSQR_FREQ.append(freqlist[i].freq)

    def make_list_evt(self, evtframe, cm):
        for i in range(len(evtframe)):
            id0 = evtframe.iloc[i][0]
            if len(id0) == 11:
                id0 = "0" + id0
            lst = evtframe.iloc[i].values.tolist()
            lst.pop(0)
            lst.insert(0, id0)
            lst.append(cm)
            self.evtGit.append(EvtGit(lst))
        #    self.evtGit.append(EvtGit.EvtGit(lst))
        self.evtGit.sort(key=lambda x: x.Id0, reverse=False)
        for i in range(len(self.evtGit)):
            self.EVT_ID.append(self.evtGit[i].Id0)

    def make_list_sta(self, staframe, cm):
        for i in range(len(staframe)):
            lst = staframe.iloc[i].values.tolist()
            self.staGit.append(StatGit(lst, cm))
        self.staGit.sort(key=lambda x: x.Stat, reverse=False)
        for i in range(len(self.staGit)):
            self.STA_ID.append(self.staGit[i].Stat)

    def set_inc(self):
        sizeevt=len(self.evtGit)
        self.nfreq=len(self.LSQR_FREQ)
        for x in range(sizeevt):
            self.evtGit[x].set_val(self.nfreq)
        sizesta=len(self.staGit)   
        for x in range(sizesta):
            self.staGit[x].set_val(self.nfreq)
            
    def add_sta(self, Sta,cmp): 
        size=len(self.staGit)
        find=False
        for x in range(size):
            if Sta.Stat == self.staGit[x].Stat:
                find=True
        if find == False:  
            self.staGit.append(StatGit.StatGit(Sta,cmp))
            
    def add_evt(self, Evt):   
       size=len(self.evtGit)
       find=False
       for x in range(size):
          if Evt.Id0 == self.evtGit[x].Id0:
              find=True
       if find == False:
           p1=EvtGit.EvtGit(Evt)
           self.evtGit.append(p1)
          # size=len(self.evtGit)
          # s1=self.evtGit[size-1].toString()
          # print(s1)
          
    def add_Freq(self, Freq):
        self.LSQR_FREQ.append(Freq)
        
    def add_ResultsLsqr(self, X):
        self.LSQR_RES.append(X)

    def WriteResults(self,cfg,logf):
        s1="......WRITE GIT RESULTS......................"
        path_gr=os.path.join(cfg.out_dir,"GRAPH")
        s1="  Directory for graphic files: {:s}".format(path_gr)
        val=os.path.isdir(path_gr)
        if val == True:
            s1="  WARNING Out Dir:  {:s} Exist! ".format(path_gr)
            logf.write(s1)
            logf.write("\n")  
            print(s1)
        else:
            flag=os.mkdir(path_gr)
            if flag == False:
                msg=f" Cannot create Dir {path_gr} \n Aborting"
                logf.write(msg)
                logf.write("\n")  
                print(msg)    
                sys.exit()
        logf.write(s1)
        logf.write("\n") 
        print(s1)
        nfr=len(self.LSQR_FREQ)
        nrow=cfg.nbin_dist
        initial_val = 0.0
        att = [[initial_val] * nfr for _ in range(nrow)]
        path=os.path.join(cfg.out_dir,"Attenuation.txt")
        s1="  File for attenuation:  {:s}".format(path)
        logf.write(s1)
        logf.write("\n") 
        print(s1)
        val = os.path.isfile(path)
        if val == True:
            s1="  WARNING Out File:  {:s} Exist .... Overwrite ".format(path)
            logf.write(s1)
            logf.write("\n")  
            print(s1)
      #  att_file = open(path, "w")
      #  s1=" Dist [km]"
      #  att_file.write(s1)
        for i in range(nfr):
            # freq=self.LSQR_FREQ[i]
       #     s1="  {:7.2f} ".format(freq)
        #    att_file.write(s1)
            sol=self.LSQR_RES[i]
            for j in range(nrow):
                att[j][i]=sol[j]
       # att_file.write("\n")
        Att = Attenuation(cfg.dist_bin, self.LSQR_FREQ, att, cfg.dref, self.progname, cfg.cmp)
        Att.WriteAttenuation(path)
        s1 = "  Plot Non Parametric attenuation curves....."
        logf.write(s1)
        logf.write("\n")
        print(s1)
        path1 = os.path.join(path_gr, "Attenuation.jpg")
        s1 = "  Graphic file for attenuation:  {:s}".format(path1)
        logf.write(s1)
        logf.write("\n")
        print(s1)
        Att.plotAttenuation(path1, cfg.plot_graph, cfg.save_graph)
        path = os.path.join(cfg.out_dir, "SOURCES")
        s1 = "  Directory for sources: {:s}".format(path)
        val = os.path.isdir(path)
        if val == True:
            s1 = "  WARNING Out Dir:  {:s} Exist! ".format(path)
            logf.write(s1)
            logf.write("\n")
            print(s1)
        else:
            flag = os.mkdir(path)
            if flag == False:
                msg = f" Cannot create Dir {path} \n Aborting"
                logf.write(msg)
                logf.write("\n")
                print(msg)
                sys.exit()
        Sou = Sources(self.LSQR_FREQ, self.evtGit, path, self.progname)
        Sou.WriteSources()
        path1 = os.path.join(path_gr, "Sources.jpg")
        s1 = "  Graphic file for sources:  {:s}".format(path1)
        logf.write(s1)
        logf.write("\n")
        print(s1)
        Sou.plotSources(path1, cfg.plot_graph, cfg.save_graph)        
        path=os.path.join(cfg.out_dir,"SITES")
        s1="  Directory for sites: {:s}".format(path)
        val=os.path.isdir(path)
        if val == True:
            s1="  WARNING Out Dir:  {:s} Exist! ".format(path)
            logf.write(s1)
            logf.write("\n")  
            print(s1)
        else:
            flag=os.mkdir(path)
            if flag == False:
                msg=f" Cannot create Dir {path} \n Aborting"
                logf.write(msg)
                logf.write("\n")  
                print(msg)    
                sys.exit()
        Sites=Stations(self.LSQR_FREQ,self.staGit,path,self.progname)
        Sites.toAmp()
        Sites.WriteStations()
        path1 = os.path.join(path_gr, "Sites.jpg")
        s1 = "  Graphic file for sites:  {:s}".format(path1)
        logf.write(s1)
        logf.write("\n")
        print(s1)
        Sites.plotStations(path1, cfg.plot_graph, cfg.save_graph)

