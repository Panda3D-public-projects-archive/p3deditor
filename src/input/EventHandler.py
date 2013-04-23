from direct.showbase.DirectObject import DirectObject
from direct.filter.CommonFilters import CommonFilters
from pandac.PandaModules import *

class EventHandler(DirectObject):
	def __init__(self):
		self.accept("add PointLight",self.addPointLight)
		self.accept("add DirectionalLight",self.addDirectionalLight)
		
		#general purpose items
		self.accept("addobject", self.addObject)
		self.accept("addterrain", self.addTerrain)
	
	def togglePerPixelLighting(self, checked):
		if checked == True:
			render.setShaderAuto(True)
		else:
			render.setShaderAuto(False)
	
	def toggleAmbientOcclusion(self, checked):
		filters = CommonFilters(base.win, base.cam)
		
		if checked == True:
			filters.setAmbientOcclusion()
		else:
			filters.delAmbientOcclusion()
	
	def toggleToonShading(self, checked):
		filters = CommonFilters(base.win, base.cam)
		
		if checked == True:
			filters.setCartoonInk()
		else:
			filters.delCartoonInk()
	
	def addObject(self,filepath):
		myObjectManager.addObject(filepath)
		messenger.send("refresh scenetree")
	
	def addTerrain(self,filepath):
		myObjectManager.addTerrain(filepath)
		messenger.send("refresh scenetree")
		
	def addPointLight(self):
		myObjectManager.addPointLight()
		messenger.send("refresh scenetree")
	
	def addDirectionalLight(self):
		myObjectManager.addDirectionalLight()
		messenger.send("refresh scenetree")
