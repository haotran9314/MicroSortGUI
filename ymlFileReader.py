import yaml
from viewPage import viewPage
def loadConfig(self,filePath):
        #Open the yml file path, if fail shows the error on status bar
        try:
            with open(filePath,'r') as config:
                configValue = yaml.safe_load(config)
            self.ui.statusbar.showMessage("Configuration file load successfully",5000)
        except:
            self.ui.statusbar.showMessage("No configuration file found!",5000)
            return
        #Get all the configuration parameters stored in config file
        integrationTime = str(configValue['configPage']['flameConfiguration']['integrationTime'])
        integrationTimeUnit = (configValue['configPage']['flameConfiguration']['integrationTimeUnit'])
        triggerMode = (configValue['configPage']['flameConfiguration']['triggerMode'])
        strobeLamp = (configValue['configPage']['flameConfiguration']['strobeLamp'])
        strobeLampMode = (configValue['configPage']['flameConfiguration']['strobeLampMode'])
        period = str(configValue['configPage']['flameConfiguration']['period'])
        periodUnit = (configValue['configPage']['flameConfiguration']['periodUnit'])
        dropletTravelTime = str(configValue['configPage']['dropletConfiguration']['dropletTravelTime'])
        dropletTravelTimeUnit = (configValue['configPage']['dropletConfiguration']['dropletTravelTimeUnit'])
        pulseTime = str(configValue['configPage']['dropletConfiguration']['pulseTime'])
        pulseTimeUnit = (configValue['configPage']['dropletConfiguration']['pulseTimeUnit'])
        numberOfDroplets = str(configValue['configPage']['dropletConfiguration']['numberOfDroplets'])
        numberOfDropletsUnit = (configValue['configPage']['dropletConfiguration']['numberOfDropletsUnit'])
        sortingElectrode = str(configValue['configPage']['dropletConfiguration']['sortingElectrode'])
        microcontrollerName = str(configValue['configPage']['microcontrollerConfiguration']['deviceName'])
        exposureTime = str(configValue['configPage']['cameraConfiguration']['exposureTime'])
        width = str(configValue['configPage']['cameraConfiguration']['width'])
        height = str(configValue['configPage']['cameraConfiguration']['height'])
        spectrometerName = str(configValue['viewPage']['spectrometerName'])
        pumpNames = (configValue['viewPage']['pumpName'])
        defaultFolder = (configValue['viewPage']['defaultFolder'])
        wavelengthMinimum = str(configValue['viewPage']['wavelengthMinimum'])
        wavelengthMaximum = str(configValue['viewPage']['wavelengthMaximum'])
        intensityMinimum = str(configValue['viewPage']['intensityMinimum'])
        intensityMaximum = str(configValue['viewPage']['intensityMaximum'])
        #Set up configuration parameters on config Page with the loaded parameters
        self.ui.integrationTime.setText(integrationTime)
        self.ui.integrationTimeUnit.setCurrentIndex(integrationTimeUnit)
        self.ui.triggerMode.setCurrentIndex(triggerMode)
        self.ui.stropeLampOption.setCurrentIndex(strobeLamp)
        self.ui.stropeLampMode.setCurrentIndex(strobeLampMode)
        if(strobeLamp == 1):
            self.ui.strobeLampPeriod.setEnabled(True)
            self.ui.strobeLampPeriod.setText(period)
        else:
            self.ui.strobeLampPeriod.setEnabled(False)
            self.ui.strobeLampPeriod.setStyleSheet("padding: 6px;"
            "border-top-left-radius :10px;"
            "border-top-right-radius : 10px; "
            "border-bottom-left-radius : 10px;"
            "border-bottom-right-radius : 10px;"
            "background-color: rgb(180, 180, 180);")
        self.ui.periodUnit.setCurrentIndex(periodUnit)
        self.ui.dropletTravelTime.setText(dropletTravelTime)
        self.ui.dropletTravelTimeUnit.setCurrentIndex(dropletTravelTimeUnit)
        self.ui.pulseTime.setText(pulseTime)
        self.ui.pulseTimeUnit.setCurrentIndex(pulseTimeUnit)
        self.ui.numberOfDroplet.setText(numberOfDroplets)
        self.ui.numberOfDropletUnit.setCurrentIndex(numberOfDropletsUnit)
        self.ui.sortingElectrode.setText(sortingElectrode)
        #Set up previously use comport for the microcotnroller combo box list
        for i in range(self.ui.deviceList.count()):
            if(microcontrollerName == self.ui.deviceList.itemText(i)):
                self.ui.deviceList.setCurrentIndex(i)
                break
        #Set up camera configuration
        self.ui.exposureTimeInput.setText(exposureTime)
        self.ui.cameraWidth.setText(width)
        self.ui.cameraHeight.setText(height)
        #Set up configuration parameter on view Page
        #Set the pump name to the pump name text box
        for i, val in enumerate(pumpNames):
            self.ui.__getattribute__("pump"+str(i+1)+"Name").setText(val)
        #Set the spectrometer list for the spectrometer combo box
        for i in range(self.ui.spectrometerOptionBox.count()):
            if(spectrometerName == self.ui.spectrometerOptionBox.itemText(i)):
                self.ui.spectrometerOptionBox.setCurrentIndex(i)
                break
        if(isinstance(self,viewPage)):
            self.pathSelectionBox.addItem(defaultFolder)
        else:
            self.viewPage.pathSelectionBox.addItem(defaultFolder)
        self.ui.wavelengthMin.setText(wavelengthMinimum)
        self.ui.wavelengthMax.setText(wavelengthMaximum)
        self.ui.intensityMin.setText(intensityMinimum)
        self.ui.intensityMax.setText(intensityMaximum)
def saveConfig(self,filePath):
    #Store all the configurations in the view page and config page to the yml file
    list = []
    list.append(self.ui.pump1Name.text())
    list.append(self.ui.pump2Name.text())
    list.append(self.ui.pump3Name.text())
    list.append(self.ui.pump4Name.text())
    list.append(self.ui.pump5Name.text())
    data = {
    "configPage": {
        "cameraConfiguration":{
            "exposureTime": self.ui.exposureTimeInput.text(),
            "width": self.ui.cameraWidth.text(),
            "height": self.ui.cameraHeight.text()
        },
        "microcontrollerConfiguration":{
            "deviceName": self.ui.deviceList.currentText()
        },
        "flameConfiguration": {
            "integrationTime": int(self.ui.integrationTime.text()) if (self.ui.integrationTime.text()!='') else 0,
            "integrationTimeUnit": self.ui.integrationTimeUnit.currentIndex(),
            "triggerMode": self.ui.triggerMode.currentIndex(),
            "strobeLamp": self.ui.stropeLampOption.currentIndex(),
            "strobeLampMode": self.ui.stropeLampMode.currentIndex(),
            "period": int(self.ui.strobeLampPeriod.text()) if (self.ui.stropeLampOption.currentIndex()>0 and
                                                              self.ui.strobeLampPeriod.text() != '') else 0,
            "periodUnit": self.ui.periodUnit.currentIndex()
        },
        "dropletConfiguration": {
            "dropletTravelTime": float(self.ui.dropletTravelTime.text()) if (self.ui.dropletTravelTime.text()!='') else 0,
            "dropletTravelTimeUnit": self.ui.dropletTravelTimeUnit.currentIndex(),
            "pulseTime": float(self.ui.pulseTime.text()) if (self.ui.pulseTime.text()!='') else 0,
            "pulseTimeUnit": self.ui.pulseTimeUnit.currentIndex(),
            "numberOfDroplets": float(self.ui.numberOfDroplet.text()) if (self.ui.numberOfDroplet.text()!='') else 0,
            "numberOfDropletsUnit": self.ui.numberOfDropletUnit.currentIndex(),
            "sortingElectrode": int(self.ui.sortingElectrode.text()) if (self.ui.sortingElectrode.text()!='') else 0
        }
    },
    "viewPage": {
        "pumpName": list,
        "defaultFolder": self.pathSelectionBox.currentText(),
        "spectrometerName": self.ui.spectrometerOptionBox.currentText(),
        "wavelengthMinimum": float(self.ui.wavelengthMin.text()) if (self.ui.wavelengthMin.text()!='') else 0,
        "wavelengthMaximum": float(self.ui.wavelengthMax.text()) if (self.ui.wavelengthMax.text()!='') else 0,
        "intensityMinimum": float(self.ui.intensityMin.text()) if (self.ui.intensityMin.text()!='') else 0,
        "intensityMaximum": float(self.ui.intensityMax.text()) if (self.ui.intensityMax.text()!='') else 0
    }
    }
    #Dump all the data to the yml file
    try:
        with open(filePath, "w") as file:
            yaml.dump(data, file)
        self.ui.statusbar.showMessage("Configuration file saved",5000)
    except:
        self.ui.statusbar.showMessage("Failed to save file",5000)

def loadElectrode(context, filePath):
    if filePath == '': return
    print("load Elecrode Now")
    try:
        with open(filePath,'rb') as config:
            configValue = yaml.safe_load(config)
        context.ui.statusbar.showMessage("Configuration file read ",5000)
    except:
        context.ui.statusbar.showMessage("No configuration file found!",5000)
        return
    tempList = []
    if not isinstance(configValue, list):
        return 
    for electrode in configValue:
        tempList.append(electrode)
    return tempList

def saveElectrodes(context,filePath, electrodeList):
    if filePath == '': return
    print("save Elecrode Now")

    try:
        with open(filePath, 'w') as config:
            yaml.dump(electrodeList, config)
            context.ui.statusbar.showMessage("Configuration file saved",5000)
            print("Appended the config file")

    except Exception as e:
        context.ui.statusbar.showMessage("Failed to save file",5000)
        print("Failed to append the config file", e)
