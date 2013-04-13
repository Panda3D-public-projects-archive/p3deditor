from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

from KeyboardModifiers import KeyboardModifiers

import libpanda, math

class SelectionTool(DirectObject):
	def __init__(self, listConsideration=[]):
		#active and not
		self.active = True
		self.kmod = KeyboardModifiers()
		#Create a selection window using cardmaker
		#We will use the setScale function to dynamically scale the quad to the appropriate size in UpdateSelRect
		temp = CardMaker('')
		temp.setFrame(0, 1, 0, 1)
		#self.npSelRect is the actual selection rectangle that we dynamically hide/unhide and change size
		self.npSelRect = render2d.attachNewNode(temp.generate())
		self.npSelRect.setColor(1,1,0,.2)
		self.npSelRect.setTransparency(1)
		self.npSelRect.hide()
		LS = LineSegs()
		LS.moveTo(0,0,0)
		LS.drawTo(1,0,0)
		LS.drawTo(1,0,1)
		LS.drawTo(0,0,1)
		LS.drawTo(0,0,0)
		self.npSelRect.attachNewNode(LS.create())
		self.listConsideration = listConsideration
		self.listSelected = []
		self.listLastSelected = []
		
		self.pt2InitialMousePos = (-12, -12)
		self.pt2LastMousePos = (-12, -12)
		
		####----Used to differentiate between group selections and point selections
		#self.booMouseMoved  = False
		self.fFovh, self.fFovv = base.camLens.getFov()
		
		####--Used to control how frequently update_rect is updated;
		self.fTimeLastUpdateSelRect = 0
		self.fTimeLastUpdateSelected = 0
		self.UpdateTimeSelRect = 0.015
		self.UpdateTimeSelected = 0.015
		
		####------Register the left-mouse-button to start selecting
		self.accept("mouse1", self.OnStartSelect)
		self.accept("control-mouse1", self.OnStartSelect)
		self.accept("mouse1-up", self.OnStopSelect)
		self.taskUpdateSelRect = 0
	
	def removeObject(self,o):
		if o in self.listConsideration:
			self.listConsideration.remove(o)
		if o in self.listSelected:
			#execute deselection object
			self.funcDeselectActionOnObject(o)
			#get rid of it
			self.listSelected.remove(o)
		if o in self.listLastSelected:
			self.listLastSelected.remove(o)
	
	def appendObject(self,o):
		if o not in self.listConsideration:
			self.listConsideration.append(o)
	
	def setActive(self):
		self.active = True
	
	def setUnactive(self):
		self.active = False
	
	def TTest(self):
		print "hello control-mouse1"
	
	#functions executed when every object is selected
	def funcSelectActionOnObject(self, obj):
		obj.selectionEvent()
	
	#functions executed when every object is selected  
	def funcDeselectActionOnObject(self, obj):
		obj.deselectionEvent()
	
	#force selection of objects in the scene graph by pattern
	def forceSelection(self, pattern):
		myCamera.st.clearSelection()
		
		print "forcing selection to", pattern 
		
		for i in self.listConsideration:
			if i.getName() == pattern: #force selection
				self.funcSelectActionOnObject(i)
				self.listSelected.append(i)
		
		self.selectionHasChanged()
	
	#call this function when you know selection has changed
	def selectionHasChanged(self):
		if len(self.listSelected) > 1:
			myGui.manyObjSelected(self.listSelected)
		if len(self.listSelected) == 0:
			myGui.noneObjSelected()
		if len(self.listSelected) == 1:
			myGui.oneObjSelected(self.listSelected[0])
	
	#used to clear selection by code
	def clearSelection(self):
		for j in self.listSelected[:]:
			if j in self.listSelected:
				#execute deselection object
				self.funcDeselectActionOnObject(j)
				#get rid of it
				self.listSelected.remove(j)
			if j in self.listLastSelected:
				self.listLastSelected.remove(j)
	
	def OnStartSelect(self):
		if not self.active:
			return
		if not base.mouseWatcherNode.hasMouse():
			return
		self.booMouseMoved = False
		self.booSelecting = True
		self.pt2InitialMousePos = Point2(base.mouseWatcherNode.getMouse())
		self.pt2LastMousePos = Point2(self.pt2InitialMousePos)
		self.npSelRect.setPos(self.pt2InitialMousePos[0], 1, self.pt2InitialMousePos[1])
		self.npSelRect.setScale(1e-3, 1, 1e-3)
		self.npSelRect.show()
		self.taskUpdateSelRect = taskMgr.add(self.UpdateSelRect, "UpdateSelRect")
		self.taskUpdateSelRect.lastMpos = None
		
	def OnStopSelect(self):
		if not self.active:
			return
		if not base.mouseWatcherNode.hasMouse():
			return
		if self.taskUpdateSelRect != 0:
			taskMgr.remove(self.taskUpdateSelRect)
		self.npSelRect.hide()
		self.booSelecting = False
		#If the mouse hasn't moved, it's a point selection
		if (abs(self.pt2InitialMousePos[0] - self.pt2LastMousePos[0]) <= .01) & (abs(self.pt2InitialMousePos[1] - self.pt2LastMousePos[1]) <= .01):
			objTempSelected = 0
			fTempObjDist = 2*(base.camLens.getFar())**2
			for i in self.listConsideration:
				if type(i.getModel()) != libpanda.NodePath:
					raise 'Unknown objtype in selection'
				else:
					sphBounds = i.getModel().getBounds()
					#p3 = base.cam.getRelativePoint(render, sphBounds.getCenter())
					p3 = base.cam.getRelativePoint(i.getModel().getParent(), sphBounds.getCenter())
					r = sphBounds.getRadius()
					screen_width = r/(p3[1]*math.tan(math.radians(self.fFovh/2)))
					screen_height = r/(p3[1]*math.tan(math.radians(self.fFovv/2)))
					p2 = Point2()
					base.camLens.project(p3, p2)
					#If the mouse pointer is in the "roughly" screen-projected bounding volume
					if (self.pt2InitialMousePos[0] >= (p2[0] - screen_width/2)):
						if (self.pt2InitialMousePos[0] <= (p2[0] + screen_width/2)):
							if (self.pt2InitialMousePos[1] >= (p2[1] - screen_height/2)):
								if (self.pt2InitialMousePos[1] <= (p2[1] + screen_height/2)):
									#We check the obj's distance to the camera and choose the closest one
									dist = p3[0]**2+p3[1]**2+p3[2]**2 - r**2
									if dist < fTempObjDist:
										fTempObjDist = dist
										objTempSelected = i

			if objTempSelected != 0:
				if self.kmod.booControl:
					self.listSelected.append(objTempSelected)
				else:
					for i in self.listSelected:
						self.funcDeselectActionOnObject(i)
				self.listSelected = [objTempSelected]
				self.funcSelectActionOnObject(objTempSelected)
			else:
				for i in self.listSelected[:]:
					self.funcDeselectActionOnObject(i)
					self.listSelected.remove(i)
		#after all this check gui changes needed
		self.selectionHasChanged()

	def UpdateSelRect(self, task): 
		if not self.active:
			return
		#Make sure we have the mouse 
		if not base.mouseWatcherNode.hasMouse(): 
			return Task.cont 
		mpos = base.mouseWatcherNode.getMouse() 
		t = globalClock.getRealTime() 
		#First check the mouse position is different 
		if self.pt2LastMousePos != mpos: 
			self.booMouseMoved = True 
			#We only need to check this function every once in a while 
			if (t - self.fTimeLastUpdateSelRect) > self.UpdateTimeSelRect: 
				self.fTimeLastUpdateSelRect =  t 
				self.pt2LastMousePos = Point2(mpos) 
				 
				#Update the selection rectange graphically 
				d = self.pt2LastMousePos - self.pt2InitialMousePos 
				self.npSelRect.setScale(d[0] if d[0] else 1e-3, 1, d[1] if d[1] else 1e-3) 
						
		if (abs(self.pt2InitialMousePos[0] - self.pt2LastMousePos[0]) > .01) & (abs(self.pt2InitialMousePos[1] - self.pt2LastMousePos[1]) > .01): 
			if (t - self.fTimeLastUpdateSelected) > self.UpdateTimeSelected: 
				#A better way to handle a large number of objects is to first transform the 2-d selection rect into 
				#its own view fustrum and then check the objects in world space. Adding space correlation/hashing 
				#will make it go faster. But I'm lazy. 
				self.fTimeLastUpdateSelected = t 
				self.listLastSelected = self.listSelected 
				self.listSelected = [] 
				#Get the bounds of the selection box 
				fMouse_Lx = min(self.pt2InitialMousePos[0], self.pt2LastMousePos[0]) 
				fMouse_Ly = max(self.pt2InitialMousePos[1], self.pt2LastMousePos[1]) 
				fMouse_Rx = max(self.pt2InitialMousePos[0], self.pt2LastMousePos[0]) 
				fMouse_Ry = min(self.pt2InitialMousePos[1], self.pt2LastMousePos[1]) 
				for i in self.listConsideration: 
					#Get the loosebounds of the nodepath 
					sphBounds = i.getModel().getBounds() 
					#Put the center of the sphere into the camera coordinate system 
					#p3 = base.cam.getRelativePoint(render, sphBounds.getCenter()) 
					p3 = base.cam.getRelativePoint(i.getModel().getParent(), sphBounds.getCenter()) 
					#Check if p3 is in the view fustrum 
					p2 = Point2() 
					if base.camLens.project(p3, p2): 
						if (p2[0] >= fMouse_Lx) & (p2[0] <= fMouse_Rx) & (p2[1] >= fMouse_Ry) & (p2[1] <= fMouse_Ly): 
							self.listSelected.append(i) 
							self.funcSelectActionOnObject(i) 
				for i in self.listLastSelected: 
					if not self.kmod.booControl: 
						if i not in self.listSelected: 
							self.funcDeselectActionOnObject(i) 
							pass
					else: 
						self.listSelected.append(i) 
		
		return Task.cont
