from PyQt5.QtWidgets import QTextBrowser
from PyQt5 import QtCore

class customTextBrowser(QTextBrowser):
    #Overide the size hint of the console window otherwise, it's going to overlay all other user interface elements
    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(1600,85)