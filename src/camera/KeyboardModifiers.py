from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

class KeyboardModifiers(DirectObject): 
	def __init__(self): 
		self.booAlt = False 
		self.booControl = False 
		self.booShift = False 
		self.accept("alt", self.OnAltDown) 
		self.accept("alt-up", self.OnAltUp) 
		self.accept("control", self.OnControlDown) 
		self.accept("control-up", self.OnControlUp) 
		self.accept("shift", self.OnShiftDown) 
		self.accept("shift-up", self.OnShiftUp) 
	 
	def OnAltDown(self): 
		self.booAlt = True 
		
	def OnAltUp(self): 
		self.booAlt = False 
		
	def OnControlDown(self): 
		self.booControl = True 
	 
	def OnControlUp(self): 
		self.booControl = False 
		
	def OnShiftDown(self): 
		self.booShift = True 
		
	def OnShiftUp(self): 
		self.booShift = False 
