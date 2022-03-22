# -*- coding: utf-8 -*-

import gc
import math
import os
import sys
from datetime import datetime

import numpy as np
import scipy
from numpy import count_nonzero
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import lsqr

from LibGit import Conf
from LibGit import GitResults
from LibGit import InputFas


def get_site_val(cfg,freq):
    crust=0
    refval=0
    v1=-1*math.pi*cfg.knot/math.log(10)
    val=math.isnan(cfg.Fk)
    if(val != True):
        if freq > val:       
           val=math.isnan(cfg.knot)
           if(val != True):
               slopeK=v1
           else:
               slopeK=0
        else:
           slopeK=0
    else:
        val=math.isnan(cfg.knot)
        if(val != True):
            slopeK=v1
        else:
            slopeK=0
    if cfg.n_freq_crust  > 1:
        n = cfg.n_freq_crust-1
        if freq < cfg.freq_crust[0]:
            pp = cfg.amp_crust[0]
        elif freq > cfg.freq_crust[n]:  
            pp = cfg.amp_crust[n]
        else:
            pp=cfg.spline_crust(freq)
        crust=math.log10(pp)
    refval=crust+slopeK*freq
    return refval
    
def DoInversion(logf,cfg,GitRes,Inp,nf):
        gc.collect()
        row = []
        col = []
        dtmat =[]
        bb= []
        s1="....... START Inversion Freq: {:7.2f} Hz  Nf: {:d} ".format(GitRes.LSQR_FREQ[nf],nf+1)
        logf.write(s1)
        logf.write("\n") 
        print(s1)
        Tab=Inp.Tables[nf]
        evt= Tab[['Id0']]
        evt = evt.drop_duplicates('Id0', keep='last')
        evt=evt.drop_duplicates()
        evt=evt['Id0'].astype(str)
        nevt=len(evt)
        ind_evt = np.zeros(shape=(nevt),dtype=int)
        ind_evt[:]=-1
        for i in range(len(evt)):
            id0=evt.iloc[i]
            if len(id0) == 11:
                id0="0"+id0
            ns=GitRes.EVT_ID.index(id0)
            ind_evt[i]=ns
        sta=Tab[['Stat']]
        sta=sta.drop_duplicates('Stat', keep='last')
        sta=sta.drop_duplicates()
        sta=sta['Stat'].astype(str)
        nsta=len(sta)
        ind_sta = np.zeros(shape=(nsta),dtype=int)
        ind_sta[:]=-1
        for i in range(len(sta)):
             stat=sta.iloc[i]
             ns=GitRes.STA_ID.index(stat)
             ind_sta[i]=ns
        ninc=cfg.nbin_dist+nevt+nsta
        s1="        Nstat: {:d} Nevt: {:d} Nbin_Dist: {:d} Tot Un: {:d}".format(nsta,nevt,cfg.nbin_dist,ninc)
        logf.write(s1)
        logf.write("\n") 
        print(s1)
        # # DATA KERNEL 
        nrow=0
        sta=sta.reset_index()
        evt=evt.reset_index()
        for i in range(len(Tab)):
            val=0
            if cfg.cmp == 'Z':
                val=Tab.iloc[i].FAS_Z*cfg.scale
            elif cfg.cmp == 'NS':  
                val=Tab.iloc[i].FAS_NS*cfg.scale
            elif cfg.cmp == 'EW':    
                val=Tab.iloc[i].FAS_EW*cfg.scale
            else:
                if cfg.mean == 'VECTORIAL':
                    EW=(Tab.iloc[i].FAS_EW*cfg.scale)*(Tab.iloc[i].FAS_EW*cfg.scale)
                    NS=(Tab.iloc[i].FAS_NS*cfg.scale)*(Tab.iloc[i].FAS_NS*cfg.scale)
                    val=math.sqrt(((EW+NS)/2))
                else:
                    val=math.sqrt((Tab.iloc[i].FAS_EW*cfg.scale)*(Tab.iloc[i].FAS_NS*cfg.scale))
            
            d=Tab.iloc[i].Dipo
            bb.append(math.log10(val))
            p1=next(x[0] for x in enumerate(cfg.dist_bin) if x[1] > d)
            # if p1 < 1:
            #     p1=1
            # if p1 > cfg.nbin_dist-1:
            #     p1 = cfg.nbin_dist-1
            d0=cfg.dist_bin[p1-1]
            dd=cfg.dist_bin[p1]-cfg.dist_bin[p1-1]
            w0=1-(d-d0)/dd
            w1=1-w0;
         #      Kernel Distance
            row.append(nrow)
            col.append(p1-1)
            dtmat.append(w0)
            row.append(nrow)
            col.append(p1)
            dtmat.append(w1)
            Id0=Tab.iloc[i].Id0
            Id0=str(Id0)
            indevt=evt[evt['Id0'] == Id0].index
            nevt0=indevt.values[0]
            if nevt0 < 0:   
                print("Ciao")
            Sta=Tab.iloc[i].Stat
            indsta=sta[sta['Stat'] == Sta].index
            nsta0=indsta.values[0]
            if nsta0 < 0:   
               print("Ciao")
        #      Kernel nevt    
            coln=cfg.nbin_dist+nevt0
            row.append(nrow)
            col.append(coln)
            dtmat.append(1)
        #      Kernel stat
            coln=cfg.nbin_dist+nevt+nsta0
            row.append(nrow)
            col.append(coln)
            dtmat.append(1)
            nrow=nrow+1
        # END DATA KERNEL 
        s1="        End data kernel nrow: {:d}  len(b): {:d} ".format(nrow,len(bb))
        nrow_data_kernel=nrow
        logf.write(s1)
        logf.write("\n") 
        print(s1)
        nref_site=0
        weight=0
        for i in range(cfg.nsites): 
       #     val=(cfg.REF_SITE[i] in self.STA_ID)
            staz=cfg.REF_SITE[i]
            val=staz in sta.values
            if val == True:
                nref_site=nref_site+1
                weight=1./nref_site;
        s1="        Site constraints, Iref: {:d}  Num ref site: {:d}, Total site ref site:  {:d}".format(cfg.iref,nref_site,cfg.nsites)        
        logf.write(s1)
        logf.write("\n") 
        print(s1)
        value = get_site_val(cfg,GitRes.LSQR_FREQ[nf])
        bb.append(value*cfg.weight_site)
       # print(" BB ",value*cfg.weight_site)
        for i in range(cfg.nsites): 
            staz=cfg.REF_SITE[i]
            val=staz in sta.values
            if val == True:
                indsta=sta[sta['Stat'] == cfg.REF_SITE[i]].index
                nsta0=indsta.values[0]
                coln=cfg.nbin_dist+nevt+nsta0
                row.append(nrow)
                col.append(coln)
                dtmat.append(weight*cfg.weight_site)
          #      print(" row ",weight*cfg.weight_site)
        nrow=nrow+1
        s1="        End site constraints nrow: {:d}  len(b): {:d} ".format(nrow,len(bb))
        logf.write(s1)
        logf.write("\n") 
        print(s1)
        # END SITE CONSTRAINT
        # REFERENCE DISTANCE CONSTRAINT
        bb.append(cfg.vdref*cfg.weight_dref)
        p1=next(x[0] for x in enumerate(cfg.dist_bin) if x[1] > cfg.dref)
        d0=cfg.dist_bin[p1-1]
        delta=cfg.dist_bin[p1]-cfg.dist_bin[p1-1]
        diff=cfg.dist_bin[p1]- cfg.dref
        v1=(diff/delta)*cfg.weight_dref
        dtmat.append(v1)
        row.append(nrow)
        col.append(p1-1)
        v1=(1-(diff/delta))*cfg.weight_dref
        dtmat.append(v1)
        row.append(nrow)
        col.append(p1)
        nrow=nrow+1
        s1="        End  dref constraint nrow: {:d}  len(b): {:d} ".format(nrow,len(bb))
        logf.write(s1)
        logf.write("\n") 
        print(s1)
        # END REFERENCE DISTANCE CONSTRAINT
        cnt = 1
        while cnt <= cfg.nbin_dist-2:
             indx=cnt
             diff21 = cfg.dist_bin[indx]-cfg.dist_bin[indx-1]
             diff32 = cfg.dist_bin[indx+1]-cfg.dist_bin[indx]
             diff31 = cfg.dist_bin[indx+1]-cfg.dist_bin[indx-1]
             v1=(-diff32/diff31)*cfg.weight_smo
             v2=1*cfg.weight_smo
             v3=(-diff21/diff31)*cfg.weight_smo
             col.append(cnt-1)
             dtmat.append(v1)
             row.append(nrow)
             col.append(cnt)
             dtmat.append(v2)
             row.append(nrow)
             col.append(cnt+1)
             dtmat.append(v3)
             row.append(nrow)         
             nrow=nrow+1
             bb.append(0*cfg.weight_smo)
             cnt=cnt+1
        s1="        End  Bin  Distance Smooth: {:d}  len(b): {:d} ".format(nrow,len(bb))
        logf.write(s1)
        logf.write("\n") 
        print(s1)     
        dtmat=np.array(dtmat)   
        row=np.array(row) 
        col=np.array(col) 
        bb=np.array(bb)
        A=csr_matrix((dtmat, (row, col)),shape=(nrow, ninc)).toarray()
        if A.size >0:
             sparsity = 1.0 - (float(count_nonzero(A))/ float(A.size))
             sparsity=sparsity*100
        else: 
             sparsity=0
        s1="        End Sparse Matrix construction, nrow: {:10d} ncol: {:10d} Sparsity: {:6.1f} % len(b): {:d}".format(nrow,ninc,sparsity,len(bb))
        logf.write(s1)
        logf.write("\n") 
        print(s1)        
        if nrow_data_kernel > cfg.nrow_min:
            s1="        LSQR INVERSION...."
            logf.write(s1)
            logf.write("\n") 
            print(s1) 
            x, istop, itn, r1norm=scipy.sparse.linalg.lsqr(A, bb, damp=1e-10, atol=1e-08, btol=1e-08, conlim=100000000.0, iter_lim=cfg.iter_lim, show=False, calc_var=False, x0=None)[:4]
            s1="        End LSQR INVERSION Stop Cond: {:d} Niter: {:d} R1norm: {:7.3f}".format(istop,itn,r1norm)
     #`     x, residuals, rank, s = np.linalg.lstsq(A,bb)
            logf.write(s1)
            logf.write("\n") 
            print(s1)
            inv=True
            i = 0
            while i < nevt:
                 nv=ind_evt[i]
                 Id1=GitRes.EVT_ID[nv]
                 Id2=GitRes.evtGit[nv].Id0
                 GitRes.evtGit[nv].val[nf]=x[i+cfg.nbin_dist]
                 Id0=evt.iloc[i]['Id0']
               #  print(" " , Id0 , "  " , Id1 , " " , i , " " , nevt , " ", Id2 , " ", nf)
                 i=i+1
            i = 0
            while i < nsta:
                 ns=ind_sta[i]
                 St1=GitRes.STA_ID[ns]
                 St2=GitRes.staGit[ns].Stat
                 GitRes.staGit[ns].val[nf]=x[i+cfg.nbin_dist+nevt]
                 St0=sta.iloc[i]['Stat']
                 # print(" " , St0 , "  " , St1 , " " , i , " " , nsta , " ", St2 , " ",  nf)
                 i=i+1
            GitRes.add_ResultsLsqr(x)
        else:
            s1="        WARNING  nrow_data_kernel: {:d} <  nrow_min (cfg): {:d}  Inversion = False ".format(nrow_data_kernel,cfg.nrow_min)
            logf.write(s1)
            logf.write("\n") 
            print(s1)
            x = np.zeros(shape=(ninc))
            x[:]=np.NaN
            GitRes.add_ResultsLsqr(x)
            inv=False
        s1="....... END Inversion Freq: {:7.2f} Hz".format(GitRes.LSQR_FREQ[nf])
        logf.write(s1)
        logf.write("\n") 
        print(s1)
        del ind_evt,ind_sta,evt,sta
        del row 
        del col
        del bb
        del A
        del dtmat

def usageGit(msg):
    print(msg)
    sys.exit()

def main():
    os.getcwd()
    progname = os.path.basename(sys.argv[0])
    progname = progname.replace(".py", "")
    if(len(sys.argv) <3):
        msg="Usage: GITeps.py ConfigFile Logfile\n Aborting"
        usageGit(msg)
    configFile=sys.argv[1]
    logFile=sys.argv[2]
    print("-----  GITeps: earthquake,path and sites   -----")
    print("         Configuration file: ", configFile)
    print("                   Log file: ", logFile)  
    val=os.path.isfile(logFile)
    if(val):
        write=os.access(logFile, os.W_OK)
        if write == False: 
            msg=f" Cannot write Log File {logFile} \n Aborting"
            usageGit(msg)
        else:
            msg=f" Warning Log File {logFile} exist !"
            print(msg)
    else:
        pa=os.path.dirname(logFile)
        write=os.access(pa, os.W_OK)
        if write == False: 
            msg=f" Cannot write File {logFile} \n Aborting"
            usageGit(msg)
    val=os.path.isfile(configFile)  
    if val == False:   
        msg=f" Config File {configFile} not found\n Aborting"
        usageGit(msg)
    log_file = open(logFile, "w")
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    s1=" ---------------------- GITeps, Starting computation: {:s} ---------".format(dt_string)
    log_file.write(s1)
    log_file.write("\n")
    print(s1)
    s1="> Configuration File: {:s} ".format(configFile)
    log_file.write(s1)
    log_file.write("\n")
    s1="> Log File: {:s} ".format(logFile)
    log_file.write(s1)
    log_file.write("\n")
    cfg=Conf(configFile,log_file)
    GitRes=GitResults(progname)
    inp=InputFas(cfg,log_file,GitRes,progname)
    for i in range(inp.nf):
        DoInversion(log_file,cfg,GitRes,inp,i)
    GitRes.WriteResults(cfg,log_file)
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    s1=" ---------------------- GITeps, End computation: {:s} ---------".format(dt_string)
    log_file.write(s1)
    log_file.write("\n")
    print(s1)
    log_file.close()

    
main()
