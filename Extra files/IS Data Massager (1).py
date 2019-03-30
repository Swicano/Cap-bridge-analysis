import numpy as np
import pandas as pd
import re
from os import listdir
from os.path import isfile, join
targetfolder='C:/Users/brent_000/Documents/Clarke Lab/PythonTools/IS Data Massager/TargetData/'#'C:/Users/brent_000/Documents/Clarke Lab/labview files/My 2700A files/Data/'
outputfolder='C:/Users/brent_000/Documents/Clarke Lab/PythonTools/IS Data Massager/Output/'
#files=['NtPEO20NaIafterinpedanceanalyzer_redo_r1 03-19-2018','NtPEO20NaIafterinpedanceanalyzer_redo_r2 03-19-2018','NtPEO20NaIafterinpedanceanalyzer_redo_r3 03-19-2018','AB_PEO20NaIafterinpedanceanalyzer_redo_r1 03-19-2018','AB_PEO20NaIafterinpedanceanalyzer_redo_r1 03-20-2018','AB_PEO20NaIafterinpedanceanalyzer_redo_r2 03-20-2018','AB_PEO20NaIafterinpedanceanalyzer_redo_r3 03-20-2018']

def GetFiles(folder):
    onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f)) and re.search(' analyzed.txt\Z',f)==None and re.search(' meta.txt\Z',f)==None]
    return onlyfiles

def massage(_folder_,_file_,_outputfolder_, avfreq=True, labarr=[2,4,5,6,7],timef='relative'):
    '''
    avfreq determins wether to average all measurements of the same freqency
    labarr determines which parts of the file name will be used in the origin comments as a label
    time determines how to display time 'relative' will give relative to the first measurement or
    specify a string format such as 'MM-DD-YYYY hh:mm:ss' am/pm not supported
    '''
    _file_=re.sub('.txt\Z','',_file_)
    path=_folder_+_file_+'.txt'
    
    data=pd.read_csv(path,delimiter='\t')
    data_sub=data.loc[1:,:].copy().dropna()
    
    unitav=data.iloc[0:1,1:]
    if timef=='relative':
        unitav.loc[0,'Time']='s'
    unitstd=unitav.copy()
    unitav.columns=unitav.columns+' av.'
    unitstd.columns=unitstd.columns+' std'
    units=pd.concat([data.iloc[0:1,0:1],unitav,unitstd],axis=1)
    data_sub=data_sub.dropna()
    data_sub=data_sub.astype({'Freq.':float,'Cap.':float,'Loss':float})
    data_sub.loc[:,'Time']=data_sub.loc[:,'Time'].apply(lambda x:timeparse(x,timef))
    
    
    if avfreq==True:
        dataAv=pd.pivot_table(data_sub,index='Freq.',aggfunc=np.mean)
        dataStd=pd.pivot_table(data_sub,index='Freq.',aggfunc=np.std)
        dataAv.columns=dataAv.columns+' av.'
        dataStd.columns=dataStd.columns+' std'
        numDataAv=pd.concat([dataAv,dataStd],axis=1).reset_index()
        
    else:
        numDataAv=data_sub.sort_values(by='Freq.')
        numDataAv.columns=numDataAv.columns[0:1].append(numDataAv.columns[1:]+' av.')
        
    newindex=pd.Index(['Freq.','omega','Cap. av.','Cap. std','Loss av.','Loss std','ReZ av.','ReZ std','ImZ av.','ImZ std','MagZ av.','MagZ std','Time av.','Time std'])
    numDataAv=numDataAv.reindex(columns=newindex)
    DataAv=pd.DataFrame(index=[0],columns=newindex)
    units=units.reindex(columns=newindex)
    units.loc[0,'omega']='rad/s'
    units.loc[0,'ReZ av.':'MagZ std']='Ohms'
    
    ##############################################
    ######-----Convert to w and Farads-----#######
    ##############################################
    numDataAv.loc[:,'Cap. av.':'Cap. std']=numDataAv.loc[:,'Cap. av.':'Cap. std']*(10**(-12))
    numDataAv.loc[:,'omega']=numDataAv.loc[:,'Freq.']*2*np.pi
    units.loc[0,'Cap. av.']='F'
    units.loc[0,'Cap. std']='F'
    
    
    
    ##############################################
    ###### Calculate real and imaginary R ########
    ##############################################
    def ReZ(x):
        W=x['omega']
        C=x['Cap. av.']
        T=x['Loss av.']
        R=1/(C*T*W)
        ReZ=R/(1+C**2*R**2*W**2)
        return ReZ
    
    def ReZstd(x):
        W=x['omega']
        C=x['Cap. av.']
        dC=x['Cap. std']
        T=x['Loss av.']
        dT=x['Loss std']
        R=1/(C*T*W)
        dR=(dT**2/(C**2*T**4*W**2)+dC**2/(C**4*T**2*W**2))**0.5
        ReZstd=((4*C**2*dC**2*R**6*W**4+dR**2*(1-2*C**2*R**2*W**2+C**4*R**4*W**4))/(1+C**2*R**2*W**2)**4)**.5
        return ReZstd
    
    def ImZ(x):
        W=x['omega']
        C=x['Cap. av.']
        T=x['Loss av.']
        R=1/(C*T*W)
        ImZ=(C*R**2*W)/(1+C**2*R**2*W**2)
        return ImZ
    
    def ImZstd(x):
        W=x['omega']
        C=x['Cap. av.']
        dC=x['Cap. std']
        T=x['Loss av.']
        dT=x['Loss std']
        R=1/(C*T*W)
        dR=(dT**2/(C**2*T**4*W**2)+dC**2/(C**4*T**2*W**2))**0.5
        ImZstd=((R**2*W**2*(dC**2*R**2+C**4*dC**2*R**6*W**4+C**2*(4*dR**2-2*dC**2*R**4*W**2)))/(1+C**2*R**2*W**2)**4)**.5
        return ImZstd
    numDataAv.loc[:,'ReZ av.']=numDataAv.apply(ReZ,axis=1)
    numDataAv.loc[:,'ReZ std']=numDataAv.apply(ReZstd,axis=1)
    numDataAv.loc[:,'ImZ av.']=numDataAv.apply(ImZ,axis=1)
    numDataAv.loc[:,'ImZ std']=numDataAv.apply(ImZstd,axis=1)
    
    def AbsZ(x):
        ReZ=x['ReZ av.']
        ImZ=x['ImZ av.']
        
        return (ReZ**2+ImZ**2)**.5
    
    def AbsZstd(x):
        ReZ=x['ReZ av.']
        ImZ=x['ImZ av.']
        dReZ=x['ReZ std']
        dImZ=x['ImZ std']
        
        return ((dImZ*ImZ**2)/(ImZ**2+ReZ**2)+(dReZ**2*ReZ**2)/(ImZ**2+ReZ**2))**0.5
    
    numDataAv.loc[:,'MagZ av.']=numDataAv.apply(AbsZ,axis=1)
    numDataAv.loc[:,'MagZ std']=numDataAv.apply(AbsZstd,axis=1)
    
    if timef=='relative':
        numDataAv.loc[:,'Time av.']=numDataAv.loc[:,'Time av.']-numDataAv.loc[:,'Time av.'].min()
    numDataAv=numDataAv.dropna(axis=1)
    
    namematch=re.search('(.*) (S[0-9]+) (NtN*[0-9]+) ([0-9]+) ([0-9a-zA-Z]*) (R[0-9]+) (.*) ?([0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]).*',_file_)
    name=''
    for labi in labarr:
        try:
            name+=namematch[labi]+' '
        except:
            pass
    name=re.sub(' \Z','',name)
    DataAv.loc[:,:]=name
    DataAv=units.append(DataAv)
    DataAv=DataAv.append(numDataAv.astype('str'),ignore_index=True)
    DataAv=DataAv.reindex(columns=newindex)

    DataAv.to_csv(_outputfolder_+_file_+' analyzed'+'.txt',sep='\t',index=False)
    
