#	The function of this program is to take as input file the files produced by the labview program designed to interface with the AH2700 capacitance bridge (tab separated, row one and two as header and unit, respectively, and 5 columns ('frequency','capacitance', 'loss', 'voltage', and 'time') and applies a fitting function to the data to extract the desired data as requested by Brent and Neelam
#   First however, for consistency the data is "massaged" according to Data Massager.py (by brent) where any data points that are taken at the same frequency are averaged together
#   Next we convert from the machine units of freq, cap, loss, etc to those we need for fitting, Real and Imaginary Impedance
#   finally we fit the resulting RealZ vs ImagZ to a semi circle using scippy optimize
#   The resulting fit data is output into a new line appended onto the file "Results.txt" which will be created if it doesnt exist
#   The transformed input data is output into a new file called 'OUTPUT'+input_file_name in the Output folder, tab separated format of 20 columns where the first 10 columns are the average and standard deviation of the original input columns, and the next 2 are unit changes of the input, then the last 8 are the average and standard deviation of the calculated resistance, real/imaginary/ and magnitude of the impedance


import numpy as np
import datetime
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
#       Note: we assume eveything in the directory is of the right format, no training wheels for now
inputfiles = [i for i in os.listdir(pathIn) if i.endswith("txt")]

for fstring in inputfiles:

    # Step Zero: define the column names <-> indices as semi constants for later_______________________________________________________
    #__________________________________________________________________________________________________________________________________
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
    #__________________________________________________________________________________________________________________________________
    fname = pathIn+fstring
    fOutname = pathOut+'OUTPUT '+fstring
    
    #check if the output file already exists, if it does we assume that the input file has already been run and skip it 
    if os.path.isfile(fOutname):
        continue
    
    # Step Two: read the file into a numpy array_And do some preprocessing:_____
    #_________________________________a) get rid of nan rows____________________
    #_________________________________b) sort rows by frequency ________________
    
    
    # we need a converter to read the wacky timestamp that Labview outputs
    def convertb(s):
        try:
            return float(datetime.datetime.strptime( s.decode(), "%m-%d-%Y-%H:%M:%S").timestamp())
        except ValueError:  # in case seconds dont get printed? that never came up for me
            return float(datetime.datetime.strptime( s.decode(), "%m-%d-%Y-%H:%M").timestamp())
    convertp = lambda s: convertb(s)
    # first two rows are headers and never change, so we skip them, since we think we know what the column layout will be anyways
    
    #inputarray = np.loadtxt(fname, skiprows=2, converters={inTime : convertp}) 
            # UGH we need to deal with missing numbers, so loadtxt is out, and genfromtxt is in
    # missing values become NaN
    inputrawarray = np.genfromtxt(fname, skip_header=2, delimiter="\t" ,converters={inTime : convertp}) 
    # remove those rows
    inputarrayuns = inputrawarray[~np.isnan(inputrawarray).any(axis=1)] 
    # then sort it since neelam wants it sorted and its easiest to do it here so that avg input is sorted also (not sure if this is guaranteed)
    inputarray = inputarrayuns[inputarrayuns[:,0].argsort()] # 0 is the 1st column, change to sort by other columns
    
    # Step Three: ''massage'' the data as Brent calls it________________________________________________________________________________
    #__________________________________________________________________________________________________________________________________
    #       in this step we take the input data and potentially average all the input data at each frequency 
    # avgedinput will give an array twice as wide of [avg] concat to [std] 
    avgedinput = np.vstack([np.concatenate([inputarray[inputarray[:,inFreq] == freq].mean(0),inputarray[inputarray[:,inFreq] == freq].std(0)],0) for freq in dict.fromkeys(inputarray[:,inFreq])])
    
    #       Then we calculate some new numbers from the averaged (and unaverraged data, though we dont use it ever?)
    Averaged = True
    # if NOT averaged
    if (not Averaged):
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
    #__________________________________________________________________________________________________________________________________
    
    # grab three (x,y) points (i chose the first last and median for simpllicity. i recommend keeping the first and last, but you can change the middle one to anything, it doesnt really matter)
    xin3 = np.array([1,2,3], dtype=np.float64)
    xin3[0] = ImpedanceRealAvg[0]
    xin3[1] = ImpedanceRealAvg[int(len(ImpedanceRealAvg)/2)]
    xin3[2] = ImpedanceRealAvg[-1]
    
    yin3 = np.array([1,2,3], dtype=np.float64)
    yin3[0] = ImpedanceImagAvg[0]
    yin3[1] = ImpedanceImagAvg[int(len(ImpedanceRealAvg)/2)]
    yin3[2] = ImpedanceImagAvg[-1]
    
    # define a numpy vector to hold the three parameters y0,x0,and r2
    par0 = np.array([1,2,3], dtype=np.float64)
    
        # y0 initial guess
    par0[0] = ((-xin3[0] + xin3[2])* (-xin3[0]**2 + xin3[1]**2 - yin3[0]**2 + yin3[1]**2) + (xin3[0] - xin3[1])* (-xin3[0]**2 + xin3[2]**2 - yin3[0]**2 + yin3[2]**2))/(2 *((-xin3[0] + xin3[2])* (-yin3[0] + yin3[1]) - (-xin3[0] + xin3[1])* (-yin3[0] + yin3[2])))
        # x0 initial guess
    par0[1] = (xin3[0]**2 - xin3[1]**2 - 2* par0[0]* yin3[0] + yin3[0]**2 + 2* par0[0] *yin3[1] - yin3[1]**2)/(2* (xin3[0] - xin3[1]))
        # r^2 initial guess
    par0[2] = (-par0[1] + xin3[0])**2 + (-par0[0] + yin3[0])**2
    
    # Step Five we want to create the various functions to pass into scipy adapted from__________________________________________________ https://docs.scipy.org/doc/scipy/reference/tutorial/optimize.html________________________________________________________________________
    #__________________________________________________________________________________________________________________________________
    
    # we fit with to a semi circle with offset center at x0,y0 and a radius equal to sqrt(r2) (calculating r2 instead of r is vestigial from brent)
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
    res = least_squares(fun, par0, jac=jac, method='lm', args=(ImpedanceRealAvg, ImpedanceImagAvg), verbose=0) # this does the actual fitting
    pcov = [' ']*(len(res.x)) 
    cond = 1/(res.x[1]+(res.x[2]-res.x[0]**2)**.5)
    dcond = ' '
    
    # Step Six, format everything to do the outputting_________________________________________________________________________________
    #__________________________________________________________________________________________________________________________________
    # First we format to output the results to the Results.txt file
    outRes = [' ']*(len(res.x)+len(pcov)+5)
    outRes[0] = fname.rsplit('\\',1)[1]
    outRes[1:6:2] = [str(i) for i in res.x]
    outRes[2:7:2] = [str(i) for i in pcov]
    outRes[7] = str(cond)
    outRes[8] = str(dcond)
    outRes.extend(fname.rsplit('\\',1)[1].split('.',1)[0].split())
    
    with open(pathResults, "a") as results:
        results.write(" \t ".join(outRes)+'\n')
        
    #  then we output the modified input file (with averages calculated) into the Output folder
    outArr = np.empty((len(freqOmegaAvg),20))
    outArr[:,0] = avgedinput[:,avdFreqA]
    outArr[:,1] = avgedinput[:,avdFreqS]
    outArr[:,2] = avgedinput[:,avdCapPFA]
    outArr[:,3] = avgedinput[:,avdCapPFS]
    outArr[:,4] = avgedinput[:,avdLossA]
    outArr[:,5] = avgedinput[:,avdLossS]
    outArr[:,6] = avgedinput[:,avdVoltA]
    outArr[:,7] = avgedinput[:,avdVoltS]
    outArr[:,8] = avgedinput[:,avdTimeA]
    outArr[:,9] = avgedinput[:,avdTimeS]
    outArr[:,10] = freqOmegaAvg
    outArr[:,11] = capFarAvg
    outArr[:,12] = resistAvg
    outArr[:,13] = resistStd
    outArr[:,14] = ImpedanceRealAvg
    outArr[:,15] = ImpedanceRealStd
    outArr[:,16] = ImpedanceImagAvg
    outArr[:,17] = ImpedanceImagStd
    outArr[:,18] = ImpedanceMagAvg
    outArr[:,19] = ImpedanceMagStd
    
    header = ' Frequency Ave \t Frequency Std \t Capacitance Ave \t Capacitance Std \t Loss Ave \t Loss Std \t Voltage Ave \t Voltage Std \t Time Ave \t Time Std \t Frequency Ave \t Capacitance Ave \t Resistance Ave \t Resistance Std \t ReZ Ave \t ReZ Std \t ImZ Ave \t ImZ Std \t MagZ Ave \t Magz Std \n  Hz \t Hz \t pF \t pF \t tand \t tand \t V \t V \t s \t s \t rad s-1 \t F \t Ohm \t Ohm \t Ohm \t Ohm \t Ohm \t Ohm \t Ohm \t Ohm '

    np.savetxt(fOutname, outArr,delimiter='\t',header=header)

    
    # and thats it!
    
    
    
     
    
# in case you want to graph these, uncomment this
#import matplotlib.pyplot as plt
#u_test1 = np.linspace(par0[1]-par0[2]**0.5, par0[1]+par0[2]**0.5)
#y_test1 = model(par0, u_test1)
#u_test = np.linspace(res.x[1]-res.x[2]**0.5, res.x[1]+res.x[2]**0.5)
#y_test = model(res.x, u_test)
#plt.plot(ImpedanceRealAvg, ImpedanceImagAvg, 'o', markersize=4, label='data')
#plt.plot(u_test1, y_test1, label='initial model')
#plt.plot(u_test, y_test, label='fitted model')
#plt.xlabel("RealZ")
#plt.ylabel("ImagZ")
#plt.legend()
#plt.show()



