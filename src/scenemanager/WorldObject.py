from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

class WorldObject(DirectObject):
	def __init__(self):
		#setting inner object proprierties
		self.isSelected = False
	
	def setSelected(self,v):
		#setting variable selection
		self.isSelected = v
		
		#callback functions
		if v == True:
			self.selectionEvent()
		else:
			self.deselectionEvent()
	
	def isSelected(self):
		return self.isSelected
	
	#callback of setSelected()
	def selectionEvent(self):
		self.model.showBounds()
		self.model.setTag("collision","0")
	
	#callback of setSelected()
	def deselectionEvent(self):
		self.model.hideBounds()
		self.model.setTag("collision","1")
	
	#reparenting model to mainNode scene
	def setParent(self,node):
		self.model.reparentTo(node)
