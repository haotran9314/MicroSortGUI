import json
#This file is used to create the mapping text file so it can be used later in the graphical user interface.
#The sole purpose of this file is to map the correct address of the port expander pins to the chip pins
mapping = {}
for i in range(1,120+1):
    if(i>0 and i<=20):
        mapping[str(i+80)] = i
    elif(i>20 and i<=40):
        mapping[str(i+80)] = i
    elif(i>40 and i<=60):
        mapping[str(i-40)] = i
    elif(i>60 and i<=80):
        mapping[str(i-40)] = i
    elif(i>80 and i<=100):
        mapping[str(i-40)] = i
    elif(i>100 and i<=120):
        mapping[str(i-40)] = i
#Dump the corresponding list to the mapping text file in json format
with open("mapping.txt", 'w') as f: 
    f.write(json.dumps(mapping))