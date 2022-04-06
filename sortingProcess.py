from concurrent.futures import ThreadPoolExecutor
import numpy,time
from getFlameData import dataProcess
from numba import njit
import threading, win32api,win32con,win32process,sys
from highResolutionSleep import*

def sortingProcess(queue,plotCompletedEvent,sendDataToPlotEvent,stopEvent):
    #Get the parameters from the queue (format: wavelength gate minimum, wavelenth gate maximum, intensity minimum, intensity maximum, integration time, spectrometer mode, background substraction, COM port, number of droplet)
    param = queue.get()
    param = [item for item in param.split(',')]
    #Set the stop even to false
    stopEvent.set()
    #Set the multi threading event so we can manage the run time of each thread
    processDataEvent = threading.Event()
    sendDataEvent = threading.Event()
    #Initialize threadpool executor
    pool = ThreadPoolExecutor(3)
    #Initialize the data process class
    dat = dataProcess()
    #Set up the parameters
    dat.setup(float(param[0]),float(param[1]),float(param[2]),float(param[3]),float(param[4]),param[5],param[6],param[7],float(param[8]))
    #Put the current process priority to High
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
    #Set a higher context switching rate
    sys.setswitchinterval(0.0005)
    #Submit the get spectrometer function to the thread pool
    pool.submit(getSpectrometerData,dat,sendDataEvent,processDataEvent,stopEvent)
    #Submit the process spectrometer data function to thread pool
    if(param[9].strip() == "True"):
        pool.submit(processSpectrometerData,dat,processDataEvent,sendDataEvent,stopEvent)
    #Submit send data to plot function to the thread pool
    pool.submit(sendData,dat,queue,sendDataEvent,sendDataToPlotEvent,plotCompletedEvent,stopEvent,param[9].strip(),processDataEvent)
    #When all thread is finished, clean all the resource up
    pool.shutdown(wait= True,cancel_futures= True)

def getSpectrometerData(dat,sendDataEvent,processDataEvent,stopEvent):
    while(stopEvent.is_set()):
        #Get spectrometer data
        dat.getData()
        # delayMicroseconds(1000)
        # st = time.perf_counter()+600/1000000
        # while(time.perf_counter()<=st):
        #     pass
        #Set the process data event so the spectrometer can be process
        processDataEvent.set()
    processDataEvent.set()
def processSpectrometerData(dat,processDataEvent,sendDataEvent,stopEvent):
    while(stopEvent.is_set()):
        #Wait for the process data even
        processDataEvent.wait()
        #If new data is available --> process the data, send signal to microcontroller if there is detection else send nothing
        dat.detectionFunction()
        #Set the send data even so the spectrometer data can be send to the graphical user interface to be plot
        sendDataEvent.set()
        processDataEvent.clear()
    #close the microcontroller object
    dat.teensy.close()
    sendDataEvent.set()
def sendData(dat,queue,sendDataEvent,sendDataToPlotEvent,plotCompletedEvent,stopEvent,waitSorting,processDataEvent):
    plotCompletedEvent.set()
    while(stopEvent.is_set()):
        #Wait for the plot complemte
        plotCompletedEvent.wait()
        #Wait for data from spetrometer to arrive
        if(waitSorting == "True"):
            sendDataEvent.wait()
            sendDataEvent.clear()
        else:
            processDataEvent.wait()
            processDataEvent.clear()
        #Concatenate the intensity and wavelength into one array
        spectrum = concat(dat.intensity,dat.wavelength,dat.background,dat.detection)
        #Send data to plot
        queue.put(spectrum)
        #Delay for 5ms --> avoid lagging between plot
        delayMicroseconds(5000)
        sendDataToPlotEvent.set()
        plotCompletedEvent.clear()

@njit(cache=True,nogil = True)
def concat(intensity,wavelength,background,detection):
    #Get the background substraction result
    intensity=(numpy.subtract(intensity,background))
    #Concatenate the wavelenght and intensity (only get every 4th elements (avoid hangging in the queue with large data))
    spectrum = numpy.concatenate((wavelength[::4],intensity[::4]))
    #Push in the detection status
    spectrum = numpy.append(spectrum,detection)
    return spectrum



