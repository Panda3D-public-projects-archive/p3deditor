from direct.showbase.DirectObject import DirectObject 
from panda3d.core import *

from PyQt4.QtCore import * 
from PyQt4.QtGui import * 

#custom imports
from SceneGraphBrowserUi import Ui_sceneGraphBrowser

from utilities import *

'''
Scene graph window class
'''
class SceneGraphWindow(QMainWindow): 
	def __init__(self): 
		QMainWindow.__init__(self)
		self.ui = Ui_sceneGraphBrowser()
		self.ui.setupUi(self)
		
		self.ui.sgTree.setHeaderHidden(True)
		
		self.ui.sgTree.itemDoubleClicked.connect(self.changeSelection)
	
	def changeSelection(self):
		myCamera.st.clearSelection()
	
	def eraseAll(self):
		self.ui.sgTree.clear()
	
	def addItem(self):
		pass
	
	def refresh(self):
		#clear up all the scene
		self.eraseAll()
		
		#adding all the others
		sga = SceneGraphAnalyzer(myApp.mainScene,self.ui.sgTree)
		sga.generate()
		
'''
Object that analyze and build up the scene graph in
the right (upper) window
'''
class SceneGraphAnalyzer:
	def __init__(self,rootNode,tree):
		self.level = 0 #this means we're at the root of the scene
		self.rootNode = rootNode #storing our temporary root node
		self.tree = tree
		self.parent = None
		
	def generate(self):
		
		#adding root scene node
		nn = QTreeWidgetItem()
		nn.setText(0,QString("mainScene"))
		self.tree.addTopLevelItem(nn)
		
		self.parent = nn
		self.browse(self.rootNode)
	
	#
	# recursive function that fills the scene node
	# limited at .egg structures
	#
	def browse(self,node):
		for child in node.getChildren():
			
			#adding root scene node
			nn = QTreeWidgetItem(self.parent)
			nn.setText(0,QString(child.getName()))
			
			lastParent = self.parent
			
			self.parent = nn
			# 
			# checking file extension in order to go to deeper than egg model structure
			# 
			if Utilities.getFileExtension(child.getName()) != "egg":
				self.browse(child)
			
			self.parent = lastParent

