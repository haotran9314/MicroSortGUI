import time
import numpy
from PyQt5.QtCore import QObject,pyqtSignal,QRunnable
import pyqtgraph as pg

from consolePrint import consolePrintError

class pumpWorkerSignals(QObject):
	#Initialize the signal for pump worker
	finished = pyqtSignal()
	error = pyqtSignal(str)
	result = pyqtSignal(object)
	progress = pyqtSignal(str)
class pumpWorker(QRunnable):
	def __init__(self, fn, *args, **kwargs):
		super(pumpWorker, self).__init__()
		# Store constructor so it can be used in the run function (when starting the thread)
		#Get the function to execute
		self.fn = fn
		#Get the arguments to pass to the function
		self.args = args
		self.kwargs = kwargs
		#Initialize the signals to update the status of the process
		self.signals = pumpWorkerSignals()
		# Add the callback to our kwargs for progress update
		self.kwargs['progressUpdate'] = self.signals.progress
	def run(self):
		try:
			#Run the function in the thread and pass all the previously stored arguments
			self.fn(*self.args, **self.kwargs)
		except Exception as e:
			self.signals.error.emit(str(e))
			# consolePrintError(self,e)
			# print("Error executing function", e)
		finally:
			#When task is complete, emit a finish signal
			self.signals.finished.emit()  # Done

class queueWorker(QObject):
	data = pyqtSignal(numpy.ndarray)
	item = pyqtSignal(pg.PlotDataItem)
	def __init__(self,queue,param,dataSendEvent,*args, **kwargs):
		super().__init__(*args, **kwargs)
		#Get the queue so it can be read later
		self.queue = queue
		#Get the param so it can be send to the sorting process later
		self.param = param
		#Get the event when data is available in the queue
		self.dataSendEvent = dataSendEvent

	def run(self):
		self.queue.put(self.param)
		time.sleep(4)
		while(1):
			#Wait for the data avaialble in the queue
			self.dataSendEvent.wait()
			self.dataSendEvent.clear()
			#Emit the data to plot in the spectrometer
			self.data.emit(self.queue.get())
