import sys,os,time
qmixsdk_dir =  "C:/QmixSDK" #path to Qmix SDK
sys.path.append(qmixsdk_dir + "/lib/python")
os.environ['PATH'] += os.pathsep + qmixsdk_dir
from qmixsdk import qmixbus
from qmixsdk import qmixpump
from qmixsdk import qmixvalve
from qmixsdk.qmixbus import UnitPrefix, TimeUnit

class nemesysPump():
    def pumpSetup(self,deviceConfig,diam,stroke,progressUpdate):
        #Get the device configuration file
        self.deviceConfig = deviceConfig
        #Pass in the progress update
        progressUpdate = progressUpdate
        #Get the diameter list
        self.diam = diam
        #Get the stroke list
        self.stroke = stroke
        #Create the pump list
        self.pumpList = []
        #Update the sstatus
        progressUpdate.emit('Starting Nemesys Bus...')
        #Set the Nemesys bus instance
        self.bus= qmixbus.Bus()
        time.sleep(0.2)
        progressUpdate.emit('Opening Pump Device Configuration ' + str(self.deviceConfig))
        #Open the NEMESYS BUS
        self.bus.open(self.deviceConfig, 0)
        time.sleep(0.2)
        try:
            #Start the bus if failed stop the pump set up
            self.bus.start()
            isConnect=True
            progressUpdate.emit("Bus set up successfull ")
            
        except:
            progressUpdate.emit("Can't start bus. Pump Set Up Failed .... ")
            isConnect=False
        time.sleep(0.2)
        if(isConnect):
            #Get all the avaialble pumps and set up each pump individually
            for i in range (qmixpump.Pump.get_no_of_pumps()):
                try:
                    pump = qmixpump.Pump()
                    self.pumpList.append(pump)
                    pump.lookup_by_device_index(i)
                    self.pumpConfig(pump,i,progressUpdate)
                except Exception as e:
                    progressUpdate.emit(str(e))

    def pumpConfig(self,pump,index,progressUpdate):
        print(pump)
        #Enabling Pump
        if(pump.is_in_fault_state()):
            pump.clear_fault()
            progressUpdate.emit("Pump Error: " + pump.get_device_name())
        if(not pump.is_enabled()):
            pump.enable(True)
        #Set Synringe Config
        pump.set_syringe_param(float(self.diam[index]),float(self.stroke[index]))
        # syringe = pump.get_syringe_param()
        #Set Syringe Unit
        pump.set_flow_unit(qmixpump.UnitPrefix.micro, qmixpump.VolumeUnit.litres, qmixpump.TimeUnit.per_second)
        pump.set_volume_unit(qmixpump.UnitPrefix.micro, qmixpump.VolumeUnit.litres)
        print("Set up sucess")
        time.sleep(1)


    def pumpStart(self, pump, flow,progressUpdate):
        pumpNumber = pump
        #get the pump object
        pump = self.pumpList[pump-1]
        #Generate the flow for the pump
        pump.generate_flow(flow)
        time.sleep(1)
        #Get the flow rate
        flowRate = pump.get_flow_is()
        #Update the flow rate to the gui
        progressUpdate.emit(str(pumpNumber) +","+str(flowRate))
        #Wait for dose to finish
        finished = self.wait(pump, 100000,pumpNumber,progressUpdate)
        if finished == True:
            print ('done')

    def pumpStop(self, pump,progressUpdate):
        #get the pump object
        pump = self.pumpList[pump-1]
        #Stop the pump
        pump.stop_pumping()

    def pumpStopAll(self,progressUpdate):
        #Iterating through all the pump object and stop it all
        for pump in self.pumpList:
          pump.stop_pumping()

    def wait(self, pump, timeOut,pumpNumber,progressUpdate):
        #Create a polling timer for the from the pump
        messageTimer= qmixbus.PollingTimer(1000)
        timer = qmixbus.PollingTimer(timeOut * 1000)
        result = True
        while (result == True) and not timer.is_expired():
            time.sleep(0.05)
            #Update the flow rate constantly
            progressUpdate.emit(str(pumpNumber) +","+str(pump.get_fill_level()))
            if messageTimer.is_expired():
                messageTimer.restart()
            #Get the pump result if it's sucessfull or failed
            result = pump.is_pumping()
        return not result
    def testFunction(self,pump,progressUpdate):
        for i in range(10000):
            progressUpdate.emit(str(pump)+","+str(i))
            time.sleep(0.01)




    
        