from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

from StaticObject import StaticObject

class DirectionalLightObject(StaticObject):
	def __init__(self):
		#executing parent class constructor
		StaticObject.__init__(self)
		
		#loading specific model for light
		self.loadModel("models/pointlight.egg")
		self.model.setPos(base.camera,0,10,0)
		self.model.reparentTo(myApp.getSceneNode())
		self.model.setLightOff()
		
		self.plight = DirectionalLight('directionalLight')
		self.plight.setColor(VBase4(1, 1, 1, 1))
		#self.plight.setLens(PerspectiveLens())
		#self.plight.setShadowCaster(True)
		self.plnp = self.model.attachNewNode(self.plight)
		render.setLight(self.plnp)
		
		#setting type
		self.setType("DirectionalLightObject")
		
		#manually overwriting initial name
		self.setName("directionallight")
	
	#overwriting setName virtual method
	def setName(self,s):
		ext = s.split(".")[-1]
		
		#forcing egg extension
		if len(ext)>0:
			if ext != "dlight":
				self.model.setName(s+".dlight")
			else:
				self.model.setName(s)
	
	def getNodePath(self):
		return self.plnp
	
	def getPandaNode(self):
		return self.plight
	
	#override of virtual method
	def loadModel(self,file):
		#loading model egg file
		self.model = loader.loadModel(file)
	
	def remove(self):
		#deleting light
		render.clearLight(self.plnp)
		self.plnp.remove()
		#first remove it from camera
		myCamera.getSelectionTool().removeObject(self)
		#then release memory
		self.model.remove()
