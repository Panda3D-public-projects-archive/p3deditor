# -*- coding: utf-8-*- 

#import direct.directbase.DirectStart 
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject 
from panda3d.core import *
from direct.task import Task

from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from mainwindow import Ui_MainWindow

#world object management
from manager import *
#camera management
from camera import *
#gui
from gui import *
#input management
from inputHandler import InputHandler

#other crazy stuffz
from SceneGraphBrowser import *

import sys,__builtin__

from pandac.PandaModules import loadPrcFileData 
loadPrcFileData("", """
text-encoding utf8
show-frame-rate-meter 1
sync-video #f
""") 

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
	
		# this basically creates an idle task 
		self.timer =  QTimer(self) 
		self.connect( self.timer, SIGNAL("timeout()"), pandaCallback ) 
		self.timer.start(0)
	
class World(ShowBase):	
	def __init__(self):
		ShowBase.__init__(self)
		
		#starting all base methods
		__builtin__.myApp = self
		__builtin__.myObjectManager = ObjectManager()
		__builtin__.myGui = MyGui()
		__builtin__.myCamera = MyCamera()
		__builtin__.myInputHandler = InputHandler()
		
		#default config when just opened
		myCamera.mm.showMouse()
		myCamera.setUtilsActive()
		self.defineBaseEvents()
		
		self.mainScene = render.attachNewNode("mainScene")
	
	def pandaCallback(self):
		taskMgr.step()
	
	def getSceneNode(self):
		return self.mainScene
	
	def exportScene(self):
		s.refresh()
		
	def defineBaseEvents(self):
		base.accept("escape", sys.exit)

w = World()

app = QApplication(sys.argv)
q = QTTest(w.pandaCallback)
q.show()
s = SceneGraphWindow()
s.show()
app.exec_()

w.run()
