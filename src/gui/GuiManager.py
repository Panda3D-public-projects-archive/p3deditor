from direct.showbase.DirectObject import DirectObject

class GuiManager(DirectObject):
 
	def __init__(self):
		pass
	
	'''
	Simply telling GUI selection has changed and sending pointers to delegates.
	'''
	def noneObjSelected(self):
		messenger.send("refresh noneproptable")
	
	def oneObjSelected(self, obj):
		messenger.send("refresh oneproptable", [obj])
		
	def manyObjSelected(self,objlist):
		messenger.send("refresh manyproptable", objlist)
