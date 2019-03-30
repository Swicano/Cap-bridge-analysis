# Capacitance Bridge Output Analysis

This program is designed to take the output of a specific LabView file, which gathers data from an Andeen Hagerling 2700a Capacitance Bridge, and transform that data in a way that is convenient for our uses.

This program scans the Input Folder for new .txt files that were output from the capacitance bridge, and fits a semi circle to the data held therein as described below. The fit parameters after fitting are appended to the file Results.txt, and a modified version of the input is output into the Output Folder with 'OUTPUT' prepended to the file name.

### Fitting behavior

The input file has data in the format of frequency, capacitance and loss from which the complex Impedance, Z(w), is calculated. Z is then fit by the formula (Im(Z(w)-Im(Z0))^2 + (Re(Z(w)-Re(Z0))^2 = R^2  to get Z0 and R^2, which are output to a new file

### Input File Format
The input file must be tab separated and end in .txt. The first two rows are considered header information and discarded. 

Example file layout:

| --- | --- | --- | --- | --- |
|Freq. | Cap. | Loss | Voltage | Time|
|Hz | pF | tan d | V |  |
|50.000 | 7.4598 | 1.02737 | 0.100 | 02-09-2019-14:13:27|
|50.000 | 7.4651 | 1.03016 | 0.100 | 02-09-2019-14:13:49|
|50.000 | 7.4697 | 1.03282 | 0.100 | 02-09-2019-14:14:10|
|... | ... | ... | ... | ...|

### Results.txt file format

The output file will 
