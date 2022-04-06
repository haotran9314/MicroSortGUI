from PyQt5 import QtCore,QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPropertyAnimation,pyqtProperty

class customLineEdit(QtWidgets.QLineEdit):
    #The below 2 lines is just for slot and signal incase we need to use it
    focusOutSig = QtCore.pyqtSignal()
    focusInSig = QtCore.pyqtSignal()
    #Inittialize the the LineEdit with custom animation value (red) to notify user when they enter incorrect values
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = QColor(255,0,0,100)
        self.pulseAnimation = QPropertyAnimation(self, b"color", self)
        self.pulseAnimation.setDuration(1000)  
        self.pulseAnimation.setStartValue(QColor(245, 29, 29,255))
        self.pulseAnimation.setEndValue(QColor(255,255,255,255))
    def externalTrigger(self):
        self.pulseAnimation.start()
    
    #need to create a Qproperty for Animation (get and set function basically)
    @pyqtProperty(QColor)
    def color(self):
        return self._color
    @color.setter
    def color(self, pos):
        self._color = pos
        self.setBackGround(self._color)

    #Set the background of the lineEdit
    def setBackGround(self,QColor):
        current_style = "padding: 6px;border-top-left-radius :10px;border-top-right-radius : 10px; border-bottom-left-radius : 10px;border-bottom-right-radius : 10px;"
        updated_style = current_style +'background-color: ' + QColor.name(QColor.HexArgb) +';'
        self.setStyleSheet(updated_style)
    
    #Check if the focus is in or out --> we can do some certain action withit
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.focusInSig.emit()
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.focusOutSig.emit()