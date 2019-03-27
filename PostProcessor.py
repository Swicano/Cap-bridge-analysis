#	The function of this program is to take as input file the files produced by the labview program designed to interface with the AH2700 capacitance bridge (tab separated, row one and two as header and unit, respectively, and 5 columns ('frequency','capacitance', 'loss', 'voltage', and 'time') and applies a fitting function to the data
#   The resulting fit data is output into a new file (tab separated) of format TBD

import argparse
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import os

# the input and output directory paths
pathOut = os.getcwd()+'\\Output\\'
pathIn =  os.getcwd()+'\\Input\\'
pathResults = os.getcwd()+'\\Results.txt'

# create output directory and  results file with header if it doesnt exist
try:
    os.makedirs(pathOut)
except FileExistsError:
    # directory already exists
    pass
    
fileHeader = 'FileName \t fitted y0 \t fitted y0_err \t fitted x0 \t fitted x0_err \t fitted r2 \t fitted r2_err \t Conductance \t Conductance_error \t \t \t filesep1 \t filesep2 \t filesep3 \t filesep4 \t filesep5 \t filesep6 \t filesep7 \t filesep8 \t filesep9 \t filesep10 \t filesep11 \t filesep12 \t filesep13 \t filesep14 \t \n'
fileUnits = 'string \t Ohms \t Ohms \t Ohms \t Ohms \t Ohms^2 \t Ohms^2 \t S \t S \n'
if not os.path.isfile(pathResults):
    with open(pathResults, "a") as file:
        file.write(fileHeader)
        file.write(fileUnits)

# open the input directory and grab each .txt file
inputfiles = [i for i in os.listdir(pathIn) if i.endswith("txt")]

for fstring in inputfiles:

    # Step Zero: define the column names <-> indices as semi constants for later

    inFreq = 0      
    inCapPF = 1     # in the input array the CAPacitance (in PicoFarads) is in column 1
    inLoss = 2
    inVolt = 3
    inTime = 4
    
    avdFreqA = 0    # in the averaged array, the FREQuency Average is column 0
    avdCapPFA = 1
    avdLossA = 2
    avdVoltA = 3
    avdTimeA = 4
    avdFreqS = 5    # in the averaged array, the FREQuency Standarddeviation is column 5
    avdCapPFS = 6
    avdLossS = 7
    avdVoltS = 8
    avdTimeS = 9
    
    
    # Step One: find an input file name somehow__________________________________________________________________________________________
    
    # The File name hardcoded (for testing)
    #fname = "C:\\Users\\gfirest\\Documents\\GitHub\\Cap-bridge-analysis\\testdata\\2700A S1 NtN1 50 After silane treatment 1 Bare Electrode R1 120oC Heating 02-09-2019.txt"
    fname = pathIn+fstring
    # Step Two: read the file into a numpy array_________________________________________________________________________________________
    
    # quite possibly the worst converter function ever made. decodes the timestamp format from labview to unix time in seconds
    # assumes the exact format '03-18-2019-13:34:11' with that extra dash
    convertr = lambda s: float(datetime.datetime(int(s.decode().split('-')[2]),int(s.decode().split('-')[0]),int(s.decode().split('-')[1]),int(s.decode().split('-')[3].split(':')[0]),int(s.decode().split('-')[3].split(':')[1]),int(s.decode().split('-')[3].split(':')[2])).timestamp())
    
    #whomp i already found a better way
    convertp = lambda s: float(datetime.datetime.strptime( s.decode(), "%m-%d-%Y-%H:%M:%S").timestamp())
    
    inputarray = np.loadtxt(fname, skiprows=2, converters={inTime : convertp}) # first two rows are headers and never change, so we skip them.
    
    # Step Three: ''massage'' the data as Brent calls it________________________________________________________________________________
    #       in this step we take the input data and potentially average all the input data at each frequency
    
    # avgedinput will give an array twice as wide of [avg] concat to [std] 
    avgedinput = np.vstack([np.concatenate([inputarray[inputarray[:,inFreq] == freq].mean(0),inputarray[inputarray[:,inFreq] == freq].std(0)],0) for freq in set(inputarray[:,inFreq])])
    
    
    # if NOT averaged
    freqOmega = inputarray[:,inFreq]*2*np.pi
    capFar = inputarray[:,inCapPF]*10**(-12)
    
    resist = 1 / (freqOmega * capFar * inputarray[:,inLoss])
    ImpedanceReal = resist/(1+capFar**2*resist**2*freqOmega**2)
    ImpedanceImag = (capFar*resist**2*freqOmega)/(1+capFar**2*resist**2*freqOmega**2)
    ImpedanceMag = (ImpedanceReal**2+ImpedanceImag**2)**.5
    
    # if YES averaged
    freqOmegaAvg = avgedinput[:,avdFreqA]*2*np.pi
    capFarAvg = avgedinput[:,avdCapPFA]*10**(-12)	
    
    resistAvg = 1 / (freqOmegaAvg * capFarAvg * avgedinput[:,avdLossA])
    ImpedanceRealAvg = resistAvg/(1+capFarAvg**2*resistAvg**2*freqOmegaAvg**2)
    ImpedanceImagAvg = (capFarAvg*resistAvg**2*freqOmegaAvg)/(1+capFarAvg**2*resistAvg**2*freqOmegaAvg**2)
    ImpedanceMagAvg = (ImpedanceRealAvg**2+ImpedanceImagAvg**2)**.5
    
    resistStd = (avgedinput[:,avdLossS]**2/(capFarAvg**2*avgedinput[:,avdLossA]**4*freqOmegaAvg**2)+(avgedinput[:,avdCapPFS]*10**(-12))**2/(capFarAvg**4*avgedinput[:,avdLossA]**2*freqOmegaAvg**2))**0.5
    
    ImpedanceRealStd = ((4*capFarAvg**2*(avgedinput[:,avdCapPFS]*10**(-12))**2*resistAvg**6*freqOmegaAvg**4+resistStd**2*(1-2*capFarAvg**2*resistAvg**2*freqOmegaAvg**2+capFarAvg**4*resistAvg**4*freqOmegaAvg**4))/(1+capFarAvg**2*resistAvg**2*freqOmegaAvg**2)**4)**.5
    
    ImpedanceImagStd = ((resistAvg**2*freqOmegaAvg**2*((avgedinput[:,avdCapPFS]*10**(-12))**2*resistAvg**2+capFarAvg**4*(avgedinput[:,avdCapPFS]*10**(-12))**2*resistAvg**6*freqOmegaAvg**4+capFarAvg**2*(4*resistStd**2-2*(avgedinput[:,avdCapPFS]*10**(-12))**2*resistAvg**4*freqOmegaAvg**2)))/(1+capFarAvg**2*resistAvg**2*freqOmegaAvg**2)**4)**.5
    
    ImpedanceMagStd = ((ImpedanceImagStd*ImpedanceImagAvg**2)/(ImpedanceImagAvg**2+ImpedanceRealAvg**2)+(ImpedanceRealStd**2*ImpedanceRealAvg**2)/(ImpedanceImagAvg**2+ImpedanceRealAvg**2))**0.5
    
    # Step Four we now want to estimate the initial parameters of the circle from just the first 3 points._______________________________
    
    xin3 = np.array([1,2,3], dtype=np.float64)
    xin3[0] = np.max(ImpedanceRealAvg)
    xin3[1] = np.median(ImpedanceRealAvg)
    xin3[2] = np.min(ImpedanceRealAvg)
    
    yin3 = np.array([1,2,3], dtype=np.float64)
    yin3[0] = ImpedanceImagAvg[np.argmax(ImpedanceRealAvg)]
    yin3[1] = ImpedanceImagAvg[np.where(ImpedanceRealAvg==np.median(ImpedanceRealAvg))[0][0]]
    yin3[2] = ImpedanceImagAvg[np.argmin(ImpedanceRealAvg)]
    
    par0 = np.array([1,2,3], dtype=np.float64)
    
        # y0 initial guess
    par0[0] = ((-xin3[0] + xin3[2])* (-xin3[0]**2 + xin3[1]**2 - yin3[0]**2 + yin3[1]**2) + (xin3[0] - xin3[1])* (-xin3[0]**2 + xin3[2]**2 - yin3[0]**2 + yin3[2]**2))/(2 *((-xin3[0] + xin3[2])* (-yin3[0] + yin3[1]) - (-xin3[0] + xin3[1])* (-yin3[0] + yin3[2])))
        # x0 initial guess
    par0[1] = (xin3[0]**2 - xin3[1]**2 - 2* par0[0]* yin3[0] + yin3[0]**2 + 2* par0[0] *yin3[1] - yin3[1]**2)/(2* (xin3[0] - xin3[1]))
        # r^2 initial guess
    par0[2] = (-par0[1] + xin3[0])**2 + (-par0[0] + yin3[0])**2
    
    # Step Five we want to create the various functions to pass into scipy adapted from__________________________________________________ https://docs.scipy.org/doc/scipy/reference/tutorial/optimize.html________________________________________________________________________
    
    def model(x, u):
        return x[0] + (-(u - x[1])**2 + x[2])**0.5
    
    def fun(x, u, y):
        return model(x, u) - y
    
    def jac(x, u, y):
        J = np.empty((u.size, x.size))
        J[:, 0] = 1.
        J[:, 1] = (1.* (u - x[1]))/(-(u - x[1])**2 + x[2])**0.5
        J[:, 2] = 0.5/(-(u - x[1])**2 + x[2])**0.5
        return J
    
    #u = ImpedanceRealAvg
    #y = ImpedanceImagAvg
    #x0 = par0
    res = least_squares(fun, par0, jac=jac, args=(ImpedanceRealAvg, ImpedanceImagAvg), verbose=0)
    pcov = [' ']*(len(res.x)) 
    cond = 1/(res.x[1]+(res.x[2]-res.x[0]**2)**.5)
    dcond = ' '
    
    output = [' ']*(len(res.x)+len(pcov)+5)
    output[0] = fname.rsplit('\\',1)[1]
    output[1:6:2] = [str(i) for i in res.x]
    output[2:7:2] = [str(i) for i in pcov]
    output[7] = str(cond)
    output[8] = str(dcond)
    output.extend(fname.rsplit('\\',1)[1].split('.',1)[0].split())
    
    with open(pathResults, "a") as results:
        results.write(" \t ".join(output)+'\n')
    
    # in case you want to graph these, uncomment this
    #u_test1 = np.linspace(par0[1]-par0[2]**0.5, par0[1]+par0[2]**0.5)
    #y_test1 = model(par0, u_test)
    #u_test = np.linspace(res.x[1]-res.x[2]**0.5, res.x[1]+res.x[2]**0.5)
    #y_test = model(res.x, u_test)
    #plt.plot(ImpedanceRealAvg, ImpedanceImagAvg, 'o', markersize=4, label='data')
    #plt.plot(u_test1, y_test1, label='initial model')
    #plt.plot(u_test, y_test, label='fitted model')
    #plt.xlabel("RealZ")
    #plt.ylabel("ImagZ")
    #plt.legend(loc='lower right')
    #plt.show()



