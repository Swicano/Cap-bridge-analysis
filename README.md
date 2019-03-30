# Capacitance Bridge Output Analysis

This program is designed to take the output of a specific LabView file, which gathers data from an Andeen Hagerling 2700a Capacitance Bridge, and transform that data in a way that is convenient for our uses.

This program scans the Input Folder for new .txt files that were output from the capacitance bridge, and fits a semi circle to the data held therein as described below. The fit parameters after fitting are appended to the file Results.txt, and a modified version of the input is output into the Output Folder with 'OUTPUT' prepended to the file name.

### Fitting behavior

The input file has data in the format of frequency, capacitance and loss from which the complex Impedance, Z(w), is calculated. Z is then fit by the formula (Im(Z(w)-Im(Z0))^2 + (Re(Z(w)-Re(Z0))^2 = R^2  to get Z0 and R^2, which are output to a new file

### Input File Format
The input file must be tab separated and end in .txt. The first two rows are considered header information and discarded. 

Example file layout:

| | | | | |
| --- | --- | --- | --- | --- |
|Freq. | Cap. | Loss | Voltage | Time|
|Hz | pF | tan d | V |  |
|50.000 | 7.4598 | 1.02737 | 0.100 | 02-09-2019-14:13:27|
|50.000 | 7.4651 | 1.03016 | 0.100 | 02-09-2019-14:13:49|
|50.000 | 7.4697 | 1.03282 | 0.100 | 02-09-2019-14:14:10|
|... | ... | ... | ... | ...|

### Results.txt file format

The Results.txt file with be of the format 

| |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | |  | 
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
|FileName | fitted y0 | fitted y0_err | fitted x0 | fitted x0_err | fitted r2 | fitted r2_err | Conductance | Conductance_error | |  |  filesep1 | filesep2 | filesep3 | filesep4 | filesep5 | filesep6 | filesep7 | filesep8 | filesep9 | filesep10 | filesep11 | filesep12 | filesep13 | filesep14 |  	 
|string | Ohms | Ohms | Ohms | Ohms | Ohms^2 | Ohms^2 | S | S |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
|2700A S1 NtN1 50 After silane treatment 1 Bare Electrode R1 120oC Heating 02-09-2019.txt | -57987664.600195 |  | 256142439.32919598 |  | 6.948414816611978e+16 |  | 1.9482406819023095e-09 | | |  | 2700A | S1 | NtN1 | 50 | After | silane | treatment | 1 | Bare | Electrode | R1 | 120oC | Heating | 02-09-2019 | 
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | 

### Output file format
The output file will be a tab separated txt file with the format below

| |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|Frequency Ave | Frequency Std | Capacitance Ave | Capacitance Std | Loss Ave | Loss Std | Voltage Ave | Voltage Std | Time Ave | Time Std | Frequency Ave | Capacitance Ave | Resistance Ave | Resistance Std | ReZ Ave | ReZ Std | ImZ Ave | ImZ Std | MagZ Ave | MagZ Std |
| Hz | Hz | pF | pF | tan(d) | tan(d) | V | V | s | s | rad s-1 | F | Ohm | Ohm | Ohm | Ohm | Ohm | Ohm | Ohm | Ohm |
 | 3.2000e+03 | 0.0000e+00 | 4.4841e+00 | 3.3166e-05 | 1.3635e-01 | 4.1231e-06 | 1.0000e-01 | 0.0000e+00 | 1.5497e+09 | 8.2915e-01 | 2.0106e+04 | 4.4841e-12 | 8.1341e+07 | 2.5320e+03 | 1.4847e+06 | 4.9478e+01 | 1.0889e+07 | 7.8578e+01 | 1.0989e+07 | 1.1037e+01 | 
 | ...| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
