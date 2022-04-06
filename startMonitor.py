import sys
import cv2
from cameraModel.Model.Cameras.Hamamatsu import camera

def startCamera(index,exposureTime,w,h):
    #Get the first camera instance
    cam = camera(index)
    #initialize camera
    cam.initializeCamera()
    #Set the camera acquisition mode to continous
    cam.setAcquisitionMode(cam.MODE_CONTINUOUS)
    #Trigger the camera
    cam.triggerCamera()
    #Set the exporsure time of the camera
    cam.setExposure(exposureTime)
    while 1:
        #Get the frame from the camera
        img = cam.readCamera()
        #Resize the image based on user input
        resize = cv2.resize(img[0], (w,h), interpolation = cv2.INTER_AREA)
        #Show the window
        cv2.imshow('MicroSort Camera', resize)
        #If exit button is pressed or x button on the window is clicked --> close the camera view
        if (cv2.waitKey(1) & 0xFF == 27) or (cv2.getWindowProperty('MicroSort Camera',cv2.WND_PROP_VISIBLE) < 1):
            break
    #Stop the camera --> release the camera object
    cam.stopCamera()

if __name__ == "__main__":
    #Get all the parameters from user inputs format (camera index, exposure time, camera width, camera height)
    for configParam in sys.stdin:
        if(configParam != None):
            param = [item for item in configParam.split(',')]
            break
    try:
        #Pass the parameters in to the camera instance
        startCamera(int(param[0])-1,int(param[1]),int(param[2]),int(param[3].strip()))
    except Exception as e:
        sys.stderr.write(str(e))
