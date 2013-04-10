from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

from WorldObject import WorldObject

class StaticObject(WorldObject):
	def __init__(self,file = False):
		#calling parent method
		WorldObject.__init__(self)
		
		#private? xD
		self.originalFilename = file
		
		#ppppppppppablic!
		self.locking = False
		
		if file != False:
			self.loadModel(file) #just down here :P
	
	def getFilename(self):
		return self.originalFilename
	
	def getName(self):
		return self.model.getName()
	
	def setName(self,s):
		self.model.setName(s)
	
	def loadPlaceHolder(self,file):
		#hiding real model
		if self.model != False:
			self.model.hide()
		#inserting placeholder
		self.placeholder = loader.loadModel("dataset/"+file)
		self.placeholder.reparentTo(self.model)
	
	def unloadPlaceHolder(self):
		if self.model != False:
			self.model.show()
		self.placeholder.remove()

	def loadModel(self,file):
		#loading model egg file
		self.model = loader.loadModel("dataset/"+file)
		self.model.reparentTo(myApp.getSceneNode())
		#storing type of object in scene
		self.type = "StaticObject"
		#storing options such as lightning
		self.lightning = True
		self.shaders = False
		self.wireframe = False
		self.hidden = False
	
	def getModel(self):
		return self.model
	
	def setLocking(self,v):
		self.locking = v
		#real control is done in InputHandler
	
	def getLocking(self):
		return self.locking
	
	def getWireframe(self):
		isWireframed = self.model.getRenderMode()
		if isWireframed == 0 or isWireframed == 1:
			isWireframed = False
		else:
			isWireframed = True
		return isWireframed
	
	def setLightning(self,v):
		self.lightning = v
		if v == True:
			#setting all lights on
			for l in myObjectManager.lightList:
				self.model.setLight(l.getNodePath())
		else:
			#set all lights off
			self.model.setLightOff()
	
	def getLightning(self):
		return self.lightning
	
	def setShaders(self,v):
		self.shaders = v
		if v == True:
			self.model.setShaderAuto()
		else:
			self.model.setShaderOff()

	def getShaders(self):
		return self.shaders
	
	def setHidden(self,v):
		self.hidden = v
		if v == True:
			pass #needed to be written with a placeholder or something
		else:
			pass #lululul
			
	def getHidden(self):
		return self.hidden

	#warn: not advised to directly set the type
	def setType(self,s):
		self.type = s

	def getType(self):
		return self.type
	
	def remove(self):
		#first remove it from camera
		myCamera.getSelectionTool().removeObject(self)
		#then release memory
		self.model.remove()
