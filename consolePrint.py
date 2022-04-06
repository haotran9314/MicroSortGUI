#The file is used for printing messages to the console window
def consolePrintError(self,str):
    self.ui.console.append("<html><b>Error: "+str+"</b</html>")
def consolePrint(self,str):
    self.ui.console.append("    "+str)