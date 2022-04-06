from numpy import delete
from customWidgets.customGraphicScene import *
from customWidgets.customGraphicButton import*
from consolePrint import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
import ymlFileReader

class chipViewPage():
    def __init__(self,ui_element,microcontrollerBoard):
        #Initialize the user interface element from the main window
        self.ui = ui_element
        #Store the microcontroller board object
        self.microcontrollerBoard = microcontrollerBoard
        #Initialize the custom graphic scene using the microcontroller object and the ui element list
        self.customGraphicScene = customGraphicScene(microcontrollerBoard,ui_element)
        #Set the scene for the graphic view
        self.ui.chipViewer.getScene(self.customGraphicScene)
        #Linked the button to the corresponding functions
        self.ui.clearAllButton.clicked.connect(self.clearAllElectrodes)
        self.ui.saveAsButton.clicked.connect(self.saveAsConfig)
        self.ui.loadButton.clicked.connect(self.loadConfig)
    #Get all the electrode items and append it on the list
    def getElectrodes(self):
        electrodesList = []
        for item in self.customGraphicScene.items():
            electrodesList.append({'id': item.name,'pulseTime':item.pulseTime, 'x_pos': item.x(), 'y_pos': item.y()})
        return electrodesList
    # Iterate through items of the scene and remove all electrodes 
    def clearAllElectrodes(self):
        self.customGraphicScene.clearAllElectrodes()
        self.ui.statusbar.showMessage("Chip Viewer Cleared ",5000)

    # Populate the scene with electrodes
    def loadConfig(self):
        self.clearAllElectrodes()
        try:
            configFileName = QFileDialog.getOpenFileName(None,"Load Configuration File","", "Config Files (*.yml)")
            electrodesList = ymlFileReader.loadElectrode(self, configFileName[0])
            self.customGraphicScene.loadElectrodes(electrodesList=electrodesList)
            self.ui.statusbar.showMessage("Electrodes are loaded successfully ",5000)
        except Exception as e:
            consolePrintError(self,str(e))

    #Get all the electrodes items and save it to the configuration file
    def saveAsConfig(self):
        configFileName = QFileDialog.getSaveFileName(None,"Save Configuration File","", "Config Files (*.yml)")
        ymlFileReader.saveElectrodes(self, configFileName[0], self.getElectrodes())