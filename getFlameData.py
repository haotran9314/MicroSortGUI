import sys
from multiprocessing import Event,Manager,Pipe
import time
import timeit
import numpy,serial
from scipy import ndimage
from numba import njit
from numpy.fft import fft
from seabreeze.spectrometers import Spectrometer
from numpy import random
from bisect import bisect_left
import seatease.spectrometers as s

class dataProcess():
	def __init__(self) -> None:
		""" Initializing all the required parameters
		"""
		#Initialize comport for microcontroller
		self.comport = ""
		#Initialize spectrometer variable
		self.spec = ""
		#Initialize detection gates
		self.wg1 = 500
		self.wg2 = 600
		self.ig1 = 90
		self.ig2 = 2000
		#Initialize spectrometer integration time and operation mode
		self.integrationTime = 3
		self.simulationMode = 's'
		#Initialize region of interest for wavelength
		self.i1 =0
		self.i2 =0
		#Initialize background, wavelength and intensity array
		self.background = numpy.arange(2048, dtype=numpy.float64)
		self.wavelength = numpy.arange(2048, dtype=numpy.float64)
		self.intensity = numpy.arange(2048, dtype=numpy.float64)
		#Initialize detection state and background substraction state
		self.detection = 0
		self.backgroundSubStraction = "False"
		self.numberOfDroplet = 1000
	def setup(self,wg1,wg2,ig1,ig2,integrationTime,spectrometerMode,backgroundSubStraction,comport,numberOfDroplet):

		#Store the passed detection gate values
		self.wg1 = wg1
		self.wg2 = wg2
		self.ig1 = ig1
		self.ig2 = ig2
		#Get the number of droplet to be sorted
		self.numberOfDroplet = numberOfDroplet
		#Store the spectrometer integration time and  mode
		self.integrationTime = integrationTime
		self.simulationMode = spectrometerMode

		#Initialize spectrometer object based on the spectrometer mode
		if(self.simulationMode.strip() == "r"):
			self.spec = Spectrometer.from_first_available()
			self.spec.integration_time_micros(self.integrationTime)
		else:
			self.spec = s.Spectrometer.from_first_available()
			self.spec.integration_time_micros(self.integrationTime)

		#Store the background substraction mode
		self.backgroundSubStraction = backgroundSubStraction

		#Store the passed comport value
		self.comport = comport
		#Try to initialize the microcontroller connection
		#self.comport.strip() #"COM5"
		try:
			self.teensy = serial.Serial(port=self.comport.strip(), baudrate=1000000, timeout=.01)
		except Exception as e:
			#If failed write to the GUI
			sys.stderr.write(str(e))
			sys.stderr.flush()

		#Get prev time
		self.prev = time.perf_counter()
		#Get the background noise from the spectrometer
		self.getBackgroundNoise()
		#Find the region of interest (wavelength) based on user input gate for wavelength
		self.wavelengthRegionIndex()
		self.wavelength,self.intensity = self.spec.spectrum()
		print("Set up successfully")

	def getBackgroundNoise(self):
		#If background substraction is set, get the current 10 average value as background noises.
		if(self.backgroundSubStraction.strip() == "True"):
			self.background = self.spec.intensities()
			for _ in range(10):
				self.background = numpy.add(self.background,self.spec.intensities())
			self.background = numpy.divide(self.background,11)
		#If background substraction is not set, set up an array of zeros as background noises.
		else:
			self.background = numpy.zeros_like(self.spec.intensities())
	def wavelengthRegionIndex(self):
		#Get the region of interest for the wavelength region
		checkRegion = self.spec.wavelengths()
		self.i1 = self.binarySearch(checkRegion,self.wg1)
		self.i2 = self.binarySearch(checkRegion,self.wg2)
	def binarySearch(self,list,item):
		#Use the binary search to get the region of interest for the wavelength regions
		i = bisect_left(list,item)
		if(i != len(list)):
			return i
	def getData(self):
		#Get the data from the spectrometer
		self.wavelength,self.intensity = self.spec.spectrum()
		if(self.simulationMode == 's'):
			if(numpy.random.rand()*10<=2):
				self.intensity[1500:1530] = numpy.random.randint(low = 100, high = 600,size=30)

	def detectionFunction(self):
		self.detection = self.sigProcessing(self.intensity[self.i1:self.i2],self.background[self.i1:self.i2],self.ig1)
		#Send a trigger to the micrcontroller so it can actuate the electrode based on the detection and the maximum number of droplets to be sorted
		if(self.detection and (time.perf_counter()-self.prev>1/self.numberOfDroplet)):
			self.prev = time.perf_counter()
			try:
				self.teensy.write(b'x')
			except Exception:
				pass
			
	@staticmethod
	@njit(cache = True,nogil = True)
	def sigProcessing(intensity,background,ig1):
		#Substract the current intensity from the background noises
		intensity=numpy.subtract(intensity,background)
		#check if there are any values greater than the gate
		index = numpy.nonzero(intensity>=ig1)
		#If there is avalue that greater than the gate --> return true else false
		if(index[0].size >0):
			return 1
		else:
			return 0

		






