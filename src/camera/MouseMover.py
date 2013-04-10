from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

'''
This class is use to move mouse when in FPS (fly) mode
setActive() -> used to activate FPS mouse slide
setUnactive() -> inactivate FPS behaviour
'''

class MouseMover(DirectObject):
	def __init__(self):
		#camera rotation settings
		self.heading = 0
		self.pitch = 0
		#used to restore last mouse position in editor
		self.lastCoo = []
	
	def flyCamera(self,task):
		# figure out how much the mouse has moved (in pixels)
		md = base.win.getPointer(0)
		x = md.getX()
		y = md.getY()
		if base.win.movePointer(0, 300, 300):
			self.heading = self.heading - (x - 300) * 0.1
			self.pitch = self.pitch - (y - 300) * 0.1
		if (self.pitch < -85): self.pitch = -85
		if (self.pitch >  85): self.pitch =  85
		base.camera.setH(self.heading)
		base.camera.setP(self.pitch)
		return Task.cont
	
	def hidMouse(self):
		#hiding mouse
		props = WindowProperties()
		props.setCursorHidden(True) 
		base.win.requestProperties(props)
	
	def showMouse(self):
		props = WindowProperties()
		props.setCursorHidden(False) 
		base.win.requestProperties(props)
		
	def setActive(self):
		#hiding mouse
		self.hidMouse()
		#storing infos
		md = base.win.getPointer(0)
		x = md.getX()
		y = md.getY()
		self.lastCoo = [x,y]
		#start activating this shit
		base.win.movePointer(0,300,300)
		taskMgr.add(self.flyCamera, "mouseMoverTask")
	
	def setUnactive(self):
		#showing mouse
		self.showMouse()
		#then removing task and resetting pointer to previous position
		taskMgr.remove("mouseMoverTask")
		base.win.movePointer(0,int(self.lastCoo[0]),int(self.lastCoo[1]))