def timeparse(time,form):
    tmatch=re.search('([0-9][0-9])-([0-9][0-9])-([0-9][0-9][0-9][0-9])-([0-9][0-9]):([0-9][0-9]):?([0-9]?[0-9]?)',time)
    mon,day,year,hour,mi,sec=tmatch.group(1),tmatch.group(2),tmatch.group(3),tmatch.group(4),tmatch.group(5),tmatch.group(6) 
    if sec=='':
        sec='00'    
    if form=='relative':
        mon,day,year,hour,mi,sec=[int(a) for a in [mon,day,year,hour,mi,sec]]
        
        
            
        totalsec=sec+mi*60+hour*60**2+day*60**2*24
        return totalsec
    else:
        def replace(subf,unit):
            n=len(subf.group(0))
            return unit[-n:]
        form=re.sub('M+',lambda x:replace(x,mon),form)
        form=re.sub('D+',lambda x:replace(x,day),form)
        form=re.sub('Y+',lambda x:replace(x,year),form)
        form=re.sub('h+',lambda x:replace(x,hour),form)
        form=re.sub('m+',lambda x:replace(x,mi),form)
        form=re.sub('s+',lambda x:replace(x,sec),form)
        
        return form
            
        

def run(avfreq=True,timef='relative'):    
    files=GetFiles(targetfolder)
    for file in files:
#        massage(targetfolder,file,outputfolder,avfreq=avfreq,timef=timef)
        try:
            massage(targetfolder,file,outputfolder,avfreq=avfreq,timef=timef)
        except:
            print(file+' not analyzed')
    
