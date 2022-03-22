#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 16:43:13 2021

@author: daniele
"""

import configparser
import math
import os
import sys

import numpy as np
from scipy.interpolate import UnivariateSpline


class Conf:
    
    def ReadFileCrust(self):
        self.freq_crust=list()
        self.amp_crust=list()
        try:
            cru = open(self.FileCrust, 'rb')
         #   cru=open(self.FileCrust,"w")
        except FileNotFoundError:
            print(f"File {self.FileCrust} not found.  Aborting")
            sys.exit(1)
        except OSError:
            print(f"OS error occurred trying to open {self.FileCrust}")
            sys.exit(1)
        except Exception as err:
            print(f"Unexpected error opening {self.FileCrust} is",repr(err))
            sys.exit(1)
        self.n_freq_crust=0
        Lines = cru.readlines()
        ncount = 0
        for line in Lines:
            ncount += 1
            line = line.rstrip().decode()
            p1=line.split()
            self.amp_crust.append(float(p1[1]))
            self.freq_crust.append(float(p1[0]))
        freq=np.asarray(self.freq_crust)
        amp=np.asarray(self.amp_crust)
        self.n_freq_crust=ncount
        self.spline_crust = UnivariateSpline(freq, amp)
        cru.close()
        
    def ReadDistFile(self):
        distl=list()
        self.dist_step=0
        try:
            dist = open(self.FileDist, 'rb')
        except FileNotFoundError:
              print(f"File {self.FileDist} not found.  Aborting")
              sys.exit(1)
        except OSError:
              print(f"OS error occurred trying to open {self.FileDist}")
              sys.exit(1)
        except Exception as err:
              print(f"Unexpected error opening {self.FileDist} is",repr(err))
              sys.exit(1)
        self.n_freq_crust=0
        Lines = dist.readlines()
        ncount = 0
        for line in Lines:
            ncount += 1
            line = line.rstrip().decode()
            p1=line.split()
            distl.append(float(p1[0]))
        self.dist_bin=np.asarray(distl)
        self.nbin_dist=len(self.dist_bin)
        self.dist_max=self.dist_bin[self.nbin_dist-1]
        self.dist_min=self.dist_bin[0]
        dist.close()    
        
    def __init__(self,fname,logf):
       self.n_freq_crust=0
       self.ConfName = fname
       self.log=logf
       self.nrow_min=100
       self.damp = 1e-10
       self.atol = 1e-08 
       self.btol = 1e-08 
       self.iter_lim= 1000
       self.knot = float('nan')
       self.weight_smo = 20
       self.freq_crust=list()
       self.amp_crust=list()
       self.Fk = float('nan')
       self.scale = 1
       
       try:
           config = configparser.RawConfigParser()
           config.read(fname)
       except FileNotFoundError:
           print(f"File {fname} not found.  Aborting")
           sys.exit(1)
       except OSError:
           print(f"OS error occurred trying to open {fname}")
           sys.exit(1)
       except Exception as err:
           print(f"Unexpected error opening {fname} is",repr(err))
           sys.exit(1)
       s1="....... START reading Configuration File: {:s} ".format(fname)
       logf.write(s1)
       logf.write("\n") 
       print(s1)
       s1="-- Section GLOBAL --"
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.job_name = config.get('GLOBAL', 'job_name')
      # print(" Job Name: ", self.job_name)
       s1="> Job Name: {:s} ".format(self.job_name)
       logf.write(s1)
       logf.write("\n") 
       print(s1)
       self.fas_dir = config.get('GLOBAL', 'fas_dir')
       s1="> FAS dir: {:s} ".format(self.fas_dir)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.out_dir = config.get('GLOBAL', 'out_dir')
       s1="> FAS dir: {:s} ".format(self.out_dir)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       val=os.path.isdir(self.out_dir)
       if(val == True):
           s1="> WARNING Out Dir:  {:s} Exist! ".format(self.out_dir)
           logf.write(s1)
           logf.write("\n")  
           print(s1)
           write=os.access(self.out_dir, os.W_OK)
           if write == False: 
               msg=f" Cannot write Out Dir {self.out_dir} \n Aborting"
               logf.write(msg)
               logf.write("\n")  
               print(msg)    
               sys.exit()
       else:
           flag=os.mkdir(self.out_dir)
           if flag == False:
               msg=f" Cannot create Out Dir {self.out_dir} \n Aborting"
               logf.write(msg)
               logf.write("\n")  
               print(msg)    
               sys.exit()
           else:
               s1=" Succesfully created Out Dir:  {:s} ".format(self.out_dir)
               logf.write(s1)
               logf.write("\n") 
               print(s1)
       self.plot_graph=False
       self.plot_graph = config.get('GLOBAL', 'plot_graph')
       self.plot_graph=self.plot_graph.upper()
       if self.plot_graph != 'TRUE' and self.plot_graph != 'FALSE': 
           self.plot_graph=False
           s1="  WARNING INVALID plot_graph: {:s} (options: TRUE or FALSE') reset to default falue: FALSE".format(str(self.plot_graph))
           logf.write(s1)
           logf.write("\n")  
           print(s1)
       else:
           s1="> plot_graph: {:s} ".format(str(self.plot_graph))
           logf.write(s1)
           logf.write("\n")  
           print(s1)
       if self.plot_graph == 'FALSE':
           self.plot_graph=False
       if self.plot_graph == 'TRUE':
           self.plot_graph=True
       self.save_graph=False
       self.save_graph = config.get('GLOBAL', 'plot_graph')
       self.save_graph=self.save_graph.upper()
       if self.save_graph != 'TRUE' and self.save_graph != 'FALSE': 
           self.save_graph=False
           s1="  WARNING INVALID save_graph: {:s} (options: TRUE or FALSE') reset to default falue: FALSE".format(str(self.save_graph))
           logf.write(s1)
           logf.write("\n")  
           print(s1)
       else:
           s1="> save_graph: {:s} ".format(str(self.save_graph))
           logf.write(s1)
           logf.write("\n")  
           print(s1) 
       if self.save_graph == 'FALSE':
           self.save_graph=False
       if self.save_graph == 'TRUE':
           self.save_graph=True
       self.cmp = config.get('GLOBAL', 'cmp')
       if self.cmp != 'H' and self.cmp != 'NS' and self.cmp != 'EW' and self.cmp != 'Z': 
           s1="  WARNING INVALID cmp:   {:s} (options: H,NS,EW,Z) reset to default cmp  H ".format(self.cmp)
           self.cmp='H'
           logf.write(s1)
           logf.write("\n")  
           print(s1)
       s1="> cmp: {:s} ".format(self.cmp)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.scale = float(config.get('GLOBAL', 'scale'))
       s1="> scale (for FAS input):  {:6.2f} ".format(self.scale)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.mean = config.get('GLOBAL', 'mean')
       if self.mean != 'VECTORIAL' and self.mean != 'GEOM': 
          s1="  WARNING INVALID mean:  {:s} (options: VECTORIAL or GEOM) reset to default mean  VECTORIAL ".format(self.cmp)
          self.mean='VECTORIAL'
          logf.write(s1)
          logf.write("\n")  
          print(s1)
       s1="> mean: {:s} ".format(self.mean)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.fmin = float(config.get('GLOBAL', 'fmin'))
       s1="> fmin:  {:6.2f} Hz".format(self.fmin)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.fmax = float(config.get('GLOBAL', 'fmax'))
       s1="> fmax:  {:6.2f} Hz".format(self.fmax)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.mmin = float(config.get('GLOBAL', 'mmin'))
       s1="> Min Mag:  {:6.2f}".format(self.mmin)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.mmax = float(config.get('GLOBAL', 'mmax'))
       s1="> Max Mag:  {:6.2f}".format(self.mmax)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       s1="-- Section DIST BIN --"
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.type_bin = config.get('DIST BIN', 'type_bin')
       if self.type_bin != 'LIN' and self.type_bin != 'LOG' and self.type_bin != 'FILE': 
          s1="  Error INVALID type_bin:  {:s} (options: LIN or LOG or FILE \n Aborting ".format(self.type_bin)
          logf.write(s1)
          logf.write("\n")  
          sys.exit(1)
          print(s1)
       s1="> type_bin:  {:s} ".format(self.type_bin)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       if self.type_bin == 'LIN' or self.type_bin == 'LOG':
           self.dist_min = float(config.get('DIST BIN', 'dist_min'))
           s1="> dist_min:  {:7.2f} km".format(self.dist_min)
           logf.write(s1)
           logf.write("\n")  
           print(s1)
           self.dist_max = float(config.get('DIST BIN', 'dist_max'))
           s1="> dist_max:  {:7.2f} km".format(self.dist_max)
           logf.write(s1)
           logf.write("\n")  
           print(s1)
       if self.type_bin == 'LIN':
           self.dist_step = float(config.get('DIST BIN', 'dist_step'))
           s1="> dist_step: {:7.2f} km".format(self.dist_step)
           logf.write(s1)
           logf.write("\n")  
           print(s1)
           self.dist_bin=list(np.arange(self.dist_min, self.dist_max, self.dist_step))
           self.dist_bin=np.array(self.dist_bin)
           self.nbin_dist=len(self.dist_bin)
           s1="> n bin dist (LIN): {:d} ".format(self.nbin_dist)
           logf.write(s1)
           logf.write("\n")  
           print(s1)
       if self.type_bin == 'LOG':  
           self.nbin_dist = int(config.get('DIST BIN', 'nbin_dist'))
           s1="> n bin dist: (LOG) {:d} ".format(self.nbin_dist)
           logf.write(s1)
           logf.write("\n")  
           print(s1)
           v1=math.log10(self.dist_min)
           v2=math.log10(self.dist_max)
           self.dist_step=(v2-v1)/float(self.nbin_dist)
           self.dist_bin=list(np.arange(v1, v2, self.dist_step))
           self.dist_bin=np.array(self.dist_bin)
           self.dist_bin=10**self.dist_bin
       if self.type_bin == 'FILE':
           s1=config.get('DIST BIN', 'dist_file')
           self.FileDist = s1
           s1="> FileDist :  {:s} ".format(self.FileDist)
           logf.write(s1)
           logf.write("\n")  
           print(s1)
           self.ReadDistFile()
       s1="-- Section CONSTRAINT DREF --"
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.dref=float(config.get('CONSTRAINT DREF', 'dref'))
       s1="> reference distance: {:4.1f} km ".format(self.dref)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       if self.dref < 0 or self.dref < self.dist_bin[0] or self.dref >= self.dist_bin[self.nbin_dist-1]:
           msg=" dref must be > {:6.1f} km and < {:6.1f} km Aborting !".format(self.dist_bin[0],self.dist_bin[self.nbin_dist-1])
           print(msg)
           sys.exit()
       self.weight_dref=float(config.get('CONSTRAINT DREF', 'weight_dref'))
       s1="> weight_dref:  {:3.0f} ".format(self.weight_dref)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.vdref = float(config.get('CONSTRAINT DREF', 'vdref'))
       self.vdref = math.log10(self.vdref)
       s1="> vdref:  {:7.5f} ".format(self.vdref)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.REF_SITE=list()
       s1="-- Section CONSTRAINTS SITES --"
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       sites = config.get('CONSTRAINTS SITES', 'sites')
       if sites == 'ALL':
           self.iref=0
           self.nsites=0
           s1="> References Sites:  ALL "
           logf.write(s1)
           logf.write("\n")  
           print(s1)
       else: 
           self.iref=1
           p1=sites.split(",")
           self.nsites=len(p1)
           s1="> N reference site:  {:d}  ".format(len(p1))
           logf.write(s1)
           print(s1,end='')
           for i in range(self.nsites):
               self.REF_SITE.append(p1[i])
               s1=" {:s} ".format(p1[i])
               logf.write(s1)
               print(s1,end='')
               logf.write("\n")  
               print("")
       self.weight_site = float(config.get('CONSTRAINTS SITES', 'weight_site'))
       s1="> weight_site:  {:3.0f} ".format(self.weight_site)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       s1=(config.get('CONSTRAINTS SITES', 'Knot'))
       if s1 != 'Na' : 
         self.knot=float(s1)
         s1="> Knot :  {:7.5f} ".format(self.knot)
         
       else:
         s1="> Knot :  Na "
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       s1=(config.get('CONSTRAINTS SITES', 'FileCrust'))
       if s1 != 'Na' : 
         self.FileCrust = s1
         s1="> FileCrust :  {:s} ".format(self.FileCrust)
         self.ReadFileCrust()
       else:
         s1="> FileCrust :  Na "
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       s1=(config.get('CONSTRAINTS SITES', 'Fk'))
       if s1 != 'Na' : 
         self.Fk=float(s1)
         s1="> Threshold Freq (K):  {:7.5f} ".format(self.Fk)
       else:
         s1="> Threshold Freq (K): Na "
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       s1="-- [CONSTRAINTS SMOOTH DIST]"
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.weight_smo = float(config.get('CONSTRAINTS SMOOTH DIST', 'weight_smo'))
       s1="> weight_smo:  {:3.0f} ".format(self.weight_smo)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       s1="-- [LSQR INVERSION]"
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.nrow_min = int(config.get('LSQR INVERSION', 'nrow_min'))
       s1="> nrow_min:  {:d} ".format(self.nrow_min)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.damp = float(config.get('LSQR INVERSION', 'damp'))
       s1="> damp:  {:f} ".format(self.damp)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.atol = float(config.get('LSQR INVERSION', 'atol'))
       s1="> atol:  {:e} ".format(self.atol)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.btol = float(config.get('LSQR INVERSION', 'btol'))
       s1="> btol:  {:e} ".format(self.atol)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       self.iter_lim  = int(config.get('LSQR INVERSION', 'iter_lim'))
       s1="> iter_lim:  {:d} ".format(self.iter_lim)
       logf.write(s1)
       logf.write("\n")  
       print(s1)
       s1="....... END reading Configuration File: {:s} ".format(fname)
       logf.write(s1)
       logf.write("\n") 
       print(s1)
       
       