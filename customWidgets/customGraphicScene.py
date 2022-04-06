import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from customWidgets.customGraphicButton import customGBT
class customGraphicScene(QGraphicsScene):
    def __init__(self,microcontrollerBoard,ui_element,parent = None):
        super().__init__(parent)
        #Intialize microcontroler object so it can be used later for electrode items creation
        self.microcontrollerBoard = microcontrollerBoard
        #Initialize ui element
        self.ui = ui_element
        #Get the first index of the electrode
        self.count = 1
        #Initiaze the background of the graphic scene
        self.background = QColor("#393939")
        #Initialize grid size value
        self.gridSize = 20
        self.gridSquares = 5
        #Initialize two pens color dark and light
        self.penLight = QPen(QColor("#2f2f2f"))
        self.penLight.setWidth(1)
        self.penDark = QPen(QColor("#292929"))
        self.penDark.setWidth(2)
        #Initialize the scene width
        self.sceneWidth = 64000
        #Initialize the scene height
        self.sceneHeight = 64000
        #Set the scene size rectangle to the scene width and scene height
        self.setSceneRect(-self.sceneWidth//2, -self.sceneHeight//2,self.sceneWidth,self.sceneHeight)
        #Set the scene background color to back
        self.setBackgroundBrush(self.background)



    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        # initialize grid (top, leftGrid, bottom and rightGrid side of the grid)
        rightGrid = int(math.ceil(rect.right()))
        bottomGrid = int(math.ceil(rect.bottom()))
        leftGrid = int(math.floor(rect.left()))
        topGrid = int(math.floor(rect.top()))
        fTopGrid = topGrid - (topGrid % self.gridSize)
        fLeftGrid = leftGrid - (leftGrid % self.gridSize)
        #Intialize lines list so it can be drawn later on the graphic scene
        lightLines, darkLines = [], []
        # compute list of vertical lines to be drawn on the chip viewer
        for y in range(fTopGrid, bottomGrid, self.gridSize):
            #Get lines to be drawn everyother horizontal lines
            if (y % (self.gridSize*self.gridSquares) != 0): 
                lightLines.append(QLine(leftGrid, y, rightGrid, y))
            else: 
                darkLines.append(QLine(leftGrid, y, rightGrid, y))
        # compute list of horizontal lines to be drawn on the chip viewer
        for x in range(fLeftGrid, rightGrid, self.gridSize):
            #Get lines to be drawn everyother vertical lines
            if (x % (self.gridSize*self.gridSquares) != 0): 
                lightLines.append(QLine(x, topGrid, x, bottomGrid))
            else: 
                darkLines.append(QLine(x, topGrid, x, bottomGrid))
        # draw the light lines
        painter.setPen(self.penLight)
        painter.drawLines(*lightLines)
        # draw the dark lines
        painter.setPen(self.penDark)
        painter.drawLines(*darkLines)
    
    def dragEnterEvent(self, event: 'QGraphicsSceneDragDropEvent') -> None:
        #Allow drag enter object
        event.setAccepted(True)
    def dropEvent(self, event: 'QGraphicsSceneDragDropEvent') -> None:
        #Allow drop item action
        event.acceptProposedAction()
        #If the drop object has the same type as list item 
        if(event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist')):
            #Create electrode graphic item in the graphic scene using the electrode input/pulse input/ or default where it's going to set 600 us pulse and electrode number increamentally
            if(self.ui.electroNumberInput.text() != '' and self.ui.electrodePulseTimeInput.text() != ''):
                rect = customGBT(self.ui.electroNumberInput.text(),self.ui.electrodePulseTimeInput.text(),self.microcontrollerBoard)
            elif(self.ui.electroNumberInput.text() != ''):
                rect = customGBT(self.ui.electroNumberInput.text(),"600",self.microcontrollerBoard)
            elif(self.ui.electrodePulseTimeInput.text() != ''):
                rect = customGBT(self.count,self.ui.electrodePulseTimeInput.text(),self.microcontrollerBoard)
            else:
                rect = customGBT(self.count,"600",self.microcontrollerBoard)
            #Get the drop item position and set it to the graphic item position
            rect.setPos(event.scenePos())
            #Add the item to the graphic scene
            self.addItem(rect)
            #Allow user to be able to move the item
            rect.setFlag(QGraphicsItem.ItemIsMovable)
            self.count += 1
    def dragMoveEvent(self, event: 'QGraphicsSceneDragDropEvent') -> None:
        #Allow drag move event
        event.setAccepted(True)

    def clearAllElectrodes(self):
        #get all item in the item list --> remove all item from that list
        for item in self.items():
            if type(item) == customGBT:
                self.removeItem(item)

    def loadElectrodes(self, electrodesList):
        #Load the electrode from the electrode list using the name of the electrode, pulse time and its position
        for electrode in electrodesList:
            loadedElectrode = self.createElectrode(electrode["id"],electrode["pulseTime"], electrode["x_pos"],electrode["y_pos"])
            self.addItem(loadedElectrode)

    def createElectrode(self, id,pulseTime ,x_pos, y_pos):
        #Create electrode item using the id, pulse time and its position
        rect = customGBT(id,pulseTime,self.microcontrollerBoard)
        rect.setPos(x_pos, y_pos)
        self.addItem(rect)
        rect.setFlag(QGraphicsItem.ItemIsMovable)
        return rect

