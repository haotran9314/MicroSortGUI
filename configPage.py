import sys, os,ymlFileReader,serial.tools.list_ports,serial
from consolePrint import consolePrint, consolePrintError
from threadWorkers import pumpWorker
from PyQt5 import QtGui, QtSerialPort,QtCore
from PyQt5.QtWidgets import QMainWindow,QHBoxLayout,QLabel, QLineEdit,QFileDialog,QToolButton,QComboBox
from PyQt5.QtCore import QSize,QObject,pyqtSignal,QThread,QRunnable,QThreadPool
from nemesysPump import *
from seabreeze.pyseabreeze import SeaBreezeAPI
from seabreeze.spectrometers import list_devices, Spectrometer
import seatease.spectrometers as s
import re

qmixsdk_dir =  "C:/QmixSDK" #path to Qmix SDK
sys.path.append(qmixsdk_dir + "/lib/python")
os.environ['PATH'] += os.pathsep + qmixsdk_dir
from qmixsdk import qmixbus
from qmixsdk import qmixpump
from qmixsdk import qmixvalve
from qmixsdk.qmixbus import UnitPrefix, TimeUnit

class configPage():
    def __init__(self,ui_elements,viewPageClass,microcontrollerBoard,sender):
        """ Set up view page graphical user interface elements and its functionality 
        \n Parameters \n ui_element: main window user interface elements \n viewPageClass: viewpage object class \n microcontrollerBoard: microcontroller object class
        """
        #Initialize list to store pump configuration parameters
        self.syringeDiameterInput = []
        self.syringeStrokeInput = []
        #Init class UI element from GUI file and View Page for easy access
        self.ui = ui_elements
        self.viewPage = viewPageClass
        self.microcontrollerBoard = microcontrollerBoard
        #Get the sender to object so we can identify which button is clicked later on
        self.sender = sender
        #Initialize pump parameter
        self.pump = nemesysPump()
        self.threadpool = QThreadPool()
        #Set up config file
        self.loadConfig()
        #Get the list of Spectrometer Devices connected to the PC using seabreeze API
        self.devices = list_devices()
        #If there are devices connected to the PC, create an instance of it, else display no connection to the status bar in the UI
        self.ui.stropeLampOption.currentIndexChanged.connect(self.handleUI)
        #Allow only number for the lineEdit input box
        self.numberOnly()
        #Set the input value to the spectrometer
        self.ui.deviceConnectButton.clicked.connect(self.microcontrollerConnect)
        self.pumpUISetup()
        #Set up the record button view
        if(self.viewPage.pathSelectionBox.currentText() == ''):
            self.ui.spectrometerRecordButton.setEnabled(False)
            self.ui.cameraRecord.setEnabled(False)
        self.ui.nemCheckBox.clicked.connect(self.nemEditAllowance)
        self.ui.nemAddPath.clicked.connect(self.addNEMDevicePropertyFolder)
        self.ui.nemDeletePath.clicked.connect(self.removeNEMDevicePropertyFolder)
        #when microcontroller send param button is clicked, send the parameters to the microcontroller for droplet configuration
        self.ui.sendParamButtom.clicked.connect(self.setParam)
        #Set up pump buttons to functions
        #when pump connect button is clicked --> set up the Nemesys pump with configuration parameters
        self.ui.pumpConnectButton.clicked.connect(self.pumpSetup)

        #Pump 3 sender test
        self.ui.pump1Start.clicked.connect(self.pumpFunctions)
        self.ui.pump2Start.clicked.connect(self.pumpFunctions)
        self.ui.pump3Start.clicked.connect(self.pumpFunctions)
        self.ui.pump4Start.clicked.connect(self.pumpFunctions)
        self.ui.pump5Start.clicked.connect(self.pumpFunctions)

        self.ui.pump1Stop.clicked.connect(self.pumpFunctions)
        self.ui.pump2Stop.clicked.connect(self.pumpFunctions)
        self.ui.pump3Stop.clicked.connect(self.pumpFunctions)
        self.ui.pump4Stop.clicked.connect(self.pumpFunctions)
        self.ui.pump5Stop.clicked.connect(self.pumpFunctions)

    def setParam(self):
        """ Send the parameters to the microcontroller 
		"""
        #Convert the parameters to the correct unit since the microcontroller will take microseconds
        dropletTravelTime = float(self.ui.dropletTravelTime.text())*1000*pow(1000,self.ui.dropletTravelTimeUnit.currentIndex())
        pulseTime = float(self.ui.pulseTime.text())*1000*pow(1000,self.ui.pulseTimeUnit.currentIndex())
        #Send the parameter to the microcontroller board object so it can send the parameters to the microcontroller
        self.microcontrollerBoard.writeParam(dropletTravelTime,pulseTime,self.ui.sortingElectrode.text())

    def handleUI(self):
        """ Handling user interface element for the strobe lamp option and period
		"""
        #If the strobe lamp option is valid
        if(not self.ui.stropeLampOption.currentIndex() == 0):
            #Enable user to set up the strobe lamp period input
            self.ui.strobeLampPeriod.setEnabled(True)
            self.ui.strobeLampPeriod.setStyleSheet("padding: 6px;"
            "border-top-left-radius :10px;"
            "border-top-right-radius : 10px; "
            "border-bottom-left-radius : 10px;"
            "border-bottom-right-radius : 10px;")
        else:
            #Disable the strobe lamp period input
            self.ui.strobeLampPeriod.setEnabled(False)
            self.ui.strobeLampPeriod.setStyleSheet("padding: 6px;"
            "border-top-left-radius :10px;"
            "border-top-right-radius : 10px; "
            "border-bottom-left-radius : 10px;"
            "border-bottom-right-radius : 10px;"
            "background-color: rgb(180, 180, 180);")
    def loadConfig(self):
        """ Load the default configuration file on start up
		"""
        #Load the default configuration file on start up
        ymlFileReader.loadConfig(self,'config.yml')
    #Allow user to only input number by putting a Integer Validator to each of the input box
    def numberOnly(self):
        """ Allow number only for all the parameters input
        """
        #Set up number validator
        self.onlyDouble = QtGui.QDoubleValidator()
        self.onlyInt = QtGui.QIntValidator()
        #Allow double for intergration time parameter
        self.ui.integrationTime.setValidator(self.onlyDouble)
        #Allow double for strobe lamp period parameter
        self.ui.strobeLampPeriod.setValidator(self.onlyDouble)
        #Allow double for droplet travel time parameter
        self.ui.dropletTravelTime.setValidator(self.onlyDouble)
        #Allow double for pulse time parameter
        self.ui.pulseTime.setValidator(self.onlyDouble)
        #Allow integer for sorting electrode parameter
        self.ui.sortingElectrode.setValidator(self.onlyInt)
        #Allow integer for number of droplet to sort parameter
        self.ui.numberOfDroplet.setValidator(self.onlyInt)
        #Allow integer for exposure time parameter
        self.ui.exposureTimeInput.setValidator(self.onlyInt)
        #Allow integer for camera width parameter
        self.ui.cameraWidth.setValidator(self.onlyInt)
        #Allow integer for camera height parameter
        self.ui.cameraHeight.setValidator(self.onlyInt)
    def microcontrollerConnect(self):
        """ Connect to the selected COM port and up parameters with the microcontroller
        """
        #Open the microcontrolelr board port
        self.microcontrollerBoard.open()
        #Get the parameters and convert it to microseconds
        dropletTravelTime = float(self.ui.dropletTravelTime.text())*1000*pow(1000,self.ui.dropletTravelTimeUnit.currentIndex())
        pulseTime = float(self.ui.pulseTime.text())*1000*pow(1000,self.ui.pulseTimeUnit.currentIndex())
        #Send the parameters to the microcontroller board
        self.microcontrollerBoard.writeParam(dropletTravelTime,pulseTime,self.ui.sortingElectrode.text())

    def pumpUISetup(self):
        """ Set up the user interface elements for the pump in the configuration page
        """
        #Syringe default value
        syringe_diam=[7.29,3.26,3.26,3.26,3.26]
        syringe_stroke=[59,40,40,40,40]
        self.ui.nemPropertyPath.addItem("C:/QmixSDK/config/Nemesys_5units_20190308")
        self.ui.pumpCalibrationInput.setPlaceholderText("3,7-8,all")

        #pumpcount = qmixpump.Pump.get_no_of_pumps()
        for i in range(5): #pumpcount: --> 5 can be replace to qmixpump.Pump.get_no_of_pumps() as it will dynamically load number of pumps we have
            #Set up font style
            font = QtGui.QFont()
            font.setPointSize(8)
            #Set up horizontal layout to set up the pump name, pump's syringe diameter and stroke
            horizontalLayout = QHBoxLayout()
            #Set up the pump name
            pumpName = QLabel(f"Pump {i+1}")
            pumpName.setMinimumSize(QSize(60, 30))
            pumpName.setMaximumSize(QSize(75, 30))
            pumpName.setFont(font)
            #If the default syringe diameter and stroke is avaialble, put into the qline edit, ow don't initialize anything
            if(i < len(syringe_diam)):
                syringeDiameter = QLineEdit(str(syringe_diam[i]))
                syringeStroke = QLineEdit(str(syringe_stroke[i]))
            else:
                syringeDiameter = QLineEdit()
                syringeStroke = QLineEdit()
            #Store the syringe diameter object instance so the value can be accesed later
            self.syringeDiameterInput.append(syringeDiameter)
            syringeDiameter.setMinimumSize(QSize(100, 30))
            syringeDiameter.setMaximumSize(QSize(100, 30))
            syringeDiameter.setStyleSheet("padding: 6px;\n"
"border-top-left-radius :10px;\n"
"border-top-right-radius : 10px; \n"
"border-bottom-left-radius : 10px;\n"
"border-bottom-right-radius : 10px;")
            #Store the syringe stroke object instance so the value can be accesed later
            self.syringeStrokeInput.append(syringeStroke)
            syringeStroke.setMinimumSize(QSize(100, 30))
            syringeStroke.setMaximumSize(QSize(100, 30))
            syringeStroke.setStyleSheet("padding: 6px;\n"
"border-top-left-radius :10px;\n"
"border-top-right-radius : 10px; \n"
"border-bottom-left-radius : 10px;\n"
"border-bottom-right-radius : 10px;")
            #Set up the status of the pump set up
            status = QLabel()
            status.setMinimumSize(QSize(60, 30))
            status.setMaximumSize(QSize(60, 30))
            horizontalLayout.addWidget(pumpName)
            horizontalLayout.addWidget(syringeDiameter)
            horizontalLayout.addWidget(syringeStroke)
            horizontalLayout.addWidget(status)
            self.ui.verticalLayout_3.addLayout(horizontalLayout)
            #Set up the nemesys configuration edit allowance. 
            self.nemEditAllowance()

    def nemEditAllowance(self):
        #if the advance set up button is check, allow for pump configuration edit
        if(not self.ui.nemCheckBox.isChecked()):
            self.ui.nemDeletePath.setEnabled(False)
            self.ui.nemAddPath.setEnabled(False)
            self.ui.nemPropertyPath.setEnabled(False)
            for i in range(len(self.syringeDiameterInput)):
                self.syringeDiameterInput[i].setEnabled(False)
                self.syringeStrokeInput[i].setEnabled(False)
        #if the advance set up button is not check, disable for pump configuration edit
        else:
            self.ui.nemDeletePath.setEnabled(True)
            self.ui.nemAddPath.setEnabled(True)
            self.ui.nemPropertyPath.setEnabled(True)
            for i in range(len(self.syringeDiameterInput)):
                self.syringeDiameterInput[i].setEnabled(True)
                self.syringeStrokeInput[i].setEnabled(True)
    def addNEMDevicePropertyFolder(self):
        #Add NEMESYS device property folder path
        self.path = QFileDialog.getExistingDirectory()
        if(self.path != ""):
            self.ui.nemPropertyPath.addItem(self.path)
            self.ui.statusbar.showMessage("NEMESYS Device Property Folder Added",2000)
    def removeNEMDevicePropertyFolder(self):
        #Remove NEMESYS device property folder path
        if(self.ui.nemPropertyPath.count()>0):
            self.ui.nemPropertyPath.removeItem(self.ui.pathSelectionBox.currentIndex())
            self.ui.statusbar.showMessage("NEMESYS Device Property Folder Removed",2000)
        else:
            self.ui.statusbar.showMessage("No Directories Found",2000)

    def pumpFunctions(self):
        sending_button = self.sender()
        function = ''.join([i for i in sending_button.objectName() if not i.isdigit()])
        pumpNumber = ''.join([i for i in sending_button.objectName() if i.isdigit()])

        attr = self.pump.__getattribute__(function)
        if("Start" in function):
            try:
                flowRate = float(self.ui.__getattribute__("pump"+pumpNumber+"Input").text())
            except:
                self.ui.__getattribute__("pump"+pumpNumber+"Input").externalTrigger()
                consolePrintError(self,"Pump Input for pump "+pumpNumber+" is invalid")
            pumpWorkers = pumpWorker(attr,int(pumpNumber),flowRate)
        elif("Stop" in function):
            pumpWorkers = pumpWorker(attr,int(pumpNumber))
        # pumpWorkers = pumpWorker(self.pump.testFunction,int(pumpNumber))
        pumpWorkers.signals.progress.connect(self.progressUpdate)
        pumpWorkers.signals.error.connect(self.errorHandler)
        self.threadpool.start(pumpWorkers)
    def errorHandler(self,error):
        consolePrintError(self,error)
    def progressUpdate(self,log):
        val = log.split(',')
        self.ui.__getattribute__("pump"+val[0]+"FlowRate").setText(val[1])
    def stopAllPump(self):
        stopAllPump = pumpWorker(self.pump.pumpStopAll)
        self.threadpool.start(stopAllPump)
        print("Stopping all pump")
    #Set up the pump worker and pass it to thread pool for concurent tasks execution
    def pumpSetup(self):
        diam = [i.text() for i in self.syringeDiameterInput]
        stroke = [i.text() for i in self.syringeStrokeInput]
        self.pumpWorker = pumpWorker(self.pump.pumpSetup,"C:/QmixSDK/config/Nemesys_5units_20190308",diam,stroke)
        self.pumpWorker.signals.finished.connect(lambda: print("Task is done"))
        self.pumpWorker.signals.progress.connect(self.pumpSetUpProgressLog)
        self.pumpWorker.signals.error.connect(self.errorHandler)
        self.threadpool.start(self.pumpWorker)

    def pumpSetUpProgressLog(self,log):
        self.ui.busStatus.setText(log)
        consolePrint(self,"Nemesys System: "+log)
    # #Generate first pump flow using the thread pool --> create the object and pass it to the thread pool
    # def pump1GenerateFlow(self):
    #     flowrate = float(self.ui.pump1Input.text())
    #     self.pumpWorker1 = pumpWorker(self.pump.pumpStart,2,flowrate)
    #     self.pumpWorker1.signals.progress.connect(self.pump1Progress)
    #     self.threadpool.start(self.pumpWorker1)
    # #Stop the first pump flow
    # def pump1StopFlow(self):
    #     stopPump = pumpWorker(self.pump.pumpStop,2)
    #     stopPump.signals.progress.connect(lambda: consolePrint(self,"Pump Stopped"))
    #     self.threadpool.start(stopPump)
    # #Generate second pump flow using the thread pool --> create the object and pass it to the thread pool
    # def pump2GenerateFlow(self):
    #     flowrate = float(self.ui.pump2Input.text())
    #     self.pumpWorker2 = pumpWorker(self.pump.pumpStart,3,flowrate)
    #     self.pumpWorker2.signals.progress.connect(self.pump2Progress)
    #     self.threadpool.start(self.pumpWorker2)
    # #Stop second pump flow
    # def pump2StopFlow(self):
    #     stopPump = pumpWorker(self.pump.pumpStop,3)
    #     stopPump.signals.progress.connect(lambda: consolePrint(self,"Pump Stopped"))
    #     self.threadpool.start(stopPump)
    # #Link the progress update signal to the Nemesys pump connection
    # def pumpSetUpProgressLog(self,log):
    #     self.ui.busStatus.setText(log)
    #     consolePrint(self,"Nemesys System: "+log)
    # #Link the progress update signal to the Nemesys pump 1 connection
    # def pump1Progress(self,result):
        
    #     self.ui.pump1FlowRate.setText(result)
    # #Link the progress update signal to the Nemesys pump 2 connection
    # def pump2Progress(self,result):
    #     self.ui.pump2FlowRate.setText(result)
    # def pump3Progress(self,result):
    #     self.ui.pump3FlowRate.setText(result)
    # def pump4Progress(self,result):
    #     self.ui.pump4FlowRate.setText(result)
    # def pump5Progress(self,result):
    #     self.ui.pump5FlowRate.setText(result)




