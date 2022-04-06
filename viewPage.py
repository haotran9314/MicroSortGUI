from ctypes import sizeof
import time, cv2,datetime,os,csv,ymlFileReader,os
import numpy as np
import pyqtgraph as pg
from multiprocessing import Queue,Event,Process
from getFlameData import* 
from threadWorkers import queueWorker
from PyQt5 import QtGui,QtCore
from PyQt5.QtGui import QFont,QMovie,QKeySequence
from PyQt5.QtWidgets import QFileDialog,QComboBox,QToolButton,QWidget,QSizePolicy,QCheckBox
from seabreeze.spectrometers import list_devices
from PyQt5.QtCore import QProcess,QThread
from customWidgets import customLRI as clri
from customWidgets.recordButtonEffect import *
from consolePrint import *
from sortingProcess import*

np.set_printoptions(threshold=np.inf)
class viewPage():
	def __init__(self,ui_element,microcontrollerBoard):
		""" Set up view page graphical user interface elements and its functionality 
		\n Parameters \n ui_element: main window user interface elements \n microcontrollerBoard: microcontroller object class
		"""
		self.ui = ui_element
		self.microcontrollerBoard = microcontrollerBoard
		self.toolbarSetUp()
		#Set up the inputbox so it only allows double
		self.setUpInputBox()
		#Set up the Spectrometer View
		self.setUpGraphicalView()
		self.loadSpectrometerDevices()
		#Init a variable to init Qprocess later
		self.p = None
		self.childPID = None
		#Initiate the worker function (the worker will be working in the thread)
		self.queueWorkerThread = None #--> Will actively listening to the queue when result from other process is available
		self.queue = Queue() #--> Initialize the Queue
		self.plotCompletedEvent = Event() #--> set plot completed event
		self.sendDataToPlotEvent = Event() #--> set send data to plot event
		self.stopEvent = Event() #--> set stop event
		#Initalize the writer for data recording of the spectrometer
		self.writer = None
		self.ui.spectrometerRecordButton.clicked.connect(self.recordData)


	#Create a new Process to get the Data (I'm using Qprocess instead of thread due to the large amount of data to analyze --> if we use thread it would constantly froze the UI)
	def start(self):
		""" Initializing a new process to get data from the spectrometer 
		"""
		#check if the process is initialized?
		if(self.p is None):
			#Disable the sorting button
			self.startSortingButton.setDisabled(True)
			self.ui.deviceConnectButton.setDisabled(True)
			#Close current process connection to the microcontroller board so other process can use(sorting process)
			self.microcontrollerBoard.closePort()
			#if process is not initialize, get all the parameters from the users
			self.frameRate = time.perf_counter()
			#store all user input parameters to a check list 
			checkList = [self.ui.integrationTime,self.ui.dropletTravelTime,
						 self.ui.wavelengthMin,self.ui.wavelengthMax,
						 self.ui.intensityMin,self.ui.intensityMax,
						 self.ui.pulseTime]
			#check all the required parameters are filled
			index = [idx for idx, element in enumerate(checkList) if element.text() == '']
			#if there is/are parameter/parameters missing
			if(len(index)>0):
				#Notify users the missing configuration parameters
				consolePrintError(self,"Missing Configuration Parameters")
				for i in index:
					#Get the list of the missing parameters and print it to the console window let the user where to fill
					checkList[i].externalTrigger()
					consolePrint(self,checkList[i].objectName())
				#notify user the missing parameters in the status bar
				self.ui.statusbar.showMessage("Please fill all the configuration parameters",5000)
				return
			#if all the parameters are correctly filled, initialize the spectrometer
			else:
				#if user chosed simulation, initialize simulation spectrometer
				if(self.ui.spectrometerOptionBox.currentIndex() == 0):
					self.mode = "s"
				#if user chosed real spectrometer device, initialize real spectrometer
				else:
					self.mode = "r"

				#Get and Convert integration value to microseconds
				integrationValue = int(self.ui.integrationTime.text())*1000*pow(1000,self.ui.integrationTimeUnit.currentIndex())
				#Get and Convert number of droplet per seconds value to microseconds
				numberOfDroplet = float(self.ui.numberOfDroplet.text())*(1000)/(pow(1000,self.ui.numberOfDropletUnit.currentIndex()))
				#update the region of interest on the spectrometer live data view
				self.regionBoxUpdate()
				
				#Try to create child process
				try:
					#Initializing the child process to execute the flameDataprocess function in flameDataProcess.py file
					self.p = Process(target=sortingProcess,args=[self.queue,self.plotCompletedEvent,self.sendDataToPlotEvent,self.stopEvent])
					#Start the process
					self.p.start()
					#Store the child process PID so it can be properly terminate later
					self.childPID = self.p.pid
				except Exception as e:
					#print the error to the console if failed to start the process
					consolePrintError(self,str(e))
				param = self.ui.wavelengthMin.text()+","+self.ui.wavelengthMax.text()+","+self.ui.intensityMin.text()+","+self.ui.intensityMax.text()+","+str(integrationValue)+","+self.mode+","+str(self.checkBox.isChecked())+","+self.ui.deviceList.currentText().split('(')[1].replace(")","")+","+str(numberOfDroplet)+","+str(self.sortingCheckBox.isChecked())+"\n"
				if(self.queueWorkerThread is None):
					#Initializing the parameter to be send to the flame data process
					#Initializing the queue worker (actively listening/communicating with other process to get/set data/parameter)
					self.readingQueue = queueWorker(self.queue,param,self.sendDataToPlotEvent)
					#Initializing the thread
					self.queueWorkerThread = QThread()
					#Send the worker to the thread
					self.readingQueue.moveToThread(self.queueWorkerThread)
					#When the thread started --> Execute the run function in the worker class
					self.queueWorkerThread.started.connect(self.readingQueue.run)
					#When the thread finished its job, kill the thread
					self.queueWorkerThread.finished.connect(self.queueWorkerThread.deleteLater)
					#When there is data available from the thread, send it to the GUI to plot
					self.readingQueue.data.connect(self.getData)
					#Start the queue worker thread
					self.queueWorkerThread.start()
					self.frameRate = time.perf_counter()
				else:
					#If the thread is initialized, just send the params for sorting to other process
					self.queue.put(param)
					#Start the ploting event
					self.plotCompletedEvent.set()
				# #update the status bar
				self.ui.statusbar.showMessage("Sorting Started",5000)

	def stop(self):
		""" Stop detection and data collection from the other process
		"""
		#if there is a valid process is running
		if(self.p is not None):
			#Enable the sorting button
			self.startSortingButton.setDisabled(False)
			self.ui.deviceConnectButton.setDisabled(False)
			
			#Trigger the stop event so other process can stop
			self.stopEvent.clear()
			self.plotCompletedEvent.set()
			#Wait the other process for 1 second to terminate
			self.p.join(1)
			#If it is still running (hanging)
			if(self.p.is_alive()):
				#Terminate the process
				self.p.terminate()
			#Set the process variable to None
			self.p = None
			#Clear the spectrometer graph
			self.ui.graphWidget.clear()
			#reconnect current process (GUI) to the microcontroller board
			self.microcontrollerBoard.open()

	def getData(self,data):
		""" Process the data from the spectrometer to be displayed on the spectrometer view
		"""
		#Get the data from other process and split it to two array (one is wavelength, one is intensity)
		spectrum = numpy.array_split(data,2)

		# out[0][out[0]<0] = 0
		# spectrum[1] = scipy.signal.savgol_filter(spectrum[1], 15, 2)

		#Update the plot with the data
		self.updatePlot(spectrum[0][:-1],spectrum[1])
		#Send a signal to other process notifying the ploting has completed --> send another packet of data to plot
		#Trigger the flag plot completed event
		self.plotCompletedEvent.set()
		
		#Record the data to CSV file if there is a CSV writer (meaning the record button is checked)
		if(not self.writer is None):
			#Get the current peak detection gate (region box) and store it as list format
			pdg = [self.ui.wavelengthMin.text(),self.ui.wavelengthMax.text(),self.ui.intensityMin.text(),self.ui.intensityMax.text()]
			#rounding the wavelength values to avoid overflow
			wl = list(np.around(np.array(spectrum[0][:-1]),2))
			#rounding the intensity values to avoid overflow
			it = list(np.around(np.array(spectrum[1]),2))
			#Write to the CSV file (wavelength array, intensity array, time, detection state)
			self.writer.writerow([wl,it,pdg,time.perf_counter()-self.startTime,spectrum[1][-1]])
			self.startTime = time.perf_counter()

	def regionBoxUpdate(self):
		""" Update the region of interest (grey box) on the spectrometer view
		"""
		#update the intensity gates
		self.region.setYBound(float(self.ui.intensityMin.text()),float(self.ui.intensityMax.text()))
		#update the wavelength gates
		self.region.setRegion((float(self.ui.wavelengthMin.text()),float(self.ui.wavelengthMax.text())))
		#update statusbar of the peak detection gate
		self.ui.statusbar.showMessage("Peak Detection Gates Updated Successfully",3000)

	def loadSpectrometerDevices(self):
		""" Get list of spectrometers and add it to the combo box
		"""
		#Get the list of the spectrometers
		self.devices = list_devices()
		#Set the first element in the combo box as Simulation Spectrometer
		self.ui.spectrometerOptionBox.addItems(["Simulation Spectrometer"])
		#If there is a list of spectrometer connected to the PC
		if(len(self.devices)>0):
			#Add all elements to the combo box for display
			self.ui.spectrometerOptionBox.addItems([str(self.devices)])

		
	#Set up the input box so it only alow double values by using QDouble Validator and set it to each input box
	def setUpInputBox(self):
		""" Alow input values for gate values to be double only
		"""
		#Set up double validator
		self.double = QtGui.QDoubleValidator()
		#Set up double validator for intensity gate 1
		self.ui.intensityMin.setValidator(self.double)
		#Set up double validator for wavelength gate 1
		self.ui.wavelengthMin.setValidator(self.double)
		#Set up double validator for intensity gate 2
		self.ui.intensityMax.setValidator(self.double)
		#Set up double validator for wavelength gate 2
		self.ui.wavelengthMax.setValidator(self.double)
		#Set up double validator for pump 1 input
		self.ui.pump1Input.setValidator(self.double)
		#Set up double validator for pump 2 input
		self.ui.pump2Input.setValidator(self.double)
		#Set up double validator for pump 3 input
		self.ui.pump3Input.setValidator(self.double)
		#Set up double validator for pump 4 input
		self.ui.pump4Input.setValidator(self.double)
		#Set up double validator for pump 5 input
		self.ui.pump5Input.setValidator(self.double)

	def setUpGraphicalView(self):
		""" Set up graphical view for the spectrometer -- I'm using pyqtgraph here instead of matplotlib due to its plotting speed for real time plot compared to matplotlib
		"""
		self.c = pg.colormap.getFromMatplotlib('rainbow')
		self.brush = self.c.getBrush(span=(300,800),orientation = 'horizontal')
		self.pen = self.c.getPen(span=(300,800),orientation = 'horizontal',width=2)
		self.bar = pg.ColorBarItem(values = (280,820),width = 20,orientation = 'horizontal',cmap = self.c,interactive=False)
		self.img = pg.ImageItem()
		self.bar.setImageItem(self.img, insert_in=self.ui.graphWidget.plotItem)
		self.ui.graphWidget.showGrid(x= True,y=True,alpha = 10)
		self.ui.graphWidget.setBackground('w')
		self.ui.graphWidget.setXRange(150, 1100, padding=0)
		self.ui.graphWidget.setYRange(-5, 20000, padding=0)
		self.range_ = self.ui.graphWidget.getViewBox().viewRange() 
		self.ui.graphWidget.getViewBox().setLimits(xMin=self.range_[0][0], xMax=self.range_[0][1],yMin=self.range_[1][0], yMax=self.range_[1][1])
		self.region = clri.customLinearRegionItem(values=(400,500),orientation='vertical',bounds=(300,800),brush=(155,155,155,80),xyBound=[30,50],pen = pg.mkPen(color=(255,255,255,0), width=0),movable= False)
		label_style = {'color': '#000', 'font-size': '10pt'}
		self.ui.graphWidget.setLabel(axis='left', text='Light Intensity (RFU)',**label_style)
		self.ui.graphWidget.setLabel(axis='bottom', text='Wavelength (nm)',**label_style)
		ay = self.ui.graphWidget.getAxis('left')
		ay.setTickFont(QFont("Times", 8))
		ay.setTextPen([0,0,0,255])
		ax = self.ui.graphWidget.getAxis('bottom')
		ax.setTickFont(QFont("Times", 8))
		ax.setTextPen([0,0,0,255])
		self.ui.graphWidget.clear()

	#Update the spectrometer plot view with the most recent data from the Qprocess
	def updatePlot(self,wavelength,intensity):
		""" Update the spectrometer view
		\nParameters\n Wavelength: wavelength array\n Intensity: intensity array\n Note: two arrays must have the same length
		"""
		#clear previous plot
		self.ui.graphWidget.clear()
		#Generate plotting curve
		curve = pg.PlotDataItem( x=wavelength, y=intensity,pen=self.pen)#, brush=self.brush, fillLevel=0.0 )
		#Add the plotting curve to pyqtgraph
		self.ui.graphWidget.addItem(curve)
		#Add the region box (gate) to pyqtgraph
		self.ui.graphWidget.addItem(self.region)
		#Set the frame rate
		self.ui.frameRate.setText(str(np.round(time.perf_counter()-self.frameRate,3)*1000) +"ms")
		self.frameRate = time.perf_counter()
	
	#When the camera view is closed show on the status bar
	def cameraProcessFinished(self):
		""" If the camera is closed shows the message on the status bar
		"""
		self.ui.statusbar.showMessage("Camera Closed",2000)
	#when camera view failed to start display the error in the console
	def cameraProcessError(self):
		""" If there are any error thrown from the camera process, display it in the console 
		"""
		error = bytes(self.pCamera.readAllStandardError()).decode()
		consolePrintError(self,str(error))
	#Starting the camera feature with a separate thread
	def startCamera(self):
		""" Start the camera view
		"""
		#Start the camera sub process
		self.pCamera = QProcess()
		#Read all the error from the sub process and display it on the GUI
		self.pCamera.readyReadStandardError.connect(self.cameraProcessError)
		#When camera finished, display to the status bar
		self.pCamera.finished.connect(self.cameraProcessFinished)
		#Start the camera process (run the startMonitor.py file)
		self.pCamera.start("python", ['startMonitor.py'])
		#Get the exposure time
		exposureTime = self.ui.exposureTimeInput.text()
		#Get the user input width for the camera window
		width = self.ui.cameraWidth.text()
		#Get the user input height for the camera window
		height = self.ui.cameraHeight.text()
		#construct the param to be send to the camera for set up
		param = "1," + exposureTime +","+ width +","+ height +"\n"
		#Send the parameters for set up to the camera process
		self.pCamera.write(param.encode())

	def recordData(self):
		""" Start the recording for the spectrometer data
		"""
		try:
			#If there record button is checked and the path to store data is valid
			if(self.ui.spectrometerRecordButton.isChecked() and self.pathSelectionBox.count()>0):
				#Generate new path 
				path = self.pathSelectionBox.currentText()+"//Spectrometer Data"
				if(not os.path.exists(path)):
					os.makedirs(path)
				#Create new file to store data\
				fileName = path+"//"+"SpectrometerDat_"+str(datetime.datetime.now()).replace(" ","_").split(".",1)[0].replace(":","꞉")+".csv"
				self.file = open(fileName,"x")
				#Create writer to write to newly created file
				self.writer = csv.writer(self.file)
				#Write the title for the data set
				self.writer.writerow(['Wavelength','Intensity','Peak Detection Gate [WWII]','Time(s)','Detection State'])
				self.startTime = time.perf_counter()
				#Display animation for the record button
				self.recordDataAnimation = recordButtonAnimation(self.ui.spectrometerRecordButton,self.ui.recordBackground)
				#Disable the folder selection path
				self.folderUI(False)

			elif(not self.ui.spectrometerRecordButton.isChecked() and self.writer != None):
				#Stop the animation for the record button
				self.recordDataAnimation.stopAnimation()
				self.recordDataAnimation = None
				#Set the writer variable to none
				self.writer = None
				#Close the file
				self.file.close()
				#Enable the folder selection path
				self.folderUI(True)
		except Exception as e:
			#Print error when failed to write file
			consolePrintError(self,str(e))

	def folderUI(self,state):
		""" Set the folder selection UI elements state
			Parameter: state (Boolean)
		"""
		#Set up the folder selection path UI state (disable/enable)
		self.pathSelectionBox.setEnabled(state)
		self.addFolderButton.setEnabled(state)
		self.deleteFolderButton.setEnabled(state)
	def toolbarSetUp(self):
		""" Set the user interface elements for the tool bar
		"""
		self.ui.toolBar.setIconSize(QtCore.QSize(25,25))
		#Create Folder Selection Box
		self.pathSelectionBox = QComboBox()
		self.pathSelectionBox.setGeometry(QtCore.QRect(80, 550, 531, 21))
		self.pathSelectionBox.setMinimumSize(QtCore.QSize(600,21))
		self.pathSelectionBox.setObjectName("pathSelectionBox")
		#Create button to add folder
		self.addFolderButton = QToolButton()
		self.addFolderButton.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.addFolderButton.setIcon(QtGui.QIcon(":/Icons/addFolder.png"))
		self.addFolderButton.setText("")
		self.addFolderButton.setObjectName("addFolderButton")
		self.addFolderButton.setToolTip('Browse for folder')
		#Create button to delete folder
		self.deleteFolderButton = QToolButton()
		self.deleteFolderButton.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.deleteFolderButton.setIcon(QtGui.QIcon(":/Icons/deleteFolder.png"))
		self.deleteFolderButton.setText("")
		self.deleteFolderButton.setObjectName("deleteFolderButton")
		self.deleteFolderButton.setToolTip('Delete current folder path from working directory')
		#Create start sorting button
		self.startSortingButton = QToolButton()
		self.startSortingButton.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.startSortingButton.setIcon(QtGui.QIcon(":/Icons/play.png"))
		self.startSortingButton.setText("")
		self.startSortingButton.setObjectName("startSortingButton")
		self.startSortingButton.setToolTip('Start sorting \n F5')
		self.startSortingButton.setShortcut(QKeySequence("F5"))
		
		#Create stop sorting button
		self.stopSortingButton = QToolButton()
		self.stopSortingButton.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.stopSortingButton.setIcon(QtGui.QIcon(":/Icons/pause.png"))
		self.stopSortingButton.setText("")
		self.stopSortingButton.setObjectName("stopSortingButton")
		self.stopSortingButton.setToolTip('Stop sorting\n F6')
		self.stopSortingButton.setShortcut(QKeySequence("F6"))
		#Create reload connection button
		self.reloadButton = QToolButton()
		self.reloadButton.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.reloadButton.setIcon(QtGui.QIcon(":/Icons/reuse.png"))
		self.reloadButton.setText("")
		self.reloadButton.setObjectName("reloadButton")
		self.reloadButton.setToolTip('Reload connection \n Ctrl+E')
		self.reloadButton.setShortcut(QKeySequence("Ctrl+E"))
		#Create background check box
		self.checkBox = QCheckBox()
		self.checkBox.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.checkBox.setText("Background Substraction")
		self.checkBox.setObjectName("checkBox")
		self.checkBox.setToolTip('Background substraction')
		#Create sorting check box
		self.sortingCheckBox = QCheckBox()
		self.sortingCheckBox.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.sortingCheckBox.setText("Binary Sorting")
		self.sortingCheckBox.setObjectName("sorting CheckBox")
		self.sortingCheckBox.setToolTip('Binary Sorting')
		#Creat load config button
		self.loadconfigButton = QToolButton()
		self.loadconfigButton.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.loadconfigButton.setIcon(QtGui.QIcon(":/Icons/loadConfig.png"))
		self.loadconfigButton.setText("")
		self.loadconfigButton.setObjectName("loadConfigButton")
		self.loadconfigButton.setToolTip('Load configuration file \n Ctrl+O')
		self.loadconfigButton.setShortcut(QKeySequence("Ctrl+O"))
		#Create save config button
		self.saveConfigButton = QToolButton()
		self.saveConfigButton.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.saveConfigButton.setIcon(QtGui.QIcon(":/Icons/diskette.png"))
		self.saveConfigButton.setText("")
		self.saveConfigButton.setObjectName("saveConfigButton")
		self.saveConfigButton.setToolTip('Save current configuration as')
		self.saveConfigButton.setShortcut(QKeySequence("Ctrl+Shift+S"))
		#Create view Camera button
		self.redockButton = QToolButton()
		self.redockButton.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.redockButton.setIcon(QtGui.QIcon(":/Icons/microscope.png"))
		self.redockButton.setText("")
		self.redockButton.setObjectName("redockButton")
		self.redockButton.setToolTip('Open the camera view\n Ctrl+Q')
		self.redockButton.setShortcut(QKeySequence("Ctrl+Q"))
		#Create spacer between widgets
		self.newspacer = QWidget()
		self.newspacer.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
		#Creat update config button
		self.defaultConfigurationUpdateButton = QToolButton()
		self.defaultConfigurationUpdateButton.setGeometry(QtCore.QRect(50, 550, 27, 22))
		self.defaultConfigurationUpdateButton.setIcon(QtGui.QIcon(":/Icons/gear.png"))
		self.defaultConfigurationUpdateButton.setText("")
		self.defaultConfigurationUpdateButton.setObjectName("defaultConfigurationUpdate")
		self.defaultConfigurationUpdateButton.setToolTip('Save as default configuration\n Ctrl+S')
		self.defaultConfigurationUpdateButton.setShortcut(QKeySequence("Ctrl+S"))
		#Add all the created widgets above to the toolbar
		self.ui.toolBar.addWidget(self.deleteFolderButton)
		self.ui.toolBar.addWidget(self.addFolderButton)
		self.ui.toolBar.addWidget(self.pathSelectionBox)
		self.ui.toolBar.addSeparator()
		self.ui.toolBar.addWidget(self.startSortingButton)
		self.ui.toolBar.addWidget(self.checkBox)
		self.ui.toolBar.addWidget(self.sortingCheckBox)
		self.ui.toolBar.addWidget(self.stopSortingButton)
		self.ui.toolBar.addWidget(self.reloadButton)
		self.ui.toolBar.addWidget(self.newspacer)
		self.ui.toolBar.addWidget(self.redockButton)
		self.ui.toolBar.addWidget(self.loadconfigButton)
		self.ui.toolBar.addWidget(self.saveConfigButton)
		self.ui.toolBar.addWidget(self.defaultConfigurationUpdateButton)
		#Add action to the created buttons in toolbar
		self.addFolderButton.clicked.connect(self.getDirectory) #--> get directory when add folder button is clicked
		self.deleteFolderButton.clicked.connect(self.removeDirectory) #--> remove directory when delete folder button is clicked
		self.loadconfigButton.clicked.connect(self.loadConfig) #--> load configuration file when load config button is clicked
		self.saveConfigButton.clicked.connect(self.saveConfig) #--> save current configuration file as when save config button is clicked
		self.defaultConfigurationUpdateButton.clicked.connect(self.updateDefaultConfig) #--> save the current configuration to the default configuration file
		self.startSortingButton.clicked.connect(self.start) #--> start the sorting sequence
		self.stopSortingButton.clicked.connect(self.stop) #--> stop the sorting sequence
		self.reloadButton.clicked.connect(self.reload) #--> all the connection (COM ports and spectrometer connection)
		self.redockButton.clicked.connect(self.startCamera) #--> Open camera view
	def reload(self):
		""" Reload all the connection for the system
		"""
		#Reload Serial Ports
		self.microcontrollerBoard.loadComports()
		#Reload Spectrometer Connections
		#clear current items in the spectrometer list
		self.ui.spectrometerOptionBox.clear()
		#reload the spectrometer combo box with new list
		self.loadSpectrometerDevices()
		self.ui.statusbar.showMessage("Reload Successfully",2000)
	def updateDefaultConfig(self):
		""" Update the default configuration
		"""
		#Update the default configuration (the defautl file is config.yml)
		ymlFileReader.saveConfig(self,'config.yml')
	def loadConfig(self):
		""" Load configuration file
		"""
		#Load the configuration file
		configFileName = QFileDialog.getOpenFileName(None,"Load Configuration File","", "Config Files (*.yml)")
		ymlFileReader.loadConfig(self,configFileName[0])
	def saveConfig(self):
		""" save current configuration file as
		"""
		#Save the current configuration as
		configFileName = QFileDialog.getSaveFileName(None,"Save Configuration File","", "Config Files (*.yml)")
		ymlFileReader.saveConfig(self,configFileName[0])
	def getDirectory(self):
		""" Add directory path for spectrometer data acquisition 
		"""
		#Open file dialog (folder browser)
		self.path = QFileDialog.getExistingDirectory()
		#If the path is valid
		if(self.path != ""):
			#Allow recording of spectrometer data
			self.ui.spectrometerRecordButton.setEnabled(True)
			#Get all paths in the current combo box 
			listOfPaths = [self.pathSelectionBox.itemText(i) for i in range(self.pathSelectionBox.count())]
			#If the item is not in the current list
			if(self.path not in listOfPaths):
				#Add the item to the list
				self.pathSelectionBox.addItem(self.path)
				#Update the index to the newest one
				self.pathSelectionBox.setCurrentIndex(self.pathSelectionBox.count()-1)
			self.ui.statusbar.showMessage("Directory Added",2000)
	def removeDirectory(self):
		""" Remove the path in the path selection combo box
		"""
		#If there is item in the combo box
		if(self.pathSelectionBox.count()>0):
			#Remove the item
			self.pathSelectionBox.removeItem(self.pathSelectionBox.currentIndex())
			self.ui.statusbar.showMessage("Directory Removed",2000)
			#If after delete the item, there is no more item in the combo box
			if(self.pathSelectionBox.count()<=0):
				#Disable the spectrometer record button
				self.ui.spectrometerRecordButton.setEnabled(False)
		else:
			self.ui.statusbar.showMessage("No Directories Found",2000)
	


