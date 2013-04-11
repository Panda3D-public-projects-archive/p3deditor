# -*- coding: utf-8-*- 

#import direct.directbase.DirectStart 
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject 
from panda3d.core import *
from direct.task import Task

# a bit of qts
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 

#world object management
from src.scenemanager.ObjectManager import ObjectManager

#camera management
from src.camera.CameraManager import CameraManager

#gui imports
from src.gui.QTTest import QTTest
from src.gui.GuiManager import GuiManager
from src.gui.SceneGraphBrowser import SceneGraphBrowser

#input management
from src.input.InputHandler import InputHandler
from src.input.EventHandler import EventHandler

import sys,__builtin__

from pandac.PandaModules import loadPrcFileData 
loadPrcFileData("", """
text-encoding utf8
show-frame-rate-meter 1
sync-video #f
""") 
	
class World(ShowBase):	
	def __init__(self):
		ShowBase.__init__(self)
		
		#starting all base methods
		__builtin__.myApp = self
		__builtin__.myObjectManager = ObjectManager()
		__builtin__.myGui = GuiManager()
		__builtin__.myCamera = CameraManager()
		__builtin__.myInputHandler = InputHandler()
		__builtin__.myEventHandler = EventHandler()
		
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

# left panel
q = QTTest(w.pandaCallback)
q.show()

# right panel
s = SceneGraphBrowser()
s.show()

app.exec_()

w.run()
