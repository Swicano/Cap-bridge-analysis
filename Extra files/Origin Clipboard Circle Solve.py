# -*- coding: utf-8 -*-
"""
Created on Sat May 19 16:25:52 2018

@author: brent_000
"""

import numpy as np
import pandas as pd
import re

class CircleExtract:
    DF=None
    filename=None
    outputfolder='C:/Users/brent_000/Documents/Clarke Lab/PythonTools/Quick Circle Solve/Output/'
    def __init__(self,name):
        self.filename=name
        self.DF=pd.DataFrame(columns=['Sample','Conductance','Error'])
    
    def r_and_psi_from_circle(self,sample,scale=0):
        df=pd.read_clipboard()
        
        x0arr=[float(a)for a in re.split(' ± ',df.iloc[2,1])]
        x0=x0arr[0]
        dx0=x0arr[1]
    
        y0arr=[float(a)for a in re.split(' ± ',df.iloc[3,1])]
        y0=y0arr[0]
        dy0=y0arr[1]
        
        r2arr=[float(a)for a in re.split(' ± ',df.iloc[4,1])]
        r2=r2arr[0]
        dr2=r2arr[1]
        
        cond=1/(x0+(r2-y0**2)**.5)
        dcond=(dx0**2/(x0+(r2-y0**2)**.5)**4)**0.5
        df=pd.DataFrame([[sample,cond*10**(-1*scale),dcond*10**(-1*scale)]],index=range(1),columns=['Sample','Conductance','Error'])
        self.DF=self.DF.append(df,ignore_index=True)
    
    def save(self):
        self.DF.to_csv(self.outputfolder+self.filename+'.csv',sep=',',index=False)
 

