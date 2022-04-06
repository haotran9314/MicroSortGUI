from PyQt5.QtCore import QPropertyAnimation,QSize
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtGui import QMovie

class recordButtonAnimation():
	def __init__(self,button,background):
		#Set up the animator for the record button 
		self.background = background
		self.opacityEffect = QGraphicsOpacityEffect()
		button.setGraphicsEffect(self.opacityEffect)
		self.animation = (QPropertyAnimation(self.opacityEffect, b"opacity"))
		self.recordingGif = (QMovie("resourcesFile/Icon/recordAnimation.gif"))
		#Set the animation starting value
		self.animation.setStartValue(0)
		self.animation.setEndValue(1)
		#Set the duration for the animation
		self.animation.setDuration(350)
		#Scale the gif animation properly
		self.recordingGif.setScaledSize(QSize(36,36))
		#set the background as the gif
		background.setMovie(self.recordingGif)
		#Start the animation
		self.startAnimation()
		
	def startAnimation(self):
		#Start the animation
		self.animation.start()
		self.recordingGif.start()
	def stopAnimation(self):
		#Stop the animation
		self.animation.stop()
		self.recordingGif.stop()
		self.background.clear()
		
