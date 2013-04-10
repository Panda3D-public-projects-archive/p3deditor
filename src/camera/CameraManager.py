from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

from KeyboardModifiers import KeyboardModifiers
from KeyboardMover import KeyboardMover
from MouseMover import MouseMover
from SelectionTool import SelectionTool
from MouseCollider import MouseCollider

class CameraManager(DirectObject):
	def __init__(self):
		#keyboard/mouse mover
		self.km = KeyboardMover()
		self.mm = MouseMover()
		#self.ps = PropSet()
		self.st = SelectionTool()
		self.mc = MouseCollider()
		#disabling mouse by default
		base.disableMouse()
		#setting status
		self.state = "static"
		
		self.setNearFar(1.0,10000)
		self.setFov(75)
	
	def getKeyboardMover(self):
		return self.km
	
	def getMouseMover(self):
		return self.km
	
	def getSelectionTool(self):
		return self.st
	
	def getFov(self):
		return base.camLens.getFov()
	
	def setNearFar(self,v1,v2):
		base.camLens.setNearFar(v1,v2)
	
	def setFov(self,value):
		base.camLens.setFov(value)

	'''
	This is an interface method used to switch between fly and static 
	modes dinamically through a simple string
	'''
	def getSelected(self):
		return self.st.listSelected
	
	def setState(self,s):
		#if there is a real change in camera state
		if s != self.state:
			#actually change state
			if s == "fly":
				#re-enabling all gui elements
				self.mm.setActive()
				self.km.setActive()
				self.st.setUnactive()
			if s == "static":
				self.mm.setUnactive()
				self.km.setUnactive()
				self.st.setActive()
			#changing state variable at the end of method execution
			self.state = s
	
	def setUtilsActive(self):
		self.accept("tab", self.toggleView)
		#self.accept("f", self.ps.toggleFullscreen)
	
	def setUtilsUnactive(self):
		self.ignore("tab")
		self.ignore("f")
	
	def toggleState(self):
		if self.state == "static":
			self.setState("fly")
		else:
			self.setState("static")
	
	def toggleView(self):
		if self.getState() == "fly":
			#myGui.showAll()  to be removed soon
			myInputHandler.setActive()
		if self.getState() == "static":
			#myGui.hideAll()  to be removed soon
			myInputHandler.setInactive()
		#switching camera in any case
		self.toggleState()
	
	def getState(self):
		return self.state
