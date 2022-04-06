import pyqtgraph as pg
import sys

# This is a custom class to add the bounding region for x/y axis
# Most of the code here is based on pyQtGraph LinearRegionIteam.py file (boundingRect) function
class customLinearRegionItem(pg.LinearRegionItem):
	def __init__(self, xyBound = None, *args, **kwargs):
		super(customLinearRegionItem, self).__init__(*args, **kwargs)
		self.constrain = xyBound
	def setYBound(self,ymin=0.0,ymax=0.0):
		yBound = [ymin,ymax]
		self.constrain = yBound
	def boundingRect(self):
		linearRegionItem = self.viewRect()      
		regionRange = self.getRegion()
		# if type is not int or list throw exception
		if(not isinstance(self.constrain,list)):
			print(type(self.constrain))
			sys.exit('Y bound must be of type int or list of int')
		#if limit is only bounded by one value
		elif(isinstance(self.constrain, int)):
			if(self.orientation == 'vertical'):
				length = linearRegionItem.height()
				linearRegionItem.setBottom(self.constrain)
				linearRegionItem.setTop(linearRegionItem.top() + length * self.span[0])
				linearRegionItem.setLeft(regionRange[0])
				linearRegionItem.setRight(regionRange[1])
			else:
				length = linearRegionItem.width()
				linearRegionItem.setBottom(regionRange[1])
				linearRegionItem.setTop(regionRange[0])
				linearRegionItem.setLeft(self.constrain)
				linearRegionItem.setRight(linearRegionItem.left() + length * self.span[1])
		# if limit is bounded by two value (list)
		elif(isinstance(self.constrain, list)):
			if(self.orientation == 'vertical'):
				length = linearRegionItem.height()
				linearRegionItem.setBottom(self.constrain[0])
				linearRegionItem.setTop(self.constrain[1])
				linearRegionItem.setLeft(regionRange[0])
				linearRegionItem.setRight(regionRange[1])
			else:
				length = linearRegionItem.width()
				linearRegionItem.setBottom(regionRange[1])
				linearRegionItem.setTop(regionRange[0])
				linearRegionItem.setLeft(self.constrain[0])
				linearRegionItem.setRight(self.constrain[1])
		# if limits is set to None
		elif(self.constrain is None):    
			if(self.orientation == 'vertical'):
				length = linearRegionItem.height()
				linearRegionItem.setBottom(linearRegionItem.top() + length * self.span[1])
				linearRegionItem.setTop(linearRegionItem.top() + length * self.span[0])
				linearRegionItem.setLeft(regionRange[0])
				linearRegionItem.setRight(regionRange[1])
			else:
				linearRegionItem.setBottom(regionRange[1])
				linearRegionItem.setTop(regionRange[0])
				length = linearRegionItem.width()
				linearRegionItem.setLeft(linearRegionItem.left() + length * self.span[0])
				linearRegionItem.setRight(linearRegionItem.left() + length * self.span[1])

		linearRegionItem = linearRegionItem.normalized()
		return linearRegionItem
