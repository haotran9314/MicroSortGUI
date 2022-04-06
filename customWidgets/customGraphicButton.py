from time import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time

from consolePrint import consolePrint

currentElectrode = 0
pulseTime = 0

class customGBT(QGraphicsItem):
    def __init__(self,name,pulseTime,microntrollerBoard):
        super(customGBT, self).__init__()
        #Make the electrode item selectable
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        #Set brush to red color for drawing later
        self.brush = QBrush(Qt.red)
        #Set the name of the electrode
        self.name = name
        #Set the pulse time of the electrode
        self.pulseTime = pulseTime
        #Set the microcontroller object so each electrode is capable of communicating with the microcontroller --> control the electrode
        self.microcontrollerBoard = microntrollerBoard
        #Initialize the timer
        self.timerIsRunning = False
        # self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget: QWidget) -> None:
        #Draw a rectangle using the red brush
        painter.fillRect(self.boundingRect(), self.brush)
        #Set the pen style for text drawing
        painter.setFont(QFont("Arial",12,15))
        painter.setPen(QColor('white'))
        #Draw the text above the rectangle showing its name and pulse time
        painter.drawText(-1,-20,"E: "+str(self.name))
        painter.drawText(-1,-1,"Pulse Time: "+str(self.pulseTime)+" us")
        # return super().paint(painter, option, widget)
    def boundingRect(self) -> QRectF:
        return QRectF(0,0,50,50)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        #If there is a clicked on the button
        global currentElectrode
        global pulseTime
        #Check if previous click eletrode is the same if not
        if(currentElectrode != int(self.name) or pulseTime != int(self.pulseTime)):
            # set the previously clicked electrode to current electrode
            currentElectrode = int(self.name)
            pulseTime = int(self.pulseTime)
            # Write new param to the microcontroller change the pulse time and the electrode
            self.microcontrollerBoard.writeParam(0,int(self.pulseTime),str(self.name))
            #Write one pulse
            self.microcontrollerBoard.write('x')
        else:
            #If previous clicked is the same as the current click --> just send an X instead setting the param again
            self.microcontrollerBoard.write('x')
        #Set the color of the rectangle to green
        self.setBrush(QColor("green"))
        if(not self.timerIsRunning):
            self.timerIsRunning = True
            timer = QTimer.singleShot(int(int(self.pulseTime)/1000), self.offEvent)
        return super().mousePressEvent(event)
    def offEvent(self):
        self.setBrush(QColor("red"))
        self.timerIsRunning = False
    # def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #     #If the click is released --> make the rectangle turn back to red
    #     self.setBrush(QColor("red"))
    #     return super().mouseReleaseEvent(event)
    def setBrush(self, brush):
        #Update the brush for color changing
        self.brush = brush
        self.update()