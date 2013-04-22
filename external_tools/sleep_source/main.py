#
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# Wezu <grzechotnik1984@gmail.com> wrote this editor. As long as you retain this
# notice you can do whatever you want with this stuff. If we meet some day, 
# and you think this stuff is worth it, you can buy me a beer in return 
# --------------------------------------------------------------------------------
# Claudio Desideri <happy.snizzo@gmail.com> has slightly modified this editor
# in order to work with the p3deditor http://p3deditor.googlecode.com .
# This is used as an external tool called when needed, therefore 
# all work still belongs to original author Wezu.
# If you meet him some day, offer him a beer.
# --------------------------------------------------------------------------------
#

import os
import math
import json
from direct.showbase.AppRunnerGlobal import appRunner
from panda3d.core import Filename
if appRunner: 
    path=appRunner.p3dFilename.getDirname()+'/'
else: 
    path=""
from panda3d.core import *
#loadPrcFileData('','text-default-font Lekton-Regular.ttf')
loadPrcFileData('','text-default-font monkey.ttf')
loadPrcFileData('','sync-video 0')
from direct.showbase.DirectObject import DirectObject
import direct.directbase.DirectStart
from direct.filter.FilterManager import FilterManager
from direct.gui.DirectGui import *



class Editor(DirectObject):
    def __init__(self):
        #got my own mouse controll
        base.disableMouse()  
        #no fps meter, I got icons there!
        base.setFrameRateMeter(False)
        #not much help from the autoshader, turned it off
        #render.setShaderAuto()  
        
        self.font = DGG.getDefaultFont()
        self.font.setPixelsPerUnit(16)
        
        #clean exit
        base.exitFunc = self.onExitCleaup
        
        #I need to keep track of some vaules
        #stupid names? bad design? not needen? Deal with it!
        self.mode=1     #1-resize, 2-color, 3-alpha, 4-rotate
        self.editMode=1 # 1-paint height, 2-paint texture, 3-paint objects       
        self.currentTexLayer=0 #the layer we are currently painting.. if we are painting a texture
        self.textureForLayer=[0,1]  #textures for texture layers
        self.currentBitMask=[0]*32
        self.currentObject=None
        self.currentTag=[]
        self.currentModelName=None
        self.currentRoot=render
        self.numGroups=0
        self.currentZ=0
        self.export=[]
        self.rotateAxis='H'
        self.resizeAxis='All'
        
        #check for resources:
        
        #where the map is saved?
        self.saveName="maps/map"
        i=0
        while os.path.exists(path+self.saveName+str(i)):
            i+=1
        self.saveName+=str(i)        
        os.makedirs(Filename(path+self.saveName).toOsSpecific())
                
        #what model do we have?
        self.models=[]
        dirList=os.listdir(Filename(path+"models/").toOsSpecific())
        for fname in dirList:
            #if not os.path.isdir(fname): #did not work after packing!
            if  Filename(fname).getExtension()=='bam' or Filename(fname).getExtension()=='egg':
                self.models.append(fname)
        
        #what textures do we have?
        self.textures=[]
        dirList=os.listdir(Filename(path+"textures/").toOsSpecific())
        for fname in dirList:
            self.textures.append(fname)
        
        #window properties, for later use and to place gui elements
        #and since I mess with, I can as well add a title
        #setting the size was done before opening the window in version .01-.04
        #since no bloom is used, I can do it here to keep it in one place
        self.wp = base.win.getProperties()
        self.winX = self.wp.getXSize()
        self.winY = self.wp.getYSize()
        wp=WindowProperties()
        wp.setTitle("SLEEP3D by Wezu v.05   ("+str(self.saveName)+")")
        wp.setSize(800,600)
        base.win.requestProperties(wp)
        
        #the plane will bu used to see where the mouse pointer is
        self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 1))
        
        #the visible pointer, it helps to see where "north" is and how high the terrain is
        self.pointer = loader.loadModel("pointer2")
        self.pointer.reparentTo(render)
        self.pointer.setLightOff()
        self.pointer.setColor(0,0,1,0.5)
        self.pointer.setScale(0.7)
        self.pointer.setTransparency(TransparencyAttrib.MAlpha)
        
        #grid - it's a editor, yoy HAVE to have a grid of some sort        
        cm = CardMaker("plane") #will reuse the card maker later
        cm.setFrame(0, 512, 0, 512)        
        self.grid=render.attachNewNode(cm.generate())
        self.grid.lookAt(0, 0, -1)
        gridTexture=loader.loadTexture('grid.png')
        gridTexture.setMinfilter(Texture.FTNearest)
        gridTexture.setMagfilter(Texture.FTNearest)
        self.grid.setTexture(gridTexture)
        self.grid.setTransparency(TransparencyAttrib.MAlpha)
        self.grid.setTexScale(TextureStage.getDefault(), 32, 32, 1)
        self.grid.setZ(1)
        self.grid.setLightOff()
        self.grid.setColor(0,0,0,0.5)
        
        #add all task to the task manager
        taskMgr.add(self.__getMousePos, "_Editor__getMousePos")
        taskMgr.add(self.moveTask, "Move Task")   
        
        #the camera, an extra node will help move it
        self.cameraNode  = NodePath(PandaNode("cameraNode"))
        self.cameraNode.reparentTo(render)
        self.cameraNode.setPos(256, 256, 0)
        base.camera.setPos(256,128, 64)
        base.camera.lookAt(256, 256, 0)
        base.camera.wrtReparentTo(self.cameraNode)        
        self.cameraZoom=50 #will use it later, not only for camera stuff
        
        #camera controls keys
        self.keyMap = { "w" : False,
                        "s" : False,
                        "a" : False,
                        "d" : False, 
                        "q" : False,
                        "e" : False,
                        "r" : False,
                        "f" : False,
                        "z" : False,
                        "x" : False }
        for key in self.keyMap.keys():
            self.accept(key, self.keyMap.__setitem__, [key, True])
            self.accept(key+"-up", self.keyMap.__setitem__, [key, False])          
        
        #other hot-keys    
        self.accept("tab", self.modeTogle, [1])
        self.accept("mouse2", self.modeTogle, [1])
        self.accept("1", self.modeSet, [1])
        self.accept("2", self.modeSet, [2])
        self.accept("3", self.modeSet, [3])
        self.accept("4", self.modeSet, [4])        
        self.accept("wheel_up", self.mouseWheel, [True])
        self.accept("wheel_down", self.mouseWheel, [False])        
        self.accept("mouse1", self.SaveAndUpdate)
        self.accept("escape", self.selectModel, [None])
        
        #terrain setup
        self.terrain = GeoMipTerrain("mySimpleTerrain")
        self.terrain.setHeightfield("img.png")
        self.terrain.setBlockSize(128)
        self.terrain.setMinLevel(2) #0 and 1 looks better, but takes to long to regenerate, 3 looks bad
        self.terrain.setBruteforce(True)
        self.terrain.getRoot().reparentTo(render)
        self.terrain.generate()        
        self.terrain.getRoot().setSz(100)   
        self.terrain.getRoot().setZ(-50)
        
        #some lights
        dlight = DirectionalLight('dlight') 
        dlight.setColor(VBase4(1, 1, 1, 1))        
        dlnp = render.attachNewNode(dlight)
        dlnp.setHpr(0, -70, 0)         
        render.setLight(dlnp)
        alight = AmbientLight('alight')        
        alnp = render.attachNewNode(alight)
        alight.setColor(Vec4(0.4, 0.4, 0.45, 1))
        render.setLight(alnp) 
        
        #the first buffer, will be drawing here
        altRender=NodePath("bufferRender")
        self.altTex=Texture()
        self.altBuffer=base.win.makeTextureBuffer("tex_buffer", 512, 512,self.altTex)
        #the camera for the buffer
        self.altCam=base.makeCamera(win=self.altBuffer)        
        self.altCam.reparentTo(altRender)          
        self.altCam.setPos(256,256,100)                
        self.altCam.setP(-90)                   
        self.lens = OrthographicLens()
        self.lens.setFilmSize(512, 512)  
        self.altCam.node().setLens(self.lens)          
        #plane with the texture, a blank texture for now
        cm.setFrame(0, 512, 0, 512)        
        self.altPlane=altRender.attachNewNode(cm.generate())
        self.altPlane.lookAt(0, 0, -1)
        self.altPlane.setTexture(loader.loadTexture('img.png'))
        self.altPlane.setLightOff()
        self.altPlane.setZ(-1)   
        #the brush 
        cm.setFrame(-16, 16, -16, 16)                
        self.brush=altRender.attachNewNode(cm.generate())
        self.brush.lookAt(0, 0, -1)
        self.brush.setTexture(loader.loadTexture('b0.png'))
        self.brush.setTransparency(TransparencyAttrib.MAlpha)        
        self.brush.setLightOff()
        self.brush.setColor(1, 1, 1, 0.5)
        
        #more buffers, this one is for projecting a "detail" texture 
        self.altTexRender=NodePath("TexbufferRender")     
        self.altTexTex=Texture() 
        self.altTexTex.setMagfilter(Texture.FTLinearMipmapLinear)
        self.altTexTex.setMinfilter(Texture.FTLinearMipmapLinear)  #todo: is this needed?      
        self.altTexTex.setWrapU(Texture.WMBorderColor  )
        self.altTexTex.setWrapV(Texture.WMBorderColor  )
        self.altTexTex.setBorderColor(Vec4(0.5,0.5,0.5,0))        
        self.altTexBuffer=base.win.makeTextureBuffer("tex_buffer2", 2048, 2048, self.altTexTex)        
        
        self.texCam=base.makeCamera(win=self.altTexBuffer)        
        self.texCam.reparentTo(self.altTexRender)          
        self.texCam.setPos(256,256,100)                
        self.texCam.setP(-90)  
        self.texLens = OrthographicLens()
        self.texfilmSize=400 #will need this later 
        self.texLens.setFilmSize(self.texfilmSize, self.texfilmSize)      
        self.texCam.node().setLens(self.texLens) 
        
        #view the buffers
        #base.bufferViewer.toggleEnable()
        #base.bufferViewer.setPosition("lrcorner")
        #base.bufferViewer.setCardSize(0.5, 0.0)   
        
        #didn't like the grayscale map - made a shader to turn it red-green
        #it just take the red color, puts (1-red) in the gren channel, 0 and 1 in blue and alpha 
        self.manager = FilterManager(self.altBuffer, self.altCam)
        self.tex = Texture()
        self.quad = self.manager.renderSceneInto(colortex=self.tex)
        self.quad.setShader(Shader.load("myfilter.sha"))
        self.quad.setShaderInput("tex", self.tex)                
        
        #some more stuff needed for texture painting    
        
        #2 texture planes are made by default 
        #could be moved to a function, but I'm to lazy, this also works fine
        self.texturePlane=loader.loadModel("plane") 
        self.texturePlane.setTransparency(TransparencyAttrib.MDual)        
        self.TexPlane=[]
        self.TexPlane.append(self.texturePlane.copyTo(self.altTexRender))        
        self.TexPlane[0].setTexture(self.TexPlane[0].findTextureStage('Tex2'), loader.loadTexture(path+'textures/'+self.textures[0]), 1)        
        self.TexPlane[0].setZ(-1)    #the Z is a hack, to avoid confilts with the texBrush, depth offset didn't work here    
        
        self.TexPlane.append(self.texturePlane.copyTo(self.altTexRender))  
        temp_textures=Texture()
        temp_textures.read('full_mask.png')
        temp_textures.setFormat(Texture.FAlpha)  
        self.TexPlane[1].setTexture(self.TexPlane[1].findTextureStage('Tex1'), temp_textures, 1)        
        self.TexPlane[1].setTexture(self.TexPlane[1].findTextureStage('Tex2'), loader.loadTexture(path+'textures/'+self.textures[1]), 1)        
        self.TexPlane[1].setZ(-1)
        self.TexPlane[1].setDepthOffset(1)       
        
        #just to see a brush when painting textures
        #todo: should it use the texture that one is painting, or grayscale is ok?
        self.texBrush=self.brush.copyTo(self.altTexRender)        
        
        #project the texture on the terrain
        self.terrain.getRoot().projectTexture(TextureStage.getDefault() , self.altTex, self.altCam)     
                
        #GUI stuff - Here be Dragons!
        #elements added as the need arose
        
        #when the window changes size we need to refresh the location of most elements
        self.accept( 'window-event', self.windowEventHandler)         
        
        #bottom row: resizeFrame, colorFrame, alphaFrame, rotateFrame
        self.resizeFrame = DirectFrame(frameSize=(-128, 0, 0, 64),
                                    frameColor=(1,1,1,1),
                                    frameTexture='resize.png',
                                    text="1.00",
                                    text_scale=20,
                                    text_pos=(-70,25,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    text_fg=(1,1,1,1),
                                    parent=pixel2d)                               
        self.resizeFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.resizeFrame.setPos(128,0,-self.winY-20)
        self.resizeFrame.bind(DGG.B1PRESS, self.modeSet,[1]) 
        
        self.resizeAllFrame = DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 0.2),                                    
                                    text="ALL",
                                    text_scale=18,
                                    text_pos=(-18,12,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    text_fg=(1,1,1,1),
                                    parent=pixel2d)                               
        self.resizeAllFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.resizeAllFrame.setPos(32,0,-self.winY+43)
        self.resizeAllFrame.bind(DGG.B1PRESS, self.setResizeMode,['All'])
        self.resizeXFrame = DirectFrame(frameSize=(-31, 0, 0, 32),
                                    frameColor=(0, 0, 0, 0.5),                                   
                                    text="X",
                                    text_scale=18,
                                    text_pos=(-18,12,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    text_fg=(1,1,1,1),
                                    parent=pixel2d)                               
        self.resizeXFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.resizeXFrame.setPos(64,0,-self.winY+43)
        self.resizeXFrame.bind(DGG.B1PRESS, self.setResizeMode,['X'])
        self.resizeYFrame = DirectFrame(frameSize=(-31, 0, 0, 32),
                                    frameColor=(0, 0, 0, 0.5),
                                    text="Y",
                                    text_scale=18,
                                    text_pos=(-18,12,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    text_fg=(1,1,1,1),
                                    parent=pixel2d)                               
        self.resizeYFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.resizeYFrame.setPos(96,0,-self.winY+43)
        self.resizeYFrame.bind(DGG.B1PRESS, self.setResizeMode,['Y'])
        self.resizeZFrame = DirectFrame(frameSize=(-31, 0, 0, 32),
                                    frameColor=(0, 0, 0, 0.5),                                    
                                    text="Z",
                                    text_scale=18,
                                    text_pos=(-18,12,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    text_fg=(1,1,1,1),
                                    parent=pixel2d)                               
        self.resizeZFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.resizeZFrame.setPos(128,0,-self.winY+43)
        self.resizeZFrame.bind(DGG.B1PRESS, self.setResizeMode,['Z'])
        
        
        
        self.colorFrame = DirectFrame(frameSize=(-128, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='color.png',
                                    text="1.00",
                                    text_scale=20,
                                    text_pos=(-70,25,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.colorFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.colorFrame.setPos(256,0,-self.winY-20)
        self.colorFrame.bind(DGG.B1PRESS, self.modeSet,[2]) 
        
        self.rotateFrame = DirectFrame(frameSize=(-128, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='rotate.png',
                                    text="0.0",
                                    text_scale=20,
                                    text_pos=(-65,25,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.rotateFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.rotateFrame.setPos(384,0,-self.winY-20)
        self.rotateFrame.bind(DGG.B1PRESS, self.modeSet,[3]) 
        
        self.rotateHFrame = DirectFrame(frameSize=(-42, 0, 0, 32),
                                    frameColor=(1, 1, 1, 0.2),                                    
                                    text="H",
                                    text_scale=18,
                                    text_pos=(-22,12,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    text_fg=(1,1,1,1),
                                    parent=pixel2d)                               
        self.rotateHFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.rotateHFrame.setPos(298,0,-self.winY+43)
        self.rotateHFrame.bind(DGG.B1PRESS, self.setRotateMode,['H'])
        
        self.rotatePFrame = DirectFrame(frameSize=(-42, 0, 0, 32),
                                    frameColor=(0, 0, 0, 0.5),                                     
                                    text="P",
                                    text_scale=18,
                                    text_pos=(-22,12,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    text_fg=(1,1,1,1),
                                    parent=pixel2d)                               
        self.rotatePFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.rotatePFrame.setPos(341,0,-self.winY+43)
        self.rotatePFrame.bind(DGG.B1PRESS, self.setRotateMode,['P'])
        
        self.rotateRFrame = DirectFrame(frameSize=(-42, 0, 0, 32),
                                    frameColor=(0, 0, 0, 0.5),                                     
                                    text="R",
                                    text_scale=18,
                                    text_pos=(-22,12,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    text_fg=(1,1,1,1),
                                    parent=pixel2d)                               
        self.rotateRFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.rotateRFrame.setPos(384,0,-self.winY+43)
        self.rotateRFrame.bind(DGG.B1PRESS, self.setRotateMode,['R'])
                          
        self.rotateRFrame.hide()
        self.rotatePFrame.hide()
        self.rotateHFrame.hide()
        self.resizeZFrame.hide()
        self.resizeYFrame.hide()
        self.resizeXFrame.hide()
        self.resizeAllFrame.hide()
        
        self.alphaFrame = DirectFrame(frameSize=(-128, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='alpha.png',
                                    text="0.50",
                                    text_scale=20,
                                    text_pos=(-70,25,0),
                                    textMayChange=1,
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.alphaFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.alphaFrame.setPos(512,0,-self.winY-20)
        self.alphaFrame.bind(DGG.B1PRESS, self.modeSet,[4])      
        
        #grid togle, bottom row, right corner
        self.gridFrame=DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='grid_icon.png',                                   
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.gridFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.gridFrame.setPos(self.winX,0,-self.winY)
        self.gridFrame.bind(DGG.B1PRESS, self.togleGrid)  
       
        #top row - just the brushes
        #each brush texture has a name like "b#.png", where "#" is from 0 to 15
        self.brushButtons=[]
        for i in xrange(16):
            self.brushButtons.append(DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(0, 0, 0, 1),
                                    frameTexture='b'+str(i)+'.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d))
            self.brushButtons[i].setTransparency(TransparencyAttrib.MAlpha)                        
            self.brushButtons[i].setPos(32+(32*i),0,-32)
            self.brushButtons[i].bind(DGG.B1PRESS, self.setBrush,[i]) 
        #this one is selected by default    
        self.brushButtons[0]['frameColor']=(1,1,1,1)            
        
        #edit modes buttons, top right corner
        self.editMapFrame=DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='hm_icon.png',                                   
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.editMapFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.editMapFrame.setPos(self.winX-128,0,-64)
        self.editMapFrame.bind(DGG.B1PRESS, self.setEditMode,[1]) 
        
        self.editTexFrame=DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(0.4, .4, .4, 0.4),
                                    frameTexture='tex_icon.png',                                   
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.editTexFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.editTexFrame.setPos(self.winX-64,0,-64)
        self.editTexFrame.bind(DGG.B1PRESS, self.setEditMode,[2]) 
        
        self.editPlaceFrame=DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(0.4, .4, .4, 0.6),
                                    frameTexture='place_icon.png',                                   
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.editPlaceFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.editPlaceFrame.setPos(self.winX,0,-64)
        self.editPlaceFrame.bind(DGG.B1PRESS, self.setEditMode,[3])     
        
        #by default 2 texture layers are created
        #we need buttons for them
        #we start the editor in hightmap paint mode, so we hide these for now
        self.textureFrames=[]
        self.textureFrames.append(DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture=path+"textures/"+self.textures[0],
                                    state=DGG.NORMAL,
                                    parent=pixel2d))                                                 
        self.textureFrames[0].setPos(self.winX,0,-128) 
        self.textureFrames[0].bind(DGG.B1PRESS, self.selctLayer,[0])         
        self.textureFrames[0].hide()  
        self.textureFrames.append(DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture=path+"textures/"+self.textures[1],
                                    state=DGG.NORMAL,
                                    parent=pixel2d))                                                 
        self.textureFrames[1].setPos(self.winX,0,-192)
        self.textureFrames[1].bind(DGG.B1PRESS, self.selctLayer,[1]) 
        self.textureFrames[1].hide() 
        #the third texture-layer-button is special, it's here to add new texture-layers    
        self.textureFrames.append(DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='plus.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d))                                                 
        self.textureFrames[2].setTransparency(TransparencyAttrib.MAlpha)                                    
        self.textureFrames[2].setPos(self.winX,0,-256)
        self.textureFrames[2].bind(DGG.B1PRESS, self.selctLayer,[2]) 
        self.textureFrames[2].hide()  
        #a little arow to show what is the current layer, and also to cycle textures for that layer
        #todo: we only have "next" do we need "prev"?
        self.texPointFrame=DirectFrame(frameSize=(-32, 0, 0, 64),
                                    frameColor=(1, 1, 1, 0.8),
                                    frameTexture='next.png',                                   
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.texPointFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.texPointFrame.setPos(self.winX-64,0,-128)  
        self.texPointFrame.bind(DGG.B1PRESS, self.nextTexture) 
        self.texPointFrame.hide() 
               
        #model select list:
        #the number of models can change, there can be a lot of them, or just few
        #a scrolled frame is needed
        
        #I want to keep the width of the fram to a minimum, so I'm using a monospace, narrow font
        #getting the length of the longest filename on the list (-4 for file extension )
        self.maxWidth= (len(max(self.models, key=len))-4)*8

        self.scrollFrame = DirectScrolledFrame(canvasSize = (self.maxWidth+10,0,0,-(len(self.models)-1)*26),
                              frameSize = (self.maxWidth+10,0,0,-512),                              
                              verticalScroll_frameSize=(10,0,0,-512), 
                              verticalScroll_frameColor=(0, 0, 0, 0),
                              frameColor=(1, 1, 1, 0),
                              manageScrollBars=False,
                              autoHideScrollBars=False, 
                              verticalScroll_thumb_frameColor=(0, 0, 0, 1),                              
                              parent=pixel2d                              
                              )         
        self.scrollFrame.verticalScroll['value']=1
        self.scrollFrame.verticalScroll['incButton_relief']=None
        self.scrollFrame.verticalScroll['incButton_state'] = DGG.DISABLED
        self.scrollFrame.verticalScroll['decButton_relief']=None
        self.scrollFrame.verticalScroll['decButton_state'] = DGG.DISABLED        
        self.scrollFrame.hide()
        
        #put the objects in
        self.objectFrames=[]
        for i in xrange(len(self.models)):   
            self.objectFrames.append(DirectFrame(frameSize=(-self.maxWidth, 0, 0, 24),
                                    frameColor=(0, 0, 0, .4),
                                    text=str(self.models[i])[:-4],
                                    text_scale=14,
                                    text_fg=(1, 1, 1, 1),
                                    text_align=TextNode.ALeft,
                                    text_pos=(-self.maxWidth+5,9,0),
                                    state=DGG.NORMAL,
                                    parent=self.scrollFrame.getCanvas()))
            self.objectFrames[i].setTransparency(TransparencyAttrib.MAlpha)
            self.objectFrames[i].setPos(self.maxWidth+12,0,-26*i)  
            self.objectFrames[i].bind(DGG.B1PRESS,  self.selectModel, ["models/"+str(self.models[i])])
            #self.objectFrames[i].bind(DGG.WITHIN,  self.selectModel, [None])
            
        #group frame
        self.groupFrame=DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 0.7),
                                    frameTexture='ungroup.png',                                   
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.groupFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.groupFrame.setPos(self.winX,0,-128)
        self.groupFrame.bind(DGG.B1PRESS,  self.makeGroup) 
        self.groupFrame.hide()
        #add tag frame
        self.addTagFrame=DirectFrame(frameSize=(-512, 0, 0, 64),
                                    frameColor=(1, 1, 1, 0.7),
                                    frameTexture='tag.png',                                   
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.addTagFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.addTagFrame.setPos(self.winX+448,0,-192)
        self.addTagFrame.bind(DGG.B1PRESS,  self.togleFrame, [self.addTagFrame]) 
        self.addTagFrame.hide()
        
        self.addTagButton=DirectFrame(frameSize=(-60, 0, 0, 60),
                                    frameColor=(0, 0, 0, 0.8),
                                    frameTexture='plus.png',                                   
                                    state=DGG.NORMAL,
                                    parent=self.addTagFrame)                               
        self.addTagButton.setTransparency(TransparencyAttrib.MAlpha)
        self.addTagButton.setPos(0,0,1)
        self.addTagButton.bind(DGG.B1RELEASE, self.storeTag) 
        self.addTagButton.bind(DGG.B1PRESS , self.blink, [self.addTagButton]) 
        
        self.keyEntry = DirectEntry(frameColor=(0, 0, 0, 0.1),  
                                    width=23,
                                    text_scale=17,
                                    text_fg=(0,0,0,1),        
                                    initialText="key...",
                                    numLines = 1,
                                    focus=0,       
                                    suppressKeys=True,                                    
                                    parent=self.addTagFrame)
        self.keyEntry.setPos(-448,0,42)
        self.valueEntry = DirectEntry(frameColor=(0, 0, 0, 0.1),  
                                    width=23,
                                    text_scale=17,
                                    text_fg=(0,0,0,1),        
                                    initialText="value...",
                                    numLines = 1,
                                    focus=0,  
                                    suppressKeys=True,
                                    parent=self.addTagFrame)
        self.valueEntry.setPos(-448,0,14)
        
        #add bit-mask frame
        self.maskFrame=DirectFrame(frameSize=(-512, 0, 0, 64),
                                    frameColor=(1, 1, 1, 0.7),
                                    frameTexture='mask.png',                                   
                                    state=DGG.NORMAL,
                                    parent=pixel2d)                               
        self.maskFrame.setTransparency(TransparencyAttrib.MAlpha)
        self.maskFrame.setPos(self.winX+448,0,-256)
        self.maskFrame.bind(DGG.B1PRESS, self.togleFrame, [self.maskFrame]) 
        self.maskFrame.hide()
        self.bitMasksButtons=[]
        for i in xrange(32):
            self.bitMasksButtons.append(DirectFrame(frameSize=(-27, 0, 0, 24),
                                        frameColor=(0, 0, 0, 0.5),
                                        text=str(i),
                                        text_scale=14,
                                        text_fg=(1, 1, 1, 1),
                                        text_align=TextNode.ACenter ,
                                        text_pos=(-15,8,0),
                                        state=DGG.NORMAL,
                                        parent=self.maskFrame))            
            if i<16:
                self.bitMasksButtons[i].setPos(-421+(i*28),0,32)
            else:
                self.bitMasksButtons[i].setPos(-421+((i-16)*28),0,6)
            self.bitMasksButtons[i].setTransparency(TransparencyAttrib.MAlpha)
            self.bitMasksButtons[i].bind(DGG.B1PRESS, self.setBitMasks, [i])
    
    #functions - evil roams here, sorry for no comments
    #notUsed=None - the Direct Gui sends the events with info about the mouse pointer - I have no use for that
    def makeGroup(self, notUsed=None):
        if self.currentRoot==render:
            self.groupFrame['frameTexture']='group.png'
            self.numGroups+=1
            self.currentRoot=render.attachNewNode("Group"+str(self.numGroups))
        else:
            self.groupFrame['frameTexture']='ungroup.png'
            #self.currentRoot.clearModelNodes()
            self.currentRoot.flattenStrong() 
            self.currentRoot=render
        
    def setRotateMode(self, axis, notUsed=None):
        self.rotateAxis=axis
        self.modeSet(3)
        if axis=='H':
            self.rotateRFrame['frameColor']=(0, 0, 0, 0.5)
            self.rotatePFrame['frameColor']=(0, 0, 0, 0.5)
            self.rotateHFrame['frameColor']=(1, 1, 1, 0.2)
            if not self.currentObject==None:    
                self.rotateFrame['text']=str(self.currentObject.getH())            
        if axis=='P':
            self.rotateRFrame['frameColor']=(0, 0, 0, 0.5)
            self.rotatePFrame['frameColor']=(1, 1, 1, 0.2)
            self.rotateHFrame['frameColor']=(0, 0, 0, 0.5)
            if not self.currentObject==None:    
                self.rotateFrame['text']=str(self.currentObject.getP())
        if axis=='R':
            self.rotateRFrame['frameColor']=(1, 1, 1, 0.2)
            self.rotatePFrame['frameColor']=(0, 0, 0, 0.5)
            self.rotateHFrame['frameColor']=(0, 0, 0, 0.5)
            if not self.currentObject==None:    
                self.rotateFrame['text']=str(self.currentObject.getR())
            
    def setResizeMode(self, axis, notUsed=None):
        self.resizeAxis=axis
        self.modeSet(1)
        if axis=='X':
            self.resizeZFrame['frameColor']=(0, 0, 0, 0.5)
            self.resizeYFrame['frameColor']=(0, 0, 0, 0.5)
            self.resizeXFrame['frameColor']=(1, 1, 1, 0.2)
            self.resizeAllFrame['frameColor']=(0, 0, 0, 0.5)
            if not self.currentObject==None:    
                self.resizeFrame['text']= "%.02f" % float(self.currentObject.getSx()) 
        if axis=='Y':
            self.resizeZFrame['frameColor']=(0, 0, 0, 0.5)
            self.resizeYFrame['frameColor']=(1, 1, 1, 0.2)
            self.resizeXFrame['frameColor']=(0, 0, 0, 0.5)
            self.resizeAllFrame['frameColor']=(0, 0, 0, 0.5)
            if not self.currentObject==None:    
                self.resizeFrame['text']= "%.02f" % float(self.currentObject.getSy()) 
        if axis=='Z':
            self.resizeZFrame['frameColor']=(1, 1, 1, 0.2)
            self.resizeYFrame['frameColor']=(0, 0, 0, 0.5)
            self.resizeXFrame['frameColor']=(0, 0, 0, 0.5)
            self.resizeAllFrame['frameColor']=(0, 0, 0, 0.5)
            if not self.currentObject==None:    
                self.resizeFrame['text']= "%.02f" % float(self.currentObject.getSz()) 
        if axis=='All':
            self.resizeZFrame['frameColor']=(0, 0, 0, 0.5)
            self.resizeYFrame['frameColor']=(0, 0, 0, 0.5)
            self.resizeXFrame['frameColor']=(0, 0, 0, 0.5)
            self.resizeAllFrame['frameColor']=(1, 1, 1, 0.2)
            if not self.currentObject==None:    
                self.resizeFrame['text']= "~ %.02f" % float((self.currentObject.getSx()+self.currentObject.getSy()+self.currentObject.getSz())/3)
            
    def selectModel(self, model, notUsed=None):
        if not self.currentObject==None:
            self.currentObject.removeNode()
        if model==None:
            self.currentObject=None
        else:    
            self.currentObject=loader.loadModel(path+model)
            self.currentObject.reparentTo(self.currentRoot)
        self.currentModelName=model
        
    def blink(self, button, notUsed=None):
        button['frameColor']=(1, 1, 1, 0.8)
     
    def onExitCleaup(self):
        print "clean EXIT!"
        
        if not len(self.export)==0:             
            outfile=open(Filename(path+self.saveName+'/data.json').toOsSpecific(), 'wb')
            json.dump(obj=self.export, fp=outfile, sort_keys=True, indent=4, separators=(',', ': '))
            outfile.close()
        if os.listdir(Filename(path+self.saveName).toOsSpecific()) == []:
            os.rmdir(Filename(path+self.saveName).toOsSpecific())
   
    def storeTag(self, notUsed=None):        
        key=self.keyEntry.get()
        value=self.valueEntry.get()
        self.currentTag.append([key, value])
        print self.currentTag
        self.addTagButton['frameColor']=(0, 0, 0, 0.8)
        self.togleFrame(self.addTagFrame)
        
    def setBitMasks(self, bit, notUsed=None):
        if self.currentBitMask[bit]==0:
            self.currentBitMask[bit]=1
            self.bitMasksButtons[bit]['frameColor']=(0, 0, 0, 0.9)
        else:     
            self.currentBitMask[bit]=0
            self.bitMasksButtons[bit]['frameColor']=(0, 0, 0, 0.5)
            
    def togleFrame(self, frame, notUsed=None):
        if frame.getPythonTag('isOpen'):
            frame.setX(self.winX+448) 
            frame.setPythonTag('isOpen', False)
            for child in frame.getChildren():
                child.hide()                
                #child['focus']=0
                self.keyEntry['focus']=0
                self.valueEntry['focus']=0
        else:
            frame.setPythonTag('isOpen', True)
            frame.setX(self.winX)            
            for child in frame.getChildren():
                child.show()
                
    def selctLayer(self, layer, notUsed=None):
        self.currentTexLayer=layer
        self.texPointFrame.setPos(self.winX-64,0,-128-(64*self.currentTexLayer)) 
        file=str(self.currentTexLayer)+"tex.png"
        if os.path.exists(path+self.saveName+"/"+file):    
            self.altPlane.setTexture(loader.loadTexture(path+self.saveName+"/"+file), 1)
        else:
            self.altPlane.setTexture(loader.loadTexture("full_mask.png"), 1)
                
        if layer == len(self.textureFrames)-1:
            self.textureFrames[layer]['frameTexture']=path+"textures/"+self.textures[0]
            self.textureFrames.append(DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='plus.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d))                                                 
            self.textureFrames[layer+1].setTransparency(TransparencyAttrib.MAlpha)                                    
            self.textureFrames[layer+1].setPos(self.winX,0,-128-(64*(layer+1)))
            self.textureFrames[layer+1].bind(DGG.B1PRESS, self.selctLayer,[layer+1]) 
            self.textureForLayer.append(0)
            self.TexPlane.append(self.texturePlane.copyTo(self.altTexRender))  
            temp_textures=Texture()
            temp_textures.read('full_mask.png')
            temp_textures.setFormat(Texture.FAlpha)  
            self.TexPlane[layer].setTexture(self.TexPlane[layer].findTextureStage('Tex1'), temp_textures, 1)        
            self.TexPlane[layer].setTexture(self.TexPlane[layer].findTextureStage('Tex2'), loader.loadTexture(path+'textures/'+self.textures[0]), 1)        
            self.TexPlane[layer].setZ(-1)
            self.TexPlane[layer].setDepthOffset(layer)     
        
    def nextTexture(self, notUsed=None):
        layer=self.currentTexLayer
        tex=self.textureForLayer[layer]
        
        if tex >= len(self.textures)-1:
            tex=0
        else:
            tex+=1 
        self.textureFrames[self.currentTexLayer]['frameTexture']=path+"textures/"+self.textures[tex]
        self.textureForLayer[layer]=tex
        self.TexPlane[layer].setTexture(self.TexPlane[layer].findTextureStage('Tex2'), loader.loadTexture(path+'textures/'+self.textures[tex]), 1)        
        
    def setEditMode (self, mode, notUsed=None):
        self.editMode=mode
        TexturePool.releaseAllTextures()
        file=str(self.currentTexLayer)+"tex.png"
        
        if mode==1:
            self.editMapFrame['frameColor']=(1,1,1,1)
            self.editTexFrame['frameColor']=(0.4, .4, .4, 0.6)
            self.editPlaceFrame['frameColor']=(0.4, .4, .4, 0.6)
            
            #self.terrain.getRoot().clearProjectTexture(TextureStage.getDefault())         
            self.terrain.getRoot().projectTexture(TextureStage.getDefault() , self.altTex, self.altCam)
            if os.path.exists(path+self.saveName+"/hf.png"):
                self.altPlane.setTexture(loader.loadTexture(path+self.saveName+"/hf.png"), 1)
            else:
                self.altPlane.setTexture(loader.loadTexture("img.png"), 1)
            for i in xrange(len(self.textureFrames)):                
                self.textureFrames[i].hide()    
            for i in xrange(16):
                self.brushButtons[i].show()    
            self.texPointFrame.hide() 
            self.scrollFrame.hide()   
            self.addTagFrame.hide() 
            self.maskFrame.hide()
            self.alphaFrame.show()                      
            self.rotateRFrame.hide()
            self.rotatePFrame.hide()
            self.rotateHFrame.hide()
            self.resizeZFrame.hide()
            self.resizeYFrame.hide()
            self.resizeXFrame.hide()
            self.resizeAllFrame.hide()
            self.groupFrame.hide()
            if not self.currentObject==None:
                self.currentObject.hide()          
            self.colorFrame['frameTexture']='color.png'
        elif mode==2:
            self.editMapFrame['frameColor']=(0.4, .4, .4, 0.6)
            self.editTexFrame['frameColor']=(1,1,1,1)
            self.editPlaceFrame['frameColor']=(0.4, .4, .4, 0.6)             
            #self.terrain.getRoot().clearProjectTexture(TextureStage.getDefault())         
            self.terrain.getRoot().projectTexture(TextureStage.getDefault() , self.altTexTex, self.texCam)  
            if os.path.exists(path+self.saveName+"/"+file):    
                self.altPlane.setTexture(loader.loadTexture(path+self.saveName+"/"+file), 1)
            else:
                self.altPlane.setTexture(loader.loadTexture("full_mask.png"), 1)
            for i in xrange(len(self.textureFrames)):                
                self.textureFrames[i].show()    
            for i in xrange(16):
                self.brushButtons[i].show()    
            self.texPointFrame.show() 
            self.scrollFrame.hide()
            self.texBrush.show()
            self.addTagFrame.hide()
            self.maskFrame.hide()
            self.alphaFrame.show()            
            self.rotateRFrame.hide()
            self.rotatePFrame.hide()
            self.rotateHFrame.hide()
            self.resizeZFrame.hide()
            self.resizeYFrame.hide()
            self.resizeXFrame.hide()
            self.resizeAllFrame.hide()
            self.groupFrame.hide()
            if not self.currentObject==None:
                self.currentObject.hide()                                
            self.colorFrame['frameTexture']='color.png'    
        elif mode==3:
            self.editMapFrame['frameColor']=(0.4, .4, .4, 0.6)
            self.editTexFrame['frameColor']=(0.4, .4, .4, 0.6)
            self.editPlaceFrame['frameColor']=(1,1,1,1)    
            self.terrain.getRoot().projectTexture(TextureStage.getDefault() , self.altTexTex, self.texCam)  
            if os.path.exists(path+self.saveName+"/"+file):    
                self.altPlane.setTexture(loader.loadTexture(path+self.saveName+"/"+file), 1)
            else:
                self.altPlane.setTexture(loader.loadTexture("full_mask.png"), 1)
            for i in xrange(len(self.textureFrames)):                
                self.textureFrames[i].hide()    
            for i in xrange(16):
                self.brushButtons[i].hide()
            self.texPointFrame.hide() 
            self.scrollFrame.show()
            self.texBrush.hide()
            self.addTagFrame.show()
            self.maskFrame.show()
            self.alphaFrame.hide()
            self.rotateRFrame.show()
            self.rotatePFrame.show()
            self.rotateHFrame.show()
            self.resizeZFrame.show()
            self.resizeYFrame.show()
            self.resizeXFrame.show()
            self.resizeAllFrame.show()
            self.groupFrame.show()
            if not self.currentObject==None:
                self.currentObject.show()                                                              
            self.colorFrame['frameTexture']='z.png'
            
    def togleGrid(self, notUsed=None):        
        if self.grid.getColor()==Vec4(0,0,0,0):            
            self.grid.setColor(0,0,0,0.5)
            self.gridFrame['frameColor']=(1,1,1,1)
        else:    
            self.grid.setColor(0,0,0,0)
            self.gridFrame['frameColor']=(0,0,0,.6)
            
    def setBrush(self, index, mouse):
        for i in xrange(16):
            self.brushButtons[i]['frameColor']=(0,0,0,1)
        self.brushButtons[index]['frameColor']=(1,1,1,1)    
        self.brush.setTexture(loader.loadTexture('b'+str(index)+'.png'))
        self.texBrush.setTexture(loader.loadTexture('b'+str(index)+'.png'))
        
    def windowEventHandler( self, window=None ):    
        if window is not None: # window is none if panda3d is not started
            wp = base.win.getProperties()
            self.winX = wp.getXSize()
            self.winY = wp.getYSize()
            self.rotateFrame.setPos(384,0,-self.winY-20)
            self.alphaFrame.setPos(512,0,-self.winY-20)
            self.colorFrame.setPos(256,0,-self.winY-20)
            self.resizeFrame.setPos(128,0,-self.winY-20)
            self.gridFrame.setPos(self.winX,0,-self.winY)
            self.editMapFrame.setPos(self.winX-128,0,-64)
            self.editTexFrame.setPos(self.winX-64,0,-64)
            self.editPlaceFrame.setPos(self.winX,0,-64)            
            self.texPointFrame.setPos(self.winX-64,0,-128-(64*self.currentTexLayer))             
            for i in xrange(len(self.textureFrames)):                
                self.textureFrames[i].setPos(self.winX,0,-128-(64*i))                          
            self.scrollFrame['frameSize']=(self.maxWidth+10,0,0,-self.winY+88)
            self.scrollFrame['verticalScroll_frameSize']=(10,0,0,-self.winY+88) 
            self.scrollFrame.verticalScroll['value']=1
            self.rotateRFrame.setPos(384,0,-self.winY+43)
            self.rotatePFrame.setPos(341,0,-self.winY+43)
            self.rotateHFrame.setPos(298,0,-self.winY+43)
            self.resizeZFrame.setPos(128,0,-self.winY+43)
            self.resizeYFrame.setPos(96,0,-self.winY+43)
            self.resizeXFrame.setPos(64,0,-self.winY+43)
            self.resizeAllFrame.setPos(32,0,-self.winY+43)
            self.groupFrame.setPos(self.winX,0,-128)
            if self.maskFrame.getPythonTag('isOpen'):
                self.maskFrame.setX(self.winX)                 
            else:               
                self.maskFrame.setX(self.winX+448) 
            if self.addTagFrame.getPythonTag('isOpen'):
                self.addTagFrame.setX(self.winX)                 
            else:               
                self.addTagFrame.setX(self.winX+448) 
                
    def moveTask(self, task):
        dt = globalClock.getDt()
        #if (dt > .05):
        #  return task.cont
        
        if self.keyMap["d"]:
          self.cameraNode.setX(self.cameraNode,self.cameraZoom*dt)
        elif self.keyMap["a"]:
          self.cameraNode.setX(self.cameraNode, -self.cameraZoom*dt)
        
        if self.keyMap["w"]:
          self.cameraNode.setY(self.cameraNode,self.cameraZoom*dt)
        elif self.keyMap["s"]:
          self.cameraNode.setY(self.cameraNode,-self.cameraZoom*dt)
        
        if self.keyMap["q"]:
          self.cameraNode.setH(self.cameraNode.getH()-60*dt)
        elif self.keyMap["e"]:
          self.cameraNode.setH(self.cameraNode.getH()+60*dt)        
        
        if self.keyMap["z"]:    
            if self.cameraZoom>1: 
                base.camera.setY(base.camera,50*dt)
                self.cameraZoom-=20*dt                
        elif self.keyMap["x"]:
            base.camera.setY(base.camera,-50*dt)
            self.cameraZoom+=20*dt 
        
        if self.keyMap["r"]:
          base.camera.setZ(base.camera,50*dt)
          base.camera.lookAt(self.cameraNode)
        elif self.keyMap["f"]:
          base.camera.setZ(base.camera,-50*dt)
          base.camera.lookAt(self.cameraNode)      
        
        if self.keyMap["z"] or self.keyMap["x"]:
            self.texfilmSize=int(round(self.cameraZoom*8/100.0)*100.0)
            if self.texfilmSize<64:
                self.texfilmSize=64
            if self.texfilmSize>512:
                self.texfilmSize=512
            self.texLens.setFilmSize(self.texfilmSize, self.texfilmSize) 
            
        if self.texfilmSize==512:
            self.texCam.setPos(256,256,100)                     
        elif abs(self.cameraNode.getX(render)-self.texCam.getX(render))>16 or abs(self.cameraNode.getY(render)-self.texCam.getY(render))>16:   
            self.texCam.setX(self.cameraNode.getX(render))
            self.texCam.setY(self.cameraNode.getY(render)) 
        self.brush.setPos(render, self.pointer.getPos())
        self.texBrush.setPos(render, self.pointer.getPos())
        
        
        return task.cont
        
    def __getMousePos(self, task):
        if base.mouseWatcherNode.hasMouse():
          mpos = base.mouseWatcherNode.getMouse()
          pos3d = Point3()
          nearPoint = Point3()
          farPoint = Point3()
          base.camLens.extrude(mpos, nearPoint, farPoint)
          if self.plane.intersectsLine(pos3d,
              render.getRelativePoint(camera, nearPoint),
              render.getRelativePoint(camera, farPoint)):
            #print "Mouse ray intersects ground plane at ", pos3d
            self.pointer.setPos(render, pos3d)
            if not self.currentObject==None:
                self.currentObject.setX(pos3d.getX())
                self.currentObject.setY(pos3d.getY())            
                self.currentObject.setZ(-50+self.currentZ+self.terrain.getElevation(pos3d.getX(), pos3d.getY())*100)
        return task.again        
            
    def SaveAndUpdate(self):       
        if self.editMode==3:        
            if not self.currentObject==None:       
                self.currentObject.copyTo(self.currentRoot)                
                self.export.append({'model':self.currentModelName,
                                    'H':str(self.currentObject.getH()),
                                    'P':str(self.currentObject.getH()),
                                    'R':str(self.currentObject.getH()),
                                    'X':str(self.currentObject.getX()),
                                    'Y':str(self.currentObject.getY()),
                                    'Z':str(self.currentObject.getZ()),
                                    'Sx':str(self.currentObject.getSx()),
                                    'Sy':str(self.currentObject.getSy()),
                                    'Sz':str(self.currentObject.getSz()),
                                    'bitMask':''.join(str(e) for e in self.currentBitMask),
                                    'tags':self.currentTag,
                                    'root':self.currentRoot.getName()
                                    })                      
        else:
            p=PNMImage(512, 512, 4)              
            base.graphicsEngine.extractTextureData(self.altTex,base.win.getGsg())
            self.altTex.store(p)   
            p.removeAlpha()    
            p.makeGrayscale(1,0,0)     
                            
            myTexture=Texture()
            myTexture.load(p)        
            self.altPlane.setTexture(myTexture, 1)
            
            if self.editMode==1:
                p.write(path+self.saveName+"/hf.png")
                t=PNMImage(513, 513, 1)      
                t.boxFilterFrom(1, p)
                self.terrain.setHeightfield(t)
                self.terrain.update()   
                
            elif self.editMode==2:
                if self.currentTexLayer==0:
                    self.selctLayer(1)
                file=str(self.currentTexLayer)+"tex.png"
                p.write(path+self.saveName+"/"+file)
                myTexture2=Texture()
                myTexture2.load(p) 
                myTexture2.setFormat(Texture.FAlpha)  
                self.TexPlane[self.currentTexLayer].setTexture(self.TexPlane[self.currentTexLayer].findTextureStage('Tex1'), myTexture2, 1)        
                
        
    def modeTogle(self, up):
        self.mode+=up
        if self.mode>4:
            self.mode=1
        if self.mode<1:
            self.mode=4
            
        if self.mode==1:
            self.resizeFrame['text_fg']=(1,1,1,1)
            self.colorFrame['text_fg']=(0,0,0,1)
            self.alphaFrame['text_fg']=(0,0,0,1)
            self.rotateFrame['text_fg']=(0,0,0,1)
        if self.mode==2:
            self.resizeFrame['text_fg']=(0,0,0,1)
            self.colorFrame['text_fg']=(1,1,1,1)
            self.alphaFrame['text_fg']=(0,0,0,1)
            self.rotateFrame['text_fg']=(0,0,0,1)
        if self.mode==3:
            self.resizeFrame['text_fg']=(0,0,0,1)
            self.colorFrame['text_fg']=(0,0,0,1)
            self.alphaFrame['text_fg']=(0,0,0,1)
            self.rotateFrame['text_fg']=(1,1,1,1)  
        if self.mode==4:
            self.resizeFrame['text_fg']=(0,0,0,1)
            self.colorFrame['text_fg']=(0,0,0,1)
            self.alphaFrame['text_fg']=(1,1,1,1)
            self.rotateFrame['text_fg']=(0,0,0,1)
              
        #print self.mode   
        
    def modeSet(self, what, notUsed=None):
        self.mode=what
        if self.mode==1:
            self.resizeFrame['text_fg']=(1,1,1,1)
            self.colorFrame['text_fg']=(0,0,0,1)
            self.alphaFrame['text_fg']=(0,0,0,1)
            self.rotateFrame['text_fg']=(0,0,0,1)
        if self.mode==2:
            self.resizeFrame['text_fg']=(0,0,0,1)
            self.colorFrame['text_fg']=(1,1,1,1)
            self.alphaFrame['text_fg']=(0,0,0,1)
            self.rotateFrame['text_fg']=(0,0,0,1)
        if self.mode==3:
            self.resizeFrame['text_fg']=(0,0,0,1)
            self.colorFrame['text_fg']=(0,0,0,1)
            self.alphaFrame['text_fg']=(0,0,0,1)
            self.rotateFrame['text_fg']=(1,1,1,1)          
        if self.mode==4:
            self.resizeFrame['text_fg']=(0,0,0,1)
            self.colorFrame['text_fg']=(0,0,0,1)
            self.alphaFrame['text_fg']=(1,1,1,1)
            self.rotateFrame['text_fg']=(0,0,0,1)
        
    
    def mouseWheel(self, up):
        if self.mode==1:
            if self.editMode==3 and not self.currentObject==None:
                if up:
                    size=0.05
                else:
                    size=-0.05
                if self.resizeAxis=='X':
                    self.currentObject.setSx(self.currentObject.getSx()+size)
                    self.resizeFrame['text']= "%.02f" % float(self.currentObject.getSx())                    
                if self.resizeAxis=='Y':
                    self.currentObject.setSy(self.currentObject.getSy()+size)
                    self.resizeFrame['text']= "%.02f" % float(self.currentObject.getSy()) 
                if self.resizeAxis=='Z':
                    self.currentObject.setSz(self.currentObject.getSz()+size)
                    self.resizeFrame['text']= "%.02f" % float(self.currentObject.getSz()) 
                if self.resizeAxis=='All':
                    self.currentObject.setSx(self.currentObject.getSx()+size)
                    self.currentObject.setSy(self.currentObject.getSy()+size)
                    self.currentObject.setSz(self.currentObject.getSz()+size)
                    self.resizeFrame['text']= "~ %.02f" % float((self.currentObject.getSx()+self.currentObject.getSy()+self.currentObject.getSz())/3)         
            else:
                scale=self.brush.getScale()            
                if up:
                    self.brush.setScale(scale+0.05)
                    self.resizeFrame['text']= "%.02f" % float(scale[0]+0.05)
                else:
                    self.brush.setScale(scale-0.05)
                    self.resizeFrame['text']= "%.02f" % float(scale[0]-0.05)
        elif self.mode==2:
            if self.editMode==3:
                if up:
                    self.currentZ+=0.05                        
                else:
                    self.currentZ-=0.05
                self.colorFrame['text']= "%.02f" % float(self.currentZ)    
            else:
                color=self.brush.getColor()
                if up and color[0]<1:
                    self.brush.setColor(color[0]+.01, color[0]+.01, color[0]+.01, color[3])
                    self.colorFrame['text']= "%.02f" % float(color[0]+0.01)
                elif color[0]>0:
                    self.brush.setColor(color[0]-.01, color[0]-.01, color[0]-.01, color[3])            
                    self.colorFrame['text']= "%.02f" % float(color[0]-0.01)
        elif self.mode==3:
            if self.editMode==3 and not self.currentObject==None:
                if up:
                    angle=5
                else:
                    angle=-5
                if self.rotateAxis=='H':
                    self.currentObject.setH(self.currentObject.getH()+angle)
                    self.rotateFrame['text']= str(self.currentObject.getH()) 
                if self.rotateAxis=='P':
                    self.currentObject.setP(self.currentObject.getP()+angle)
                    self.rotateFrame['text']= str(self.currentObject.getP()) 
                if self.rotateAxis=='R':
                    self.currentObject.setR(self.currentObject.getR()+angle)
                    self.rotateFrame['text']= str(self.currentObject.getR())     
            else:
                if up:
                    self.brush.setH(self.brush.getH()+5)                
                else: 
                    self.brush.setH(self.brush.getH()-5)
                self.rotateFrame['text']= str(self.brush.getH(render))    
        elif self.mode==4:
            color=self.brush.getColor()
            if up and color[3]<1:
                self.brush.setColor(color[0], color[1], color[1], color[3]+0.01)
                self.alphaFrame['text']= "%.02f" % float(color[3]+0.01)
            elif color[3]>0:
                self.brush.setColor(color[0], color[1], color[1], color[3]-0.01)
                self.alphaFrame['text']= "%.02f" % float(color[3]+0.01)
        
        self.texBrush.setH(self.brush.getH())    
        self.texBrush.setColor(self.brush.getColor())    
        self.texBrush.setScale(self.brush.getScale())    
w = Editor()
run() 
