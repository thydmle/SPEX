# **SPEX**
This repository consists of a Python program and an Arduino sketch which were written to implement a control system for a diffraction grating spectrometer, as a part of my Senior capstone project. \
Repository is under constant development. Please reach out to the owner prior to forking/cloning, as there might be ongoing problems that are under further development. 

## **Setup**
This code runs ideally in a virtual Python environment based on the first comment in the Python program.\
Should you like to run this on your native environment, make sure that you have all of the listed modules correctly installed prior to running the script. \

The required modules are: 
```
wxpython
numpy
serial
matplotlib
```
In order to run this control system, an Uno board must be first connected to the computer via its USB port. \
The SpexArduino.ino sketch must then be uploaded to the Uno board.\

Then, run the Python program from the command line as follows (make sure that you are in the correct directory):
```
$ python3 Spex.py
```
If the Python progam boots up correctly, it should display the following message on the command line:
```
Connected to UNO on port: /dev/cu.usbmodem14201
Uno SPEX program ready...
Done init dialog
```

