import serial.tools.list_ports,time,json
from PyQt5 import QtSerialPort,QtCore
class microntrollerBoard():
    def __init__(self,ui_element) -> None:
        #Get the user interface elements of the GUI
        self.ui = ui_element
        #Load the comport to the microcontroller port selection
        self.loadComports()
        self.isConnect = False
        #load port mapping
        with open('mapping.txt') as map:
            self.portMap = map.read()
        self.portMap = json.loads(self.portMap)
    def open(self):
        #If there is a connection avaialble 
        if(self.isConnect):
            print(self.microcontrollerBoard.portName())
            #Check if the user desired connection is matched with the current connection
            if(self.microcontrollerBoard.portName() != self.ui.deviceList.currentText().split('(')[1].replace(")","")):
                #If not close the connection and establish a new connection for the user
                print("COM change")
                self.microcontrollerBoard.close()
                self.isConnect = False
        #If there is no serial connection
        if(not self.isConnect):
            comPort = self.ui.deviceList.currentText().split('(')[1].replace(")","")
            #Initialize serial port instance
            self.microcontrollerBoard = QtSerialPort.QSerialPort()
            #When data is available, link it to the get data method where it will handle the arrival data
            self.microcontrollerBoard.readyRead.connect(self.getData)
            #Set the port connection
            self.microcontrollerBoard.setPortName(comPort)
            #Set port rate
            self.microcontrollerBoard.setBaudRate(1000000)
            #Set write and read channel
            self.microcontrollerBoard.open(QtCore.QIODevice.ReadWrite)
            self.isConnect = True
    def getData(self):
        #Handle the data and display it on the microcontroller console
        text = self.microcontrollerBoard.readAll()
        data = bytes(text).decode("utf8")
        self.ui.hardwareTextBox.appendPlainText(data)
    def closePort(self):
        #If there is a serial connection
        if(self.isConnect):
            #Disconnect it and realease the port
            self.microcontrollerBoard.close()
            self.isConnect = False
    def write(self,data):
        #If there is a connection
        if(self.isConnect):
            #Write the data to the microcontroller
            self.microcontrollerBoard.write(data.encode())
            self.microcontrollerBoard.flush()
        else:
            self.ui.hardwareTextBox.appendPlainText("Please Connect to Microcontroller")
    def writeParam(self,dropletTravelTime,pulseTime,electrode):
        #If there is a connection
        if(self.isConnect):
            try:
                #write the parameters as parameters format so it can be read from the microcontroller side
                parameters = "p"+","+str(int(dropletTravelTime)) +","+ str(int(pulseTime))+","+str(self.portMap[electrode])
                self.microcontrollerBoard.write(parameters.encode())
                self.microcontrollerBoard.flush()
                #Shows the sent parameter on the microcontroller console
                self.ui.hardwareTextBox.appendPlainText("Param sent with mapping: "+parameters)
            except Exception as e:
                self.ui.console.append(e)
        else:
            self.ui.hardwareTextBox.appendPlainText("Please Connect to Microcontroller")
    def loadComports(self):
        #Clear the current device list
        self.ui.deviceList.clear()
        #Load with new list
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.ui.deviceList.addItem(port.description)