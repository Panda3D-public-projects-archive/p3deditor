from direct.showbase.DirectObject import DirectObject

import subprocess, os

#TODO: implement
class ThirdPartyToolsManager(DirectObject):
	def __init__(self):
		self.accept("third-party", self.run)
		
		#storing previous path in order not to mess up everything
		self.savedPath = os.getcwd()
	
	#you can add here supported types of plugins
	def run(self, tool, params):
		if tool == "terrain":
			self.runTerrain(params)
	
	def runTerrain(self, params):
		print "INFO: running terrain editor"
		print "cls: python main.py "+params
		
		os.chdir("external_tools/sleep_source")
		subprocess.call(["python main.py "+params], shell=True)
		os.chdir(self.savedPath)
		messenger.send("refresh-terrain-pool")
