#	The function of this program is to take as input file the files produced by the labview program designed to interface with the AH2700 capacitance bridge (tab separated, row one and two as header and unit, respectively, and 5 columns ('frequency','capacitance', 'loss', 'voltage', and 'time') and applies a fitting function to the data
#   The resulting fit data is output into a new file (tab separated) of format TBD

import argparse
import numpy as np
import datetime

# Step One: find an input file name somehow____________________________________________________________________________________________

# The File name hardcoded (for testing)
fname = r"C:\Users\gfirest\Documents\GitHub\Cap-bridge-analysis\testdata\2700A S2 NtN9 50 Bare Electrode R1 100oC Heating 03-18-2019.txt"

# Step Two: read the file into a numpy array___________________________________________________________________________________________

# quite possibly the worst converter function ever made. decodes the timestamp format from labview to unix time in seconds
# assumes the exact format '03-18-2019-13:34:11' with that extra dash
convertr = lambda s: float(datetime.datetime(int(s.decode().split('-')[2]),int(s.decode().split('-')[0]),int(s.decode().split('-')[1]),int(s.decode().split('-')[3].split(':')[0]),int(s.decode().split('-')[3].split(':')[1]),int(s.decode().split('-')[3].split(':')[2])).timestamp())

#whomp i already found a better way
convertp = lambda s: float(datetime.datetime.strptime( s.decode(), "%m-%d-%Y-%H:%M:%S").timestamp())

inputarray = numpy.loadtxt(fname, skiprows=2, converters={4 : convertp}) # first two rows are headers and never change, so we skip them.

# Step Three: ''massage'' the data as Brent calls it___________________________________________________________________________________
#       in this step we take the input data and potentially average all the input data at each frequency

# avgedinput will give an array twice as wide of [avg] concat to [std] 
avgedinput = np.vstack([np.concatenate([inputarray[inputarray[:,0] == freq].mean(0),inputarray[inputarray[:,0] == freq].std(0)],0) for freq in freqsset])


freqomega = inputarray[:,0]*2*np.pi
picocap = inputarray[:,1]*10**(-12)




