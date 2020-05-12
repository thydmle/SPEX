#!/usr/bin/env python3
# Runs under MacOS, Python 3.7 + wxPython + numpy + matplotlib + PySerial
#
# ---------------------------------
# Spex in Python
# Use with Arduino Uno program SpexArduino.ino
#
# ----------------------------------

# Written by Thy Doan Mai Le
# March 10, 2019
# -----------------------------------

# Please consult the author, tle3@ithaca.edu or tl780@georgetown.edu, 
# prior to making any changes
# ----------------------------------
# UPDATES 5/11/2020:
# The string comparison in ConnectToUno, when the python program
#	verifies the SPEX string sent from the Arduino, is not working as it should
#	Despite the sent string being exactly SPEX, the python program is unable to 
#	recognize that string when the character array is converted into a string
#	However, when a single string was created in python, the string is accepted
#	Conclusion: the str(ch) needs further investigation for any unknown subtleties
#-----------------------------------
# UPDATES 5/12/2020:
# String conversion problem in ConnectToUno is fixed. Read inline comments for details.

import wx

if (wx.__version__[0] == '4'):
	import wx.adv
import os
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.figure as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy as np
import serial
import serial.tools.list_ports
import sys

####----------------------------------
####
# DEFAULT: channels from 4000 to 7000 angstrom, with 0.5 increase
# TO CHANGE: 
#	start = starting wavelength in angstrom
#	stop = stopping wavelength in angstrom

start = 4000
stop = 7000
xxx = np.linspace(start, stop, np.absolute(stop - start) + 1001)
yyy = np.zeros(start+1, np.int)
ser = serial.Serial()
chan = 0

