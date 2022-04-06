from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui


class customGraphicView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.scene = ''
        #Intialize the zoom factors and zoom limitation
        self.zoomInFactor = 1.5
        self.zoomStep = 1
        self.zoom = 10
    def getScene(self,scene):
        #Get the scene and set the scene
        self.scene = scene
        self.setScene(self.scene)
    def initUI(self):
        #Set up graphic view properties
        #Set up smoothing factor for the graphic view
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        #Set up the full view for the graphic view
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        #Set up the anchor mode of the graphic view
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #Disable the horizontal and vertical scroll bar
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            #If the delete key button is clicked --> remove the selected item
            for item in self.scene.selectedItems():
                self.scene.removeItem(item)
                self.scene.count -= 1
        else:
            return super().keyPressEvent(event)

    def mousePressEvent(self, event):
        #If right button is pressed
        if event.button() == Qt.RightButton:
            #Create release event from the graphic view using the graphic scene position and scene position
            releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),Qt.LeftButton, Qt.NoButton, event.modifiers())
            super().mouseReleaseEvent(releaseEvent)
            #Set the drag mode to hand drag mode
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            #Create a dummy event if a right button press is on the graphic item (otherwise it's going to crash the app)
            dummyEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
            super().mousePressEvent(dummyEvent)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            #Create a dummy event if a right button release is on the graphic item (otherwise it's going to crash the app)
            dummyEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
            super().mouseReleaseEvent(dummyEvent)
            #Set the drag mode back to no drag since the right click button is realeased
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # get zoom out factor
        zoomOutFactor = 1 / self.zoomInFactor
        #Get zoom factor base on current zoom
        if event.angleDelta().y() <= 0:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep
        else:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        # set the zoom factor to the scene
        self.scale(zoomFactor, zoomFactor)

            

