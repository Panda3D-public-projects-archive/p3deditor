from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

class EventHandler(DirectObject):
	def __init__(self):
		self.accept("add PointLight",self.addPointLight)
		self.accept("add DirectionalLight",self.addDirectionalLight)
		self.accept("addobject", self.addObject)
	
	def addObject(self,filepath):
		myObjectManager.addObject(filepath)
		messenger.send("refresh scenetree")
	
	def addPointLight(self):
		myObjectManager.addPointLight()
		messenger.send("refresh scenetree")
	
	def addDirectionalLight(self):
		myObjectManager.addDirectionalLight()
		messenger.send("refresh scenetree")