class MainWindow(wx.Frame):
	def __init__(self, parent, title, position, size):
		global xxx, yyy, chan
		################### Connect to Arduino Uno
		self.unPort = 'None'
		self.unoMsg = 'No Uno Connected.'
		self.ConnectToUno()
	# Frame object is initiated here
		wx.Frame.__init__(self, parent, title=title, pos=position, size=size)
		# self.__close_callback = None
		self.Bind(wx.EVT_CLOSE, self.OnQuit)
	# when initialization dialog is done, print statement occurs
		print("Done init dialog\n")
	# Menu, graph panel and button panel are created, sequentially
		self.CreateMenu()
		self.CreateGraphPanel()
		self.CreateButtonPanel()
		frame_box = wx.BoxSizer(wx.VERTICAL)
		frame_box.Add(self.panel, flag=wx.EXPAND, proportion=1, border=10)
		frame_box.Add(self.buttonpanel, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)
		self.SetSizer(frame_box)
		self.Show()
		self.Layout()

	# --------------------------------------------------------------------------
	def CreateMenu(self):
		menubar = wx.MenuBar()
		filemenu = wx.Menu()
		self.abouItem = filemenu.Append(wx.ID_ABOUT, '&About xSPX')
		filemenu.AppendSeparator()
		self.startItem = filemenu.Append(-1, "Start...\tCtrl+1")
		self.stopItem = filemenu.Append(-1, "Stop...\tCtrl+2")
		self.saveItem = filemenu.Append(-1, "Save...\tCtrl+3")
		self.quitItem = filemenu.Append(-1, "Quit...\tCtrl+4")
		menubar.Append(filemenu, "&File")
		self.SetMenuBar(menubar)
		self.Bind(wx.EVT_MENU, self.OnStart, self.startItem)
		self.Bind(wx.EVT_MENU, self.OnStop, self.stopItem)
		self.Bind(wx.EVT_MENU, self.OnQuit, self.quitItem)
		self.Bind(wx.EVT_MENU, self.OnSave, self.saveItem)
		self.stopItem.Enable(False)
		self.saveItem.Enable(False)

	# --------------------------------------------------------------------------
	def CreateGraphPanel(self):
	# In PySpex 2.0, this function differs from PySpex 1.0
	# The graph panel now has a sidebar where the user is able to input 
	#	parameters desired for their scan
		panel = wx.Panel(self)
		self.panel = panel
		self.figure = plt.Figure()
		self.axis = self.figure.add_subplot(1, 1, 1)
		self.figure.subplots_adjust(left=0.1, right=0.975, top=0.98, bottom=0.075)
		self.axis.set_yscale('linear')
		self.figurepanel = FigureCanvas(self.panel, -1, self.figure)
		self.draw() 
		#### Adding things to the graph panel
		graph_box = wx.BoxSizer(wx.HORIZONTAL)
		row1 = wx.BoxSizer(wx.VERTICAL)
		#### The start and stop textboxes
		self.startwavelength = wx.StaticText(self, label="Start Wavelength")
		self.startint = wx.TextCtrl(self)
		self.stopwavelength = wx.StaticText(self, label="Stop Wavelength")
		self.stopint = wx.TextCtrl(self)
		row1.Add(self.startwavelength, 0, wx.CENTER|wx.ALL, 5)
		row1.Add(self.startint, 0, wx.CENTER|wx.ALL, 5)
		row1.Add(self.stopwavelength, 0, wx.CENTER|wx.ALL,5)
		row1.Add(self.stopint,0,wx.CENTER|wx.ALL,5)
		#### The enter button
		self.enterbutton = wx.Button(panel, label="Enter", size=(90,30))
		self.enterbutton.Bind(wx.EVT_BUTTON, self.OnEnter)
		row1.Add(self.enterbutton, 0, wx.CENTER, 5)	 
		graph_box.Add(row1)
		#### Wrapping up the creation of the sidebar + graph panel
		self.graph_box = graph_box
		graph_box.Add(self.figurepanel, flag=wx.EXPAND, proportion=1)
		self.panel.SetSizer(graph_box)

	# --------------------------------------------------------------------------
	def CreateButtonPanel(self):
		buttonpanel = wx.Panel(self)
		self.startbutton = wx.Button(buttonpanel, label='Start', size=(90, 30))
		self.stopbutton = wx.Button(buttonpanel, label='Stop', size=(90, 30))
		self.savebutton = wx.Button(buttonpanel, label='Save', size=(90, 30))
		self.quitbutton = wx.Button(buttonpanel, label='Quit', size=(110, 30))
		self.startbutton.Bind(wx.EVT_BUTTON, self.OnStart)
		self.stopbutton.Bind(wx.EVT_BUTTON, self.OnStop)
		self.savebutton.Bind(wx.EVT_BUTTON, self.OnSave)
		self.quitbutton.Bind(wx.EVT_BUTTON, self.OnQuit)
		self.ts = wx.StaticText(buttonpanel, -1, "Connected to UNO on port: " + self.unoPort, \
								size=(-1, 30), style=wx.ALIGN_CENTER)
		self.buttonbox = wx.BoxSizer(wx.HORIZONTAL)
		# What is buttonbox?
		self.buttonbox.Add(self.ts, flag=wx.EXPAND | wx.ALL, proportion=4)
		self.buttonbox.AddStretchSpacer(prop=100)
		self.buttonbox.Add(self.startbutton)
		self.buttonbox.Add(self.stopbutton)
		self.buttonbox.Add(self.savebutton)
		self.buttonbox.Add(self.quitbutton)
		self.buttonpanel = buttonpanel
		self.buttonpanel.SetSizer(self.buttonbox)
		self.Layout()
		self.startbutton.Enable()
		self.stopbutton.Disable()
		self.savebutton.Disable()
		self.quitbutton.Enable()

	####----------------------------------------------------------------------
	####
	#### EVENTS to handle:
	####--------------------------------------------------------------------
	def OnEnter(self, event):
		global start, stop, xxx, yyy
		start = int(self.startint.GetValue())
		stop = int(self.stopint.GetValue())
		xxx = np.linspace(start, stop, np.absolute(stop - start) + 1)
		yyy = np.zeros(np.absolute(stop - start) + 1, np.int)
		self.draw()

	####-------------------------------------------------------------------------
	def OnStart(self, event):
		global xxx, yyy, remains
		self.Bind(wx.EVT_IDLE, self.OnIdle)
		print('Data collection started...')
		self.draw()
		self.startbutton.Disable()
		self.stopbutton.Enable()
		self.savebutton.Disable()
		self.quitbutton.Disable()
		self.startItem.Enable(False)
		self.stopItem.Enable(True)
		self.saveItem.Enable(False)
		self.quitItem.Enable(False)
		self.ser.write('g'.encode(encoding='UTF-8'))
		self.remains = ''

	####------------------------------------------------------------------
	def OnStop(self, event):
		self.ser.write('s'.encode(encoding='UTF-8'))
		print('Data Collection stopped.')
		self.Unbind(wx.EVT_IDLE)
		self.startbutton.Enable()
		self.stopbutton.Disable()
		self.savebutton.Enable()
		self.quitbutton.Enable()
		self.startItem.Enable(True)
		self.stopItem.Enable(False)
		self.saveItem.Enable(True)
		self.quitItem.Enable(True)
		self.ClearBuffer()
		self.draw()

	####--------------------------------------
	def OnSave(self, event):
		self.Unbind(wx.EVT_IDLE)
		self.startbutton.Enable()
		self.stopbutton.Disable()
		self.savebutton.Enable()
		self.quitbutton.Enable()
		self.startItem.Enable(True)
		self.stopItem.Enable(False)
		self.saveItem.Enable(True)
		self.quitItem.Enable(True)
		dlg = wx.FileDialog(self, "Save data as...", \
							os.getcwd(), "", "*.txt", \
							style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		result = dlg.ShowModal()
		inFile = dlg.GetPath()
		dlg.Destroy()
		if result == wx.ID_OK:	# Save button was pressed
			print("Saving data to" + String(inFile))
			np.savetxt(inFile, yyy, fmt='%d')
			self.savebutton.Disable()
			self.saveItem.Enable(False)
		# self.Close(True)
		# self.Destroy()
		elif result == wx.ID_CANCEL:  # Cancel button was pressed
			print("Save data cancelled.")

	####--------------------------------------------------------------------------
	def OnIdle(self, event):
		global yyy, xxx, chan
		# print "Entered Idle\n"
		if self.ser.inWaiting() > 0:
			# print "Entered if\n"
			ins = self.ser.read(self.ser.inWaiting())
			data = (self.remains + ins).split()
			# check remains carried properly:
			# print "(" + self.remains+ ")" + ins.split()[0] + "=" + data[0]+"," +data[1]
			if (ins[-1] != "\n"):
				self.remains = data.pop()
			else:
				self.remains = ""
			# print len(data)
			for d in data:
				yyy[chan] = int(d)
				chan += 1
			# print yyy[chan] + "\n"
			self.draw()
		event.RequestMore(True)

	#-----------------------------------------------
	def draw(self):
		global start, stop
		self.axis.clear()
		self.axis.set_xlabel('Wavelength in Angstrom')
		self.axis.set_ylabel('Voltage')
		self.axis.set_xlim(start, stop)
		self.axis.set_xticks(np.arange(start, stop, 500))
		self.axis.grid(color='lightgrey')
		self.axis.set_yticks(np.arange(0, 1023, 100))
		self.axis.set_ylim(0, 1024)
		self.theline = self.axis.plot(xxx, yyy, color='blue', drawstyle='steps-mid')
		self.figurepanel.draw()

	# ---------------------------------------------------
	def OnAboutBox(self, event):
		if wx.__version__[0] == '4':
			info = wx.adv.AboutDialogInfo()
		else:
			info = wx.AboutDialogInfo()
		info.SetName('xSpex')
		info.SetVersion('0.9.8', longVersion='0.9 Alpha')
		info.SetDescription('Spex')
		info.AddDeveloper('Thy Doan Mai Le\nMarch, 2019')
		if wx.__version__[0] == '4':
			wx.adv.AboutBox(info)
		else:
			wx.AboutBox(info)

	# ----------------------------------------------------
	def OnQuit(self, event):
		self.Unbind(wx.EVT_IDLE)
		self.ser.write('s'.encode(encoding='UTF-8'))	 # stop Uno data stream
		# print "Quit Event"
		print("Quitting...")
		self.ser.close()
		self.Destroy()

	####-----------------------------------------------------
	####
	#### Comm with Uno
	####
	####--------------------------------------------------
	def ConnectToUno(self):
		UnoPID = 0x0043
		noUno = True
		self.unoPort = 'None'
		for pinfo in serial.tools.list_ports.comports():
			if (pinfo.pid == UnoPID):
				Device = 'Uno'
				self.unoPort = pinfo.device
				noUno = False
				break
		if (noUno):
			wx.MessageBox( \
				'Unable to find an Arduino Uno. Is it connected?', \
				'Error:', wx.OK | wx.ICON_EXCLAMATION)	# ICON_ERROR)
			sys.exit('Error: No Arduino Uno found!')
		while True:
			# try catch block
			try:
				self.ser = serial.Serial(port=self.unoPort, baudrate=250000, \
										 timeout=2)
				break
			except serial.SerialException:
				print("Waiting for USB port...");
				wx.MessageBox( \
					'Waiting for USB port...\n' + \
					'Is the Serial Monitor open on the Arduino app?', \
					'WARNING:', wx.OK | wx.ICON_NONE)
		self.unoMsg = "Connected to UNO on port: " + self.unoPort
		# self.unoPort = unoPort
		print(self.unoMsg)
		self.ser.dtr = False
		self.ser.reset_input_buffer()
		self.ser.dtr = True
		self.ClearBuffer()
		ch = self.ser.read(10)[0:4]
		# serial read returns bytes
		# spex = "SPEX"
		# problem 5/11/2020: for some reason the comparison is not passing
		# 		  5/12/2020: PROBLEM IS FIXED
		#		             new implementation of the str() function requires
		#					 encoding and errors provided for byte data, which
		#					 is what ch is. 
		# ------ ISSUE CLOSED -------------
		if (str(ch, encoding='utf-8', errors='strict') == "SPEX"):
			print("Uno SPEX program ready...")
		else:
			print('Uno SPEX program not found')
			wx.MessageBox('Uno SPEX program not found\n' + \
						  'Reload the program and try ', \
						  'WARNING:', wx.CANCEL | wx.ICON_ERROR)
			sys.exit('Uno SPEX program not found!')
		self.ser.write('s'.encode(encoding='UTF-8'))

	# ----------------------------------------------------------
	def ClearBuffer(self):
		self.ser.reset_input_buffer()
		# clear the data buffer:
		buf = self.ser.inWaiting()
		while (buf > 0):
			ch = self.ser.read(buf)
			buf = self.ser.inWaiting()
####-------------------------------------------------------
####------------------------------------------------------
#### Main program
####
####--------------------------------------------------------------
app = wx.App(False)
w, h = wx.GetDisplaySize()
frame = MainWindow(None, "SPEX", (10, 25), (0.95 * w, 0.85 * h))
app.MainLoop()
