#************************************************************5**********
# AI - Artificial Intelligence for Games ST0228 (August 2011)
# Name: Marcus Khoo Lian Kai
# Admin: 1031582
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText 
from direct.task import Task
from pandac.PandaModules import *

class Preloader():
    
    def __init__(self):
        self.progressBar = DirectWaitBar(text = "", value = 0, pos = (0,0,0), scale = 0.5, barColor = (1,0.3,0,1))
        self.textObject = OnscreenText(text = "", pos = (0.0,-0.15),
                              scale = 0.1,fg=(0,0,0,1),align=TextNode.ACenter,mayChange=1)
                              
        f = open('models_2.txt', 'r')
        self.models = f.readlines()
        f.close()
        
        for N in range(len(self.models)):
            self.models[N] = self.models[N].replace("\n", "")
            
        self.totalItems = len(self.models)
        
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()
        
        self.itemCount = 0
        
        for M in self.models:
            print(M)
            item = loader.loadModel(M)
            progress = 100 / float(self.totalItems)
            self.progressBar['value'] += progress
            #text = str(self.progressBar['value'])+'%'
            self.textObject.setText("Loading")
            #self.loaderBar.setTexOffset(self.modTS, -progress + 0.15,0)
            base.graphicsEngine.renderFrame()
            base.graphicsEngine.renderFrame()
            
        self.textObject.destroy()
        self.progressBar.destroy()