
from direct.task import Task
from direct.showbase.DirectObject import DirectObject

from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from mainwindow import Ui_MainWindow

from utilities import *

import sys, os, string


class QTTest(QMainWindow): 
	def __init__(self,pandaCallback): 
		QMainWindow.__init__(self)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		
		self.fillPool()
		self.ui.eggPool.itemDoubleClicked.connect(self.sendNewModel)
		
		# this basically creates an idle task 
		self.timer =  QTimer(self) 
		self.connect( self.timer, SIGNAL("timeout()"), pandaCallback ) 
		self.timer.start(0)
	
	def fillPool(self):
		self.ui.eggPool.clear()
		files = Utilities.getFilesIn("dataset")
		for e in files:
			self.ui.eggPool.addItem(e)
	
	def sendNewModel(self,item):
		filepath = str(item.text())  #casting due to compatibility issues
		myObjectManager.addObject(filepath)
		

class MyGui(DirectObject):
 
	def __init__(self):
		pass
	
	#
	# TODO STUFF
	#
	def noneObjSelected(self):
		print "TODO: implement MyGui.noneObjSelected()"
	
	def oneObjSelected(self):
		print "TODO: implement MyGui.oneObjSelected()"
		
	def manyObjSelected(self):
		print "TODO: implement MyGui.manyObjSelected()"