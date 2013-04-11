from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

'''
Possible camera states:
static : not moving and do not react from mouse input
fly	: used to fly throught the world
place  : placing an object (not moving)

note that 'place' status is equivalent to static for camera side
'''

class MouseCollider:
	def __init__(self):
		# collision handler
		self.picker = CollisionTraverser()
		self.pq     = CollisionHandlerQueue()

		self.pickerNode = CollisionNode('mouseRay')
		self.pickerNP = camera.attachNewNode(self.pickerNode)
		self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
		self.pickerRay = CollisionRay()
		self.pickerNode.addSolid(self.pickerRay)
		self.picker.addCollider(self.pickerNP, self.pq)
		#uncomment for debugging purpose
		#self.picker.showCollisions(render)
	
	def pickPointOnSurface(self):
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())

			self.picker.traverse(render)
			
			if self.pq.getNumEntries() > 0:
				# This is so we get the closest object
				self.pq.sortEntries()
				numEntries = self.pq.getNumEntries()
				for numEntry in range(numEntries):
					entry = self.pq.getEntry(numEntry)
					n = entry.getIntoNodePath()
					a = n.findNetTag("collision")
					if a.getTag("collision") != "0":
						p = entry.getSurfacePoint(render)
						r = entry.getSurfaceNormal(render)
						
						return [p,r]
				return None
			return None
		else:
			return None
					
		'''		
			n = self.pq.getEntry(0).getIntoNodePath()
			if n.getPythonTag("collision") != 0:
				p = self.pq.getEntry(0).getSurfacePoint(render)
				r = self.pq.getEntry(0).getSurfaceNormal(render)
			return [p,r]
		else:
			return None
	'''
