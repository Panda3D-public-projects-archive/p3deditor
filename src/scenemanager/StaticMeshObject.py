from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

from StaticObject import StaticObject

class StaticMeshObject(StaticObject):
	def __init__(self,file=False):
		StaticObject.__init__(self,file)
		#defining specific mesh object methods
		self.setType("StaticMeshObject")
