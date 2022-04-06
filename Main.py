import sys,ctypes,psutil,signal

from configPage import *
from chipViewerPage import *
from customWidgets.customTextBrowser import customTextBrowser
from viewPage import *
from microcontrollerCom import *
# include PyQt5 library
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow,QSplashScreen 
from resourcesFile.GUI import Ui_MainWindow
from resourcesFile.splashScreen import Ui_SplashScreen

counter = 0
#Initialize the Main GUI window
class App(QMainWindow):
	def __init__(self):
		super().__init__()
		#Set up UI elements (title,icon and the GUI file)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.setWindowTitle('MicroSort')
		self.setWindowIcon(QIcon('resourcesFile/Icon/lab.png'))
		self.showMaximized()
		#Set the start up page as configuration page
		self.ui.main.setCurrentWidget(self.ui.configPage)
		#Set up the console window in the GUI for debugging
		self.ui.consoleWindow.setWindowTitle("Console Window")
		#Set up micronctroller connection
		self.microcontrolerBoard = microntrollerBoard(self.ui)
		#Set up view page from the viewPage class
		self.view = viewPage(self.ui,self.microcontrolerBoard)
		#Set up config page from the configPage class
		self.config = configPage(self.ui,self.view,self.microcontrolerBoard,self.sender)
		#Set up chip view page
		self.chipView = chipViewPage(self.ui,self.microcontrolerBoard)
		#Connect side buttons to functions
		#When configuration button is clicked --> link to configButton function
		self.ui.configButton.clicked.connect(self.configButton)
		#When view page button is clicked --> link to viewButton function
		self.ui.viewButton.clicked.connect(self.viewButton)
		#When chip view button is clicked --> link to chipviewButton function
		self.ui.chipViewButton.clicked.connect(self.chipViewButton)

	def configButton(self):
		#Set the page to configuration page
		self.ui.main.setCurrentWidget(self.ui.configPage)
	def viewButton(self):
		#Set the page to view page
		self.ui.main.setCurrentWidget(self.ui.sortingPage)
	def chipViewButton(self):
		#Set the page to chip viewer page
		self.ui.main.setCurrentWidget(self.ui.chipViewerPage)

	def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
		""" When app is closed, destroy all python processes 
		"""
		#Stop all the pump
		self.config.stopAllPump()
		#close the queue of communication between processes
		self.view.queue.close()
		#If the child process is not closed
		if(self.view.childPID is not None):
			#Kill the process
			if psutil.pid_exists(self.view.childPID):
				os.kill(self.view.childPID,signal.SIGTERM)
		return super().closeEvent(a0)

class splashScreen(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_SplashScreen()
		self.ui.setupUi(self)
		self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
		self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setWindowTitle('MicroSort')
		self.setWindowIcon(QIcon('resourcesFile/Icon/lab.png'))
		self.movie = QMovie("resourcesFile/Icon/loading.gif")
		self.movie.setScaledSize(QSize(200,200))
		self.ui.appLoading.setMovie(self.movie)
		self.movie.start()
		self.shadow = QGraphicsDropShadowEffect(self)
		self.shadow.setBlurRadius(20)
		self.shadow.setXOffset(0)
		self.shadow.setYOffset(0)
		self.shadow.setColor(QColor(0, 0, 0, 60))
		self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.progress)
		# TIMER IN MILLISECONDS
		self.timer.start(20)

		## SHOW ==> MAIN WINDOW
		########################################################################
		self.show()
		## ==> END ##

	## ==> APP FUNCTIONS
	########################################################################
	def progress(self):

		global counter

		# SET VALUE TO PROGRESS BAR
		self.ui.progressBar.setValue(counter)

		# CLOSE SPLASH SCREE AND OPEN APP
		if counter > 100:
			# STOP TIMER
			self.timer.stop()

			# SHOW MAIN WINDOW
			self.main = App()
			self.main.show()

			# CLOSE SPLASH SCREEN
			self.close()

		# INCREASE COUNTER
		counter += 1

	

if __name__ == "__main__":
	st = time.perf_counter()
	appId = u'shihlab.microsort.1.0'
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)
	app = QApplication(sys.argv)
	window = splashScreen()
	# st = time.perf_counter()
	# w = App()
	# print(time.perf_counter()- st)
	# w.show()
	# print(time.perf_counter()- st)
	sys.exit(app.exec())
