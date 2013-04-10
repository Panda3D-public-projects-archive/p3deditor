from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

'''
This class is used to move camera WASD in FPS style
'''

class KeyboardMover(DirectObject):
	def __init__(self):
		#ballancer
		self.scrollSpeed = 2
		#moving camera vars
		self.pressedUp = False
		self.pressedDown = False
		self.pressedLeft = False
		self.pressedRight = False
		self.pressedFUp = False
		self.pressedFDown = False
		#setting up keys
		keys = ["w","s","a","d","t","g"]
		self.setupKeys(keys)
	
	def moveCamera(self,task):
		dt = globalClock.getDt()
		if self.pressedUp == True:
			camera.setY(camera, self.scrollSpeed*10*dt)
		if self.pressedDown == True:
			camera.setY(camera, -1*self.scrollSpeed*10*dt)
		if self.pressedLeft == True:
			camera.setX(camera, -1*self.scrollSpeed*10*dt)
		if self.pressedRight == True:
			camera.setX(camera, self.scrollSpeed*10*dt)
		if self.pressedFUp == True:
			camera.setZ(camera, self.scrollSpeed*10*dt)
		if self.pressedFDown == True:
			camera.setZ(camera, -1*self.scrollSpeed*10*dt)
		return Task.cont
	
	def setUnactive(self):
		self.ignoreAll()
		taskMgr.remove("keyboardMoverTask")
	
	def setActive(self):
		self.accept(self.up, self.pressKey, ["up"])
		self.accept(self.down, self.pressKey, ["down"])
		self.accept(self.left, self.pressKey, ["left"])
		self.accept(self.right, self.pressKey, ["right"])
		self.accept(self.FUp, self.pressKey, ["fup"])
		self.accept(self.FDown, self.pressKey, ["fdown"])
		self.accept(self.up+"-up", self.releaseKey, ["up"])
		self.accept(self.down+"-up", self.releaseKey, ["down"])
		self.accept(self.left+"-up", self.releaseKey, ["left"])
		self.accept(self.right+"-up", self.releaseKey, ["right"])
		self.accept(self.FUp+"-up", self.releaseKey, ["fup"])
		self.accept(self.FDown+"-up", self.releaseKey, ["fdown"])
		#self.ignore()
		taskMgr.add(self.moveCamera, "keyboardMoverTask")
	
	def releaseKey(self,key):
		if key == "up":
			self.pressedUp = False
		if key == "down":
			self.pressedDown = False
		if key == "left":
			self.pressedLeft = False
		if key == "right":
			self.pressedRight = False
		if key == "fup":
			self.pressedFUp = False
		if key == "fdown":
			self.pressedFDown = False
	
	def pressKey(self,key):
		if key == "up":
			self.pressedUp = True
		if key == "down":
			self.pressedDown = True
		if key == "left":
			self.pressedLeft = True
		if key == "right":
			self.pressedRight = True
		if key == "fup":
			self.pressedFUp = True
		if key == "fdown":
			self.pressedFDown = True
	
	def getKeys(self):
		keys = [self.up, self.down, self.left, self.right, self.FUp, self.FDown]
		return keys
	
	def setupKeys(self,keys):
		self.up = keys[0]
		self.down = keys[1]
		self.left = keys[2]
		self.right = keys[3]
		self.FUp = keys[4]
		self.FDown = keys[5]
