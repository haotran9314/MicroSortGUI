License Notice:

Two custom libraries from online are used: 
UUTrack Library, developed by aquilesC. The library used for camera frame acquisition and control
The code used are in the cameraModel folder
Source Code can be found at: https://github.com/uetke/UUTrack
highResolution delay, developed by ElectricRCAircraftGUy. The library is used for getting high resolution delay for testing maximum throughput
The code used is in the highResolutionSleep.py file
Source Code can be found at: https://github.com/ElectricRCAircraftGuy/eRCaGuy_PyTime
All credits for the two libraries goes to the developer. 

Icons used in the graphical user interface were taken from flaticon
All icons used can be found in the resourcesFile/Icon
Source: https://www.flaticon.com/
All credits for the icons goes to the developer.

To get started with developing the UI:

1. Download the QtDesigner App
2. Open the GUI.ui in resourcesFile folder using QtDesigner
3. Drag and drop the desired the ui elements to the window
4. Select Form --> Preview to view the designed GUI
5. Save the file when finish editting


--------------------------------------------------------
To start with the programming of the GUI
1. Run the runMe.bat file to install all the dependencies
2. Run the uiGenerate.py file in the resourcesFile to update with the most recent change in the Dashboard.ui file 
   *Important Note: 
   Add the below code after every uiGenerate run under the line  *****self.chipViewer.setObjectName("chipViewer")********* if not the chip viewer will not work!!!
        self.layout1 = QtWidgets.QHBoxLayout()
        self.layout2 = QtWidgets.QVBoxLayout()
        self.chipViewerPage.setLayout(self.layout1)
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setMaximumSize(300,166667)
        self.listWidget.setDragEnabled(True)
        QtWidgets.QListWidgetItem("Electrode", self.listWidget)
        self.elecTrodeLabel = QtWidgets.QLabel("Enter Electrode Number")
        self.clearAllButton = QtWidgets.QPushButton("Clear All")
        self.loadButton = QtWidgets.QPushButton("Load")
        self.saveAsButton = QtWidgets.QPushButton("Save As")
        self.electroNumberInput = QtWidgets.QLineEdit()
        self.electroNumberInput.setMaximumSize(300,100)
        self.layout2.addWidget(self.clearAllButton)
        self.layout2.addWidget(self.loadButton)
        self.layout2.addWidget(self.saveAsButton)
        self.layout2.addWidget(self.elecTrodeLabel)
        self.layout2.addWidget(self.electroNumberInput)
        self.layout2.addWidget(self.listWidget)
        self.layout1.addWidget(self.chipViewer)
        self.layout1.addLayout(self.layout2)
3. Run the app using main.py file

Let me know if you have any questions about the code. 