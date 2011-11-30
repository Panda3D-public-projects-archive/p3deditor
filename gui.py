
from direct.task import Task
from direct.showbase.DirectObject import DirectObject

from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from mainwindow import Ui_MainWindow

import sys, os, string


class QTTest(QMainWindow): 
	def __init__(self,pandaCallback): 
		QMainWindow.__init__(self)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		
		fsModel = QFileSystemModel()
		fsModel.setRootPath(QDir.currentPath())
		
		self.ui.eggPool.setModel(fsModel)
		self.ui.eggPool.setRootIndex(fsModel.index(QDir.currentPath()+"/dataset"))
		#hiding everything execept for filename
		self.ui.eggPool.hideColumn(1)
		self.ui.eggPool.hideColumn(2)
		self.ui.eggPool.hideColumn(3)
		self.ui.eggPool.setHeaderHidden(True)
		
		self.ui.eggPool.activated.connect(self.ping)
		
		# this basically creates an idle task 
		self.timer =  QTimer(self) 
		self.connect( self.timer, SIGNAL("timeout()"), pandaCallback ) 
		self.timer.start(0)
	
	def ping(self):
		print "piripiriping!"

class MyGui(DirectObject):
 
	def __init__(self):
		pass