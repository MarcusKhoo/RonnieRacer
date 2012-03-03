import sys
import direct.directbase.DirectStart

from pandac.PandaModules import *

from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState

from direct.task import Task

from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectLabel import DirectLabel

from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32
from panda3d.core import Filename
from panda3d.core import PNMImage

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletHingeConstraint
from panda3d.bullet import BulletConeTwistConstraint
from panda3d.bullet import BulletVehicle
from panda3d.bullet import BulletHeightfieldShape
from panda3d.bullet import BulletSliderConstraint
from panda3d.bullet import ZUp
from Preloader_2 import Preloader

class RonnieRacer(DirectObject):
  
  gameState = 'INIT'
  gameLevel = 1
  distanceTravelled = 0
  speed = 0
  score = 0
  triesLeft = 3
  count = 0
  rot = 0
  time = 0
  pause = False
  
  def __init__(self):
    self.imageObject = OnscreenImage(image = 'media/images/splashscreen.png', pos=(0,0,0), scale=(1.4,1,1))
    self.loseScreen = OnscreenImage(image = 'media/images/gameover.png', pos=(0,0,0), scale=(1,1,0.8))
    self.loseScreen.hide()
    self.retryScreen = OnscreenImage(image = 'media/images/retry.png', pos=(0,0,0), scale=(1,1,0.8))
    self.retryScreen.hide()
    self.congratScreen = OnscreenImage(image = 'media/images/congratulations.png', pos=(0,0,0), scale = (1,1,0.8))
    self.congratScreen.hide()
    self.winScreen = OnscreenImage(image = 'media/images/victory.png', pos=(0,0,0), scale = (1,1,0.8))
    self.winScreen.hide()
    self.pauseScreen = OnscreenImage(image = 'media/images/pause.png', pos=(0,0,0), scale = (1,1,0.8))
    self.pauseScreen.hide()
    self.instructionScreen = OnscreenImage(image = 'media/images/instructions.png', pos=(0,0,0), scale = (1,1,0.8))
    self.instructionScreen.hide()
    preloader = Preloader()
    base.setBackgroundColor(0, 0, 0, 1)
    base.setFrameRateMeter(True)
    
    # Audio
    self.loseSound = base.loader.loadSfx("media/audio/sfxboo.wav")
    self.winSound = base.loader.loadSfx("media/audio/cheer2.aif")
    self.menuMusic = base.loader.loadSfx("media/audio/Scattershot.mp3")
    self.gameMusic = base.loader.loadSfx("media/audio/Ghostpocalypse - 7 Master.mp3")
    
    self.menuMusic.setLoop(True)
    self.menuMusic.setLoopCount(0)
    
    self.gameMusic.setLoop(True)
    self.gameMusic.setLoopCount(0)

    #setup buttons
    self.retryBtn = DirectButton(text="Retry", scale = 0.1, pos = (0,0,0), command = self.doRetry)
    self.retryBtn.hide()
    self.menuBtn = DirectButton(text="Main Menu", scale = 0.1, pos = (0,0,0), command = self.doMenu)
    self.menuBtn.hide()
    self.nextBtn = DirectButton(text='Next', scale = 0.1, pos = (0,0,0), command = self.doNext)
    self.nextBtn.hide()
    self.backBtn = DirectButton(text='back', scale = 0.1, pos = (-0.7,0,-0.7), command = self.doBack)
    self.backBtn.hide()
    
    #setup font
    self.font = loader.loadFont('media/SHOWG.TTF')
    self.font.setPixelsPerUnit(60)
    
    #setup text
    self.text = OnscreenText(text = '', pos = (0, 0), scale = 0.07, font = self.font)
    
    self.rpmText = OnscreenText(text = '', 
                            pos = (-0.9, -0.9), scale = 0.07, font = self.font)
                            
    self.speedText = OnscreenText(text = '', 
                            pos = (0, -0.9), scale = 0.07, font = self.font)
                            
    self.distanceText = OnscreenText(text = '', 
                            pos = (0.9, -0.9), scale = 0.07, font = self.font)
    
    self.triesLeftText = OnscreenText(text = '', 
                            pos = (1.0, 0.9), scale = 0.07, font = self.font)
    
    self.gameLevelText = OnscreenText(text = '', 
                            pos = (-1.0, 0.9), scale = 0.07, font = self.font)
    
    self.timeText = OnscreenText(text = '', 
                            pos = (0, 0.9), scale = 0.07, font = self.font)
    
    self.scoreText = OnscreenText(text = '', 
                            pos = (1.0, 0.8), scale = 0.07, font = self.font)
    
    self.finalScoreText = OnscreenText(text = '', 
                            pos = (0, 0.2), scale = 0.07, font = self.font)
    # Light
    alight = AmbientLight('ambientLight')
    alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
    alightNP = render.attachNewNode(alight)

    dlight = DirectionalLight('directionalLight')
    dlight.setDirection(Vec3(1, 1, -1))
    dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
    dlightNP = render.attachNewNode(dlight)

    render.clearLight()
    render.setLight(alightNP)
    render.setLight(dlightNP)

    # Input
    self.accept('escape', self.doExit)
    self.accept('r', self.doReset)
    self.accept('f1', self.toggleWireframe)
    self.accept('f2', self.toggleTexture)
    self.accept('f3', self.toggleDebug)
    self.accept('f5', self.doScreenshot)

    inputState.watchWithModifiers('forward', 'w')
    inputState.watchWithModifiers('left', 'a')
    inputState.watchWithModifiers('reverse', 's')
    inputState.watchWithModifiers('right', 'd')
    inputState.watchWithModifiers('turnLeft', 'a')
    inputState.watchWithModifiers('turnRight', 'd')

    # Task
    taskMgr.add(self.update, 'updateWorld')

  # _____HANDLER_____
  def doExit(self):
    sys.exit(1)

  def doReset(self):
    self.cleanup()
    self.terrain.getRoot().removeNode()
    self.setup()

  def doBack(self):
    self.backBtn.hide()
    self.instructionScreen.hide()
    
    self.imageObject.show()
    self.helpBtn.show()
    self.startBtn.show()
    self.exitBtn.show()

  def toggleWireframe(self):
    base.toggleWireframe()

  def toggleTexture(self):
    base.toggleTexture()

  def toggleDebug(self):
    if self.debugNP.isHidden():
      self.debugNP.show()
    else:
      self.debugNP.hide()

  def doScreenshot(self):
    base.screenshot('Bullet')

  # ____TASK___

  def processInput(self, dt):
    # Process input
    engineForce = 0.0
    brakeForce = 0.0
    
    self.accept('p', self.doPause)
  
    if inputState.isSet('forward'):
       engineForce = 15.0
       brakeForce = 0.0
   
    if inputState.isSet('reverse'):
       engineForce = -25.0
       brakeForce = 25.0
   
    if inputState.isSet('turnLeft'):
       self.steering += dt * self.steeringIncrement
       self.steering = min(self.steering, self.steeringClamp)
   
    if inputState.isSet('turnRight'):
       self.steering -= dt * self.steeringIncrement
       self.steering = max(self.steering, -self.steeringClamp)
   
    # Apply steering to front wheels
    self.vehicle.setSteeringValue(self.steering, 0)
    self.vehicle.setSteeringValue(self.steering, 1)
   
    # Apply engine and brake to rear wheels
    self.vehicle.applyEngineForce(engineForce, 2)
    self.vehicle.applyEngineForce(engineForce, 3)
    self.vehicle.setBrake(brakeForce, 2)
    self.vehicle.setBrake(brakeForce, 3)
    
  def processContacts(self, dt):
    result = self.world.contactTestPair(self.vehicleNP.node(), self.flagNP.node())
    if(result.getNumContacts() > 0):
      self.gameState = 'WIN'
      self.doContinue()
      
  def doContinue(self):
    if(self.gameState == 'INIT'):
      self.gameState = 'MENU'
      self.menuMusic.play()
      self.text.hide()
      self.startBtn = DirectButton(text=("Play"), scale = 0.1, pos = (0.5,0,0),command=self.playGame)
      self.helpBtn = DirectButton(text=("Help"), scale = 0.1, pos = (0.5,0,-0.2),command=self.help)
      self.exitBtn = DirectButton(text=("Exit"), scale = 0.1,  pos = (0.5,0,-0.4), command = self.doExit)
      return
      
    if(self.gameState == 'RETRY'):
      self.retryScreen.show()
      self.retryBtn.show()
      
      self.loseSound.play()
      return
    
    if(self.gameState == 'LOSE'):
      self.loseScreen.show()
      self.menuBtn.show()
      return
    
    if(self.gameState == 'WIN'):
      if(self.gameLevel < 3):
        self.congratScreen.show()
        self.nextBtn.show()
      elif(self.gameLevel >= 3):
        self.winScreen.show()
        self.menuBtn.show()
      self.finalScoreText.setText('Your Score: '+str(int(self.score)))
      self.finalScoreText.show()
        
      self.winSound.play()
      
  def help(self):
    self.gameState = 'HELP'
    self.startBtn.hide()
    self.exitBtn.hide()
    self.helpBtn.hide()
    self.imageObject.hide()
    self.instructionScreen.show()
    self.backBtn.show()
    
  def doNext(self):
    self.nextBtn.hide()
    self.finalScoreText.hide()
    self.congratScreen.hide()
    self.gameLevel += 1
    if(self.gameLevel == 2):
      self.score += 2000
    elif(self.gameLevel == 3):
      self.score += 3000
    self.doReset()
    self.triesLeft = 3
    self.gameState = 'PLAY'
    
  def doRetry(self):
    self.doReset()
    self.gameState = 'PLAY'
    self.retryScreen.hide()
    self.retryBtn.hide()
    self.triesLeft -= 1
  
  def doMenu(self):
    self.cleanup()
    self.terrain.getRoot().removeNode()
    self.gameState = 'MENU'
    
    self.score = 0
    
    self.imageObject.show()
    self.startBtn.show()
    self.exitBtn.show()
    self.helpBtn.show()
    
    self.loseScreen.hide()
    self.menuBtn.hide()
    self.winScreen.hide()
    self.finalScoreText.hide()
    
    self.speedText.hide()
    self.distanceText.hide()
    self.rpmText.hide()
    self.scoreText.hide()
    self.gameLevelText.hide()
    self.timeText.hide()
    self.triesLeftText.hide()
    
    self.gameMusic.stop()
    self.menuMusic.play()
      
  def doPause(self):
    self.pause  = not self.pause
    if(self.pause):
      self.pauseScreen.show()
    else:
      self.pauseScreen.hide()
      
  def playGame(self):
    self.gameState = 'PLAY'
    
    self.triesLeft = 3
    self.gameLevel = 1
    
    self.imageObject.hide()
    self.startBtn.hide()
    self.exitBtn.hide()
    self.helpBtn.hide()
    
    self.menuMusic.stop()
    self.gameMusic.play()
    
    self.speedText.show()
    self.distanceText.show()
    self.rpmText.show()
    self.scoreText.show()
    self.gameLevelText.show()
    self.triesLeftText.show()
    self.timeText.show()
    
    # Physics
    self.setup()

  def update(self, task):
    dt = globalClock.getDt()
    if(not self.pause):
      if(self.gameState == 'RETRY'):
        return task.cont
      
      if (self.gameState == 'INIT'):
        self.accept('space', self.doContinue)
        self.text.setText('Press Space to Continue')
        
      if(self.gameState == 'PLAY'):
        if (self.steering > 0):
            self.steering -= dt * 50
        if (self.steering < 0):
            self.steering += dt * 50
            
        playerOldSpeed = self.vehicle.getCurrentSpeedKmHour()
        
        self.processInput(dt)
        self.processContacts(dt)
        self.world.doPhysics(dt, 10, 0.008)
  
        #calculate speed,rpm,distance and display text
        self.speed = self.vehicle.getCurrentSpeedKmHour()
        if(self.speed<0):
            self.speed = -self.speed
        self.speedText.setText('Speed: ' + str(int(self.speed)) + 'Km/h')
        self.distanceTravelled += self.speed*(dt/3600)
        self.distanceText.setText('Distance: '+str(float(int(self.distanceTravelled * 1000))/1000) + 'Km')
  
        playerNewSpeed = self.vehicle.getCurrentSpeedKmHour()
  
        playerAcceleration = (playerNewSpeed - playerOldSpeed) / (dt/60)
        #playerPosText = self.vehicleNP.getPos()
        #self.text.setText('Player position: %s'%playerPosText)
        self.rpmText.setText('Engine RPM: ' + str(int(((self.vehicle.getCurrentSpeedKmHour() / 60) * 1000) / (2 * 0.4 * 3.14159265))) + ' Rpm')
        
        self.triesLeftText.setText('Tries Left: ' + str(self.triesLeft))
  
        self.gameLevelText.setText('Level: '+ str(self.gameLevel))
        
        #update camera
        #position
        d = self.vehicleNP.getPos() - base.cam.getPos()
        if(d.length() > 8):
          base.cam.setX(base.cam.getX() + d.getX()*dt)
          base.cam.setY(base.cam.getY() + d.getY()*dt)
        base.cam.setZ(self.vehicleNP.getZ() + 4)
        #lookat
        base.cam.lookAt(self.vehicleNP.getPos()+Vec3(0,0,1))
        
        if(self.gameLevel == 1):
          if(self.vehicleNP.getZ() < -17):
            if(self.triesLeft > 0):
              self.gameState = 'RETRY'
            else:
              self.gameState = 'LOSE'
            self.doContinue()
        elif(self.gameLevel == 2):
          if(self.vehicleNP.getZ() < -20):
            if(self.triesLeft > 0):
              self.gameState = 'RETRY'
            else:
              self.gameState = 'LOSE'
            self.doContinue()
        elif(self.gameLevel == 3):
          if(self.vehicleNP.getZ() < -17):
            if(self.triesLeft > 0):
              self.gameState = 'RETRY'
            else:
              self.gameState = 'LOSE'
            self.doContinue()
            
        if(self.speed < 5):
          self.steeringIncrement = 120
        elif(self.speed >= 5 and self.speed < 10):
          self.steeringIncrement = 100
        elif(self.speed >= 10 and self.speed < 15):
          self.steeringIncrement = 80
        elif(self.speed >=15 and self.speed < 30):
          self.steeringIncrement = 60
          
        #spin the flag
        self.rot += 1
        self.flagNP.setHpr(self.rot,0,0)
        
        #time
        self.time += dt
        self.timeText.setText('Time: ' + str(int(self.time)))
        if(self.score > 0):
          self.score -= dt
        self.scoreText.setText('Score: '+str(int(self.score)))

    return task.cont

  def cleanup(self):
    self.world = None
    self.worldNP.removeNode()

  def setup(self):
    # Steering info
    self.steering = 0.0            # degree
    self.steeringClamp = 30.0      # degree
    self.steeringIncrement = 80.0 # degree per second
    
    self.worldNP = render.attachNewNode('World')

    # World
    self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
    #self.debugNP.show()

    self.world = BulletWorld()
    self.world.setGravity(Vec3(0, 0, -9.81))
    self.world.setDebugNode(self.debugNP.node())
    
    if(self.gameLevel == 1):
      #set score
      print('GameLevel')
      self.score = 1000
      self.distanceTravelled = 0
      self.time = 0
      # Plane
      img = PNMImage(Filename('media/terrain/SIMP_Assignment_2_Terrain_1.png'))
      shape = BulletHeightfieldShape(img, 50.0, ZUp)

      np = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
      np.node().addShape(shape)
      np.setPos(0, 0, 0)
      np.setCollideMask(BitMask32.allOn())

      self.world.attachRigidBody(np.node())
    
      #skybox
      skybox = loader.loadModel('media/models/skybox/skybox_01.X')
      skybox.reparentTo(render)

    # Chassis
      shape = BulletBoxShape(Vec3(0.6, 1.4, 0.5))
      ts = TransformState.makePos(Point3(0, 0, 1.0))

      self.vehicleNP = self.worldNP.attachNewNode(BulletRigidBodyNode('Vehicle'))
      self.vehicleNP.node().addShape(shape, ts)
      self.vehicleNP.setPos(-93, -88, -7)#-93, -88, -7) #(-82,65.8,-8) #(55,8.38,-6)#(45, -19, -8)#(-93, -88, -7)
      self.vehicleNP.setHpr(-90,0,0)
      self.vehicleNP.node().setMass(5.0)
      self.vehicleNP.node().setDeactivationEnabled(False)
      
      base.cam.setPos(self.vehicleNP.getPos().getX()+2,self.vehicleNP.getPos().getY()+2,self.vehicleNP.getPos().getZ()+2)

      self.world.attachRigidBody(self.vehicleNP.node())

      # Vehicle
      self.vehicle = BulletVehicle(self.world, self.vehicleNP.node())
      self.vehicle.setCoordinateSystem(ZUp)
      self.world.attachVehicle(self.vehicle)

      self.hummerNP = loader.loadModel('media/models/vehicle/body.X')
      self.hummerNP.reparentTo(self.vehicleNP)
  
      # Right front wheel
      np = loader.loadModel('media/models/vehicle/front_right.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3( 0.8,  0.9, 0.8), True, np)
  
      # Left front wheel
      np = loader.loadModel('media/models/vehicle/front_left.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3(-0.8,  0.9, 0.8), True, np)
  
      # Right rear wheel
      np = loader.loadModel('media/models/vehicle/back_right.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3( 0.8, -0.7, 0.8), False, np)
  
      # Left rear wheel
      np = loader.loadModel('media/models/vehicle/back_left.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3(-0.8, -0.7, 0.8), False, np)
      
      #Obstacles
      self.setupObstacleOne(Vec3(50, -5, -4), 1.8, Vec3(60, 0, 0))
      self.setupObstacleFour(Vec3(63.3, 59.2, -10), 1.5, Vec3(0,0,0))
      self.setupObstacleFour(Vec3(41, 57, -10), 1.5, Vec3(0,0,0))
      self.setupObstacleFour(Vec3(7.5, 53.8, -10), 1.5, Vec3(0,0,0))
      self.setupObstacleFour(Vec3(-28, 81.4, -10), 1.5, Vec3(0,0,0))
      self.setupObstacleSix(Vec3(-91, 81 , -6), 1, Vec3(60,0,0))
      
      #Goal
      self.setupGoal(Vec3(-101,90.6,-6.5))
      
      #self.vehicleNP.setPos(Vec3(6,52,-6))
      self.setupTerrain()
    elif(self.gameLevel == 2):
      self.distanceTravelled = 0
      self.time  = 0 
      # Plane
      img = PNMImage(Filename('media/terrain/SIMP_Assignment_2_Terrain_2.png'))
      shape = BulletHeightfieldShape(img, 50.0, ZUp)

      np = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
      np.node().addShape(shape)
      np.setPos(0, 0, 0)
      np.setCollideMask(BitMask32.allOn())

      self.world.attachRigidBody(np.node())
      
      #skybox
      skybox = loader.loadModel('media/models/skybox/skybox_01.X')
      skybox.reparentTo(render)

      # Chassis
      shape = BulletBoxShape(Vec3(0.6, 1.4, 0.5))
      ts = TransformState.makePos(Point3(0, 0, 1.0))

      self.vehicleNP = self.worldNP.attachNewNode(BulletRigidBodyNode('Vehicle'))
      self.vehicleNP.node().addShape(shape, ts)
      self.vehicleNP.setPos(-99.6,105,-11.8)#(88, 21, -11)#(34.3,8.4,-11.8)#(-99.6,105,-11.8)#(86.4,41.2,-12)
      self.vehicleNP.setHpr(-130,0,0)
      self.vehicleNP.node().setMass(5.0)
      self.vehicleNP.node().setDeactivationEnabled(False)
      
      base.cam.setPos(self.vehicleNP.getPos().getX()+2,self.vehicleNP.getPos().getY()+2,self.vehicleNP.getPos().getZ()+2)

      self.world.attachRigidBody(self.vehicleNP.node())

      # Vehicle
      self.vehicle = BulletVehicle(self.world, self.vehicleNP.node())
      self.vehicle.setCoordinateSystem(ZUp)
      self.world.attachVehicle(self.vehicle)

      self.hummerNP = loader.loadModel('media/models/vehicle/body.X')
      self.hummerNP.reparentTo(self.vehicleNP)
  
      # Right front wheel
      np = loader.loadModel('media/models/vehicle/front_right.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3( 0.8,  0.9, 0.8), True, np)
  
      # Left front wheel
      np = loader.loadModel('media/models/vehicle/front_left.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3(-0.8,  0.9, 0.8), True, np)
  
      # Right rear wheel
      np = loader.loadModel('media/models/vehicle/back_right.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3( 0.8, -0.7, 0.8), False, np)
  
      # Left rear wheel
      np = loader.loadModel('media/models/vehicle/back_left.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3(-0.8, -0.7, 0.8), False, np)
      
      self.setupObstacleFive(Vec3(91, 3, -9),1,Vec3(90,0,0))
      self.setupObstacleFive(Vec3(94,-19, -10),0.9,Vec3(90,0,0))
      self.setupObstacleFive(Vec3(85,-40, -10),1,Vec3(90,0,0))
      self.setupObstacleFour(Vec3(-33.5, 23.4,-14.5),1,Vec3(0,0,0))
      self.setupObstacleFour(Vec3(-43.3, 24.2,-14.5),1,Vec3(0,0,0))
      self.setupObstacleTwo(Vec3(34.7,20.9,-8.5),1,Vec3(90,0,0))
      self.setupObstacleTwo(Vec3(26.8,20.3,-8.5),1,Vec3(90,0,0))
      self.setupObstacleTwo(Vec3(42.1,22.5,-8.5),1,Vec3(90,0,0))
      #self.setupObstacleFive(Vec3(91,0.2, -8),2.1,Vec3(90,0,0))
            
      #Goal
      self.setupGoal(Vec3(94,-89.7,-10))
      self.setupTerrain()
    elif(self.gameLevel == 3):
      self.distanceTravelled = 0
      self.time  = 0 
      # Plane
      img = PNMImage(Filename('media/terrain/SIMP_Assignment_2_Terrain_3.png'))
      shape = BulletHeightfieldShape(img, 50.0, ZUp)

      np = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
      np.node().addShape(shape)
      np.setPos(0, 0, 0)
      np.setCollideMask(BitMask32.allOn())

      self.world.attachRigidBody(np.node())
      
      #skybox
      skybox = loader.loadModel('media/models/skybox/skybox_01.X')
      skybox.reparentTo(render)

      # Chassis
      shape = BulletBoxShape(Vec3(0.6, 1.4, 0.5))
      ts = TransformState.makePos(Point3(0, 0, 1.0))

      self.vehicleNP = self.worldNP.attachNewNode(BulletRigidBodyNode('Vehicle'))
      self.vehicleNP.node().addShape(shape, ts)
      self.vehicleNP.setPos(-110, -110, 0)
      self.vehicleNP.setHpr(-40,0,0)
      self.vehicleNP.node().setMass(5.0)
      self.vehicleNP.node().setDeactivationEnabled(False)
      
      base.cam.setPos(self.vehicleNP.getPos().getX()+2,self.vehicleNP.getPos().getY()+2,self.vehicleNP.getPos().getZ()+2)

      self.world.attachRigidBody(self.vehicleNP.node())

      # Vehicle
      self.vehicle = BulletVehicle(self.world, self.vehicleNP.node())
      self.vehicle.setCoordinateSystem(ZUp)
      self.world.attachVehicle(self.vehicle)

      self.hummerNP = loader.loadModel('media/models/vehicle/body.X')
      self.hummerNP.reparentTo(self.vehicleNP)
  
      # Right front wheel
      np = loader.loadModel('media/models/vehicle/front_right.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3( 0.8,  0.9, 0.8), True, np)
  
      # Left front wheel
      np = loader.loadModel('media/models/vehicle/front_left.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3(-0.8,  0.9, 0.8), True, np)
  
      # Right rear wheel
      np = loader.loadModel('media/models/vehicle/back_right.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3( 0.8, -0.7, 0.8), False, np)
  
      # Left rear wheel
      np = loader.loadModel('media/models/vehicle/back_left.X')
      np.reparentTo(self.worldNP)
      self.addWheel(Point3(-0.8, -0.7, 0.8), False, np)

      self.setupTerrain()
      
      #Goal
      self.setupGoal(Vec3(114,100,-13))
      
      #Obstacles
      self.setupObstacleFour(Vec3(-60, -73, -9), 1, Vec3(0, 0, 0))
      self.setupObstacleFour(Vec3(-63, -77, -9), 1, Vec3(0, 0, 0))
      self.setupObstacleTwo(Vec3(-15, -40, -3), 1, Vec3(0, 0, 0))
      self.setupObstacleFour(Vec3(-60, 12, -11), 1, Vec3(0, 0, 0))
      self.setupObstacleSix(Vec3(-15, 90, -6), 1.5, Vec3(-30, 0, 0))
      self.setupObstacleFour(Vec3(28, 87, -11), 1, Vec3(0, 0, 0))
      self.setupObstacleFour(Vec3(32, 90, -11), 1, Vec3(0, 0, 0))



  def addWheel(self, pos, front, np):
    wheel = self.vehicle.createWheel()

    wheel.setNode(np.node())
    wheel.setChassisConnectionPointCs(pos)
    wheel.setFrontWheel(front)

    wheel.setWheelDirectionCs(Vec3(0, 0, -1))
    wheel.setWheelAxleCs(Vec3(1, 0, 0))
    wheel.setWheelRadius(0.4)
    wheel.setMaxSuspensionTravelCm(40.0)

    wheel.setSuspensionStiffness(40.0)
    wheel.setWheelsDampingRelaxation(2.3)
    wheel.setWheelsDampingCompression(4.4)
    wheel.setFrictionSlip(100.0);
    wheel.setRollInfluence(0.1)

  def setupTerrain(self):
    if(self.gameLevel == 1):
      #terrain setting
      img = PNMImage(Filename('media/terrain/SIMP_Assignment_2_Terrain_1.png'))
      self.terrain = GeoMipTerrain("myTerrain") 
      self.terrain.setHeightfield(img) 
      self.terrain.getRoot().setSz(50) 
      self.terrain.setBlockSize(4) 
      #self.terrain.setFactor(10) 
      #self.terrain.setMinLevel(0)
      self.terrain.setNear(50)
      self.terrain.setFar(1000)
      self.terrain.setFocalPoint(base.camera)
      self.terrain.getRoot().reparentTo(render)
      offset = img.getXSize() / 2.0 - 0.5
      self.terrain.getRoot().setPos(-offset, -offset, -50 / 2.0) 
      self.terrain.generate() 
    
      #load textures 
      tex0 = loader.loadTexture("media/terrain/SIMP_Assignment_2_Terrain_1_d.png") 
      tex0.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex1 = loader.loadTexture("media/terrain/longGrass.png") 
      tex1.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex2 = loader.loadTexture("media/terrain/bigRockFace.png") 
      tex2.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex3 = loader.loadTexture("media/terrain/greenrough.png") 
      tex3.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex4 = loader.loadTexture("media/terrain/grayRock.png") 
      tex4.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex5 = loader.loadTexture("media/terrain/SIMP_Assignment_2_Terrain_1_c.png") 
      tex5.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex6 = loader.loadTexture("media/terrain/SIMP_Assignment_2_Terrain_1_l.png") 
      tex6.setMinfilter(Texture.FTLinearMipmapLinear) 
      #set mutiltextures 
      self.terrain.getRoot().setTexture( TextureStage('tex0'),tex0 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex1'),tex1 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex2'),tex2 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex3'),tex3 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex4'),tex4 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex5'),tex5 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex6'),tex6 ) 
      #load shader 
      self.terrain.getRoot().setShader(loader.loadShader('terraintexture.sha'))
    elif(self.gameLevel == 2):
      #terrain setting
      img = PNMImage(Filename('media/terrain/SIMP_Assignment_2_Terrain_2.png'))
      self.terrain = GeoMipTerrain("myTerrain") 
      self.terrain.setHeightfield(img) 
      self.terrain.getRoot().setSz(50) 
      self.terrain.setBlockSize(4) 
      #self.terrain.setFactor(10) 
      #self.terrain.setMinLevel(0)
      self.terrain.setNear(50)
      self.terrain.setFar(100)
      self.terrain.setFocalPoint(base.camera)
      self.terrain.getRoot().reparentTo(render)
      offset = img.getXSize() / 2.0 - 0.5
      self.terrain.getRoot().setPos(-offset, -offset, -50 / 2.0) 
      self.terrain.generate() 
    
      #load textures 
      tex0 = loader.loadTexture("media/terrain/SIMP_Assignment_2_Terrain_2_d.png") 
      tex0.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex1 = loader.loadTexture("media/terrain/sandripple.png") 
      tex1.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex2 = loader.loadTexture("media/terrain/orangesand.png") 
      tex2.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex3 = loader.loadTexture("media/terrain/grayRock.png") 
      tex3.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex4 = loader.loadTexture("media/terrain/bigRockFace.png") 
      tex4.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex5 = loader.loadTexture("media/terrain/SIMP_Assignment_2_Terrain_2_c.png") 
      tex5.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex6 = loader.loadTexture("media/terrain/SIMP_Assignment_2_Terrain_2_l.png") 
      tex6.setMinfilter(Texture.FTLinearMipmapLinear) 
      #set mutiltextures 
      self.terrain.getRoot().setTexture( TextureStage('tex0'),tex0 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex1'),tex1 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex2'),tex2 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex3'),tex3 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex4'),tex4 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex5'),tex5 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex6'),tex6 ) 
      #load shader 
      self.terrain.getRoot().setShader(loader.loadShader('terraintexture.sha'))
    elif(self.gameLevel == 3):
      #terrain setting
      img = PNMImage(Filename('media/terrain/SIMP_Assignment_2_Terrain_3.png'))
      self.terrain = GeoMipTerrain("myTerrain") 
      self.terrain.setHeightfield(img) 
      self.terrain.getRoot().setSz(50) 
      self.terrain.setBlockSize(4) 
      #self.terrain.setFactor(10) 
      #self.terrain.setMinLevel(0)
      self.terrain.setNear(50)
      self.terrain.setFar(100)
      self.terrain.setFocalPoint(base.camera)
      self.terrain.getRoot().reparentTo(render)
      offset = img.getXSize() / 2.0 - 0.5
      self.terrain.getRoot().setPos(-offset, -offset, -50 / 2.0) 
      self.terrain.generate() 
    
      #load textures 
      tex0 = loader.loadTexture("media/terrain/SIMP_Assignment_2_Terrain_3_d.png") 
      tex0.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex1 = loader.loadTexture("media/terrain/hardDirt.png") 
      tex1.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex2 = loader.loadTexture("media/terrain/littlerocks.png") 
      tex2.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex3 = loader.loadTexture("media/terrain/greenrough.png") 
      tex3.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex4 = loader.loadTexture("media/terrain/bigRockFace.png") 
      tex4.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex5 = loader.loadTexture("media/terrain/SIMP_Assignment_2_Terrain_3_c.png") 
      tex5.setMinfilter(Texture.FTLinearMipmapLinear) 
      tex6 = loader.loadTexture("media/terrain/SIMP_Assignment_2_Terrain_3_l.png") 
      tex6.setMinfilter(Texture.FTLinearMipmapLinear) 
      #set mutiltextures 
      self.terrain.getRoot().setTexture( TextureStage('tex0'),tex0 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex1'),tex1 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex2'),tex2 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex3'),tex3 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex4'),tex4 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex5'),tex5 ) 
      self.terrain.getRoot().setTexture( TextureStage('tex6'),tex6 ) 
      #load shader 
      self.terrain.getRoot().setShader(loader.loadShader('terraintexture.sha'))

  def setupObstacleOne(self, pos, scale, turn):
    
    #box A
    shape = BulletBoxShape(Vec3(3, 0.1, 0.1) * scale)
    
    bodyA = BulletRigidBodyNode('Box A')
    bodyNP= self.worldNP.attachNewNode(bodyA)
    bodyNP.node().addShape(shape)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(3, 0.1, 0.1)*2 * scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyA)
    
    # Box C
    shape = BulletBoxShape(Vec3(0.1, 0.1, 0.9)*scale)
    
    bodyC = BulletRigidBodyNode('Box C')
    bodyNP = self.worldNP.attachNewNode(bodyC)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(1.0)
    bodyNP.node().setLinearDamping(0.5)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(0.1, 0.1, 0.9)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyC)
    
    pivotA = Point3(0, 0, -0.1 * scale)
    pivotB = Point3(0, 0, 1 * scale)
    axisA = Vec3(1, 0, 0)
    axisB = Vec3(1, 0, 0)
    
    hinge = BulletHingeConstraint(bodyA, bodyC, pivotA, pivotB, axisA, axisB, True)
    hinge.setDebugDrawSize(2.0)
    hinge.setLimit(-90,90, softness=1.0, bias=0.3, relaxation=1.0)
    self.world.attachConstraint(hinge)
    
    # Box B
    shape = BulletBoxShape(Vec3(3, 2, 0.1)*scale)
    
    bodyB = BulletRigidBodyNode('Box B')
    bodyNP = self.worldNP.attachNewNode(bodyB)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(1.0)
    bodyNP.node().setLinearDamping(0.5)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn);
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(3, 2, 0.1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyB)
    
    # Hinge
    pivotA = Point3(0, 0, 0)
    pivotB = Point3(0, 0, -1 * scale)
    
    hinge = BulletHingeConstraint(bodyB, bodyC, pivotA, pivotB, axisA, axisB, True)
    hinge.setLimit(0,360, softness=1.0, bias=0.3, relaxation=1.0)
    self.world.attachConstraint(hinge)
  
  def setupObstacleTwo(self,pos,scale,turn):
    
    #box A
    shape = BulletBoxShape(Vec3(3, 0.1, 0.1)*scale)
    
    bodyA = BulletRigidBodyNode('Box A')
    bodyNP= self.worldNP.attachNewNode(bodyA)
    bodyNP.node().addShape(shape)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(3, 0.1, 0.1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyA)
    
    # Box B
    shape = BulletBoxShape(Vec3(0.1, 1, 1)*scale)
    
    bodyB = BulletRigidBodyNode('Box B')
    bodyNP = self.worldNP.attachNewNode(bodyB)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(100.0)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(0.1, 1, 1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyB)
    
    # Hinge
    pivotA = Point3(2, 0, 0)
    pivotB = Point3(0, 0, 2)
    axisA = Vec3(1, 0, 0)
    axisB = Vec3(1, 0, 0)
    
    hinge = BulletHingeConstraint(bodyA, bodyB, pivotA, pivotB, axisA, axisB, True)
    hinge.setDebugDrawSize(2.0)
    hinge.setLimit(-90,90, softness=1.0, bias=0.3, relaxation=1.0)
    self.world.attachConstraint(hinge)
    
    # Box C
    shape = BulletBoxShape(Vec3(0.1, 1, 1)*scale)
    
    bodyC = BulletRigidBodyNode('Box C')
    bodyNP = self.worldNP.attachNewNode(bodyC)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(100.0)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(0.1, 1, 1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyC)
    
    pivotA = Point3(-2, 0, 0)
    pivotB = Point3(0, 0, 2)
    
    hinge = BulletHingeConstraint(bodyA, bodyC, pivotA, pivotB, axisA, axisB, True)
    self.world.attachConstraint(hinge)
  
  def setupObstacleThree(self, pos, scale, turn):
    # Box A
    shape = BulletBoxShape(Vec3(0.1, 0.1, 0.1))
    
    bodyA = BulletRigidBodyNode('Box A')
    bodyA.setRestitution(1.0)
    bodyNP = self.worldNP.attachNewNode(bodyA)
    bodyNP.node().addShape(shape)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(0.1, 0.1, 0.1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyA)
    
    #Box B
    shape = BulletBoxShape(Vec3(0.1,0.1,0.1))
    
    bodyB = BulletRigidBodyNode('Box B')
    bodyB.setRestitution(1.0)
    bodyNP = self.worldNP.attachNewNode(bodyB)
    bodyNP.node().addShape(shape)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(0.1,0.1,0.1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyB)
    
    # Slider
    frameA = TransformState.makePosHpr(Point3(0, 0, 0), Vec3(0, 0, 0))
    frameB = TransformState.makePosHpr(Point3(0, 0, 0), Vec3(0, 0, 0))
    
    slider = BulletSliderConstraint(bodyA, bodyB, frameA, frameB, True)
    slider.setDebugDrawSize(2.0)
    slider.setLowerLinearLimit(0)
    slider.setUpperLinearLimit(12)
    slider.setLowerAngularLimit(-90)
    slider.setUpperAngularLimit(-85)
    self.world.attachConstraint(slider)
    
    # Box C
    shape = BulletBoxShape(Vec3(1, 3, 0.1))
    
    bodyC = BulletRigidBodyNode('Box C')
    bodyC.setRestitution(1.0)
    bodyNP = self.worldNP.attachNewNode(bodyC)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(0.1)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())  
    bodyNP.setPos(Vec3(pos.getX() + 3, pos.getY() - 4, pos.getZ()))
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(1, 3, 0.1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyC)
    
    bodyNP.node().setLinearVelocity(-100)
    
    # Slider
    frameA = TransformState.makePosHpr(Point3(0, 0, 0), Vec3(0, 0, 0))
    frameB = TransformState.makePosHpr(Point3(0, 0, 0), Vec3(0, 0, 0))
    
    slider = BulletSliderConstraint(bodyA, bodyC, frameA, frameB, True)
    slider.setDebugDrawSize(2.0)
    slider.setLowerLinearLimit(2)
    slider.setUpperLinearLimit(6)
    slider.setLowerAngularLimit(-90)
    slider.setUpperAngularLimit(-85)
    self.world.attachConstraint(slider)
  
  def setupObstacleFour(self, pos, scale, turn):
    #Start Here
    # Box A
    shape = BulletBoxShape(Vec3(0.01, 0.01, 0.01) * scale)
    bodyA = BulletRigidBodyNode('Box A')
    bodyNP = self.worldNP.attachNewNode(bodyA)
    bodyNP.node().addShape(shape)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos.getX(), pos.getY(), pos.getZ() + 4) #(0, 0, 4)

    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(0.01, 0.01, 0.01)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)

    self.world.attachRigidBody(bodyA)

    # Box B
    shape = BulletSphereShape(0.5*scale)

    bodyB = BulletRigidBodyNode('Sphere B')
    bodyNP = self.worldNP.attachNewNode(bodyB)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(10.0)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos.getX(), pos.getY(), pos.getZ() + 5) #(0, 0, 0.001)

    visNP = loader.loadModel('media/models/ball.egg')
    visNP.clearModelNodes()
    visNP.setScale(1.25*scale)
    visNP.reparentTo(bodyNP)
    
    bodyNP.node().setLinearVelocity(100)

    self.world.attachRigidBody(bodyB)

    # Cone
    frameA = TransformState.makePosHpr(Point3(0, 0, 0), Vec3(0, 0, 90))
    frameB = TransformState.makePosHpr(Point3(2, 0, 0)*scale, Vec3(0, 0, 0))

    cone = BulletConeTwistConstraint(bodyA, bodyB, frameA, frameB)
    cone.setDebugDrawSize(2.0)
    cone.setLimit(30, 90, 270, softness=1.0, bias=0.3, relaxation=10.0)
    self.world.attachConstraint(cone)
    
    # Box C
    shape = BulletBoxShape(Vec3(0.1, 0.1, 1)*scale)

    bodyC = BulletRigidBodyNode('Box C')
    bodyNP = self.worldNP.attachNewNode(bodyC)
    bodyNP.node().addShape(shape)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos.getX(), pos.getY(), pos.getZ() + 3)
    
    self.world.attachRigidBody(bodyC)

    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(0.1, 0.1, 1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
  def setupObstacleSix(self, pos, scale, turn):
    #box A
    shape = BulletBoxShape(Vec3(0.1, 0.1, 0.1)*scale)
    
    bodyA = BulletRigidBodyNode('Box A')
    bodyNP= self.worldNP.attachNewNode(bodyA)
    bodyNP.node().addShape(shape)
    bodyNP.setCollideMask(BitMask32.allOff())
    bodyNP.setPos(pos.getX()-2,pos.getY(),pos.getZ()+2.5)#-2,0,2.5)
    bodyNP.setHpr(turn)
    
    # Box B
    shape = BulletBoxShape(Vec3(2, 0.1, 3)*scale)
    
    bodyB = BulletRigidBodyNode('Box B')
    bodyNP = self.worldNP.attachNewNode(bodyB)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(1.0)
    bodyNP.node().setLinearDamping(0.5)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos.getX()-3,pos.getY(), pos.getZ())#, 0, 0)
    bodyNP.setHpr(turn)
    
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(2, 0.1, 3)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyB)
    
    
    # Hinge
    pivotA = Point3(-2, 0, -3)
    pivotB = Point3(-2, 0, -3)
    axisA = Vec3(0, 0, 1)
    axisB = Vec3(0, 0, 1)
    
    hinge = BulletHingeConstraint(bodyA, bodyB, pivotA, pivotB, axisA, axisB, True)
    hinge.setDebugDrawSize(2.0)
    hinge.setLimit(0,90, softness=1.0, bias=0.3, relaxation=1.0)
    self.world.attachConstraint(hinge)
    
    #box A
    shape = BulletBoxShape(Vec3(0.1, 0.1, 0.1)*scale)
    
    bodyA = BulletRigidBodyNode('Box A')
    bodyNP= self.worldNP.attachNewNode(bodyA)
    bodyNP.node().addShape(shape)
    bodyNP.setCollideMask(BitMask32.allOff())
    bodyNP.setPos(pos.getX()+2,pos.getY(),pos.getZ()+2.5)#2,0,2.5)
    bodyNP.setHpr(turn)
    
    # Box B
    shape = BulletBoxShape(Vec3(2, 0.1, 3)*scale)
    
    bodyB = BulletRigidBodyNode('Box B')
    bodyNP = self.worldNP.attachNewNode(bodyB)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(1.0)
    bodyNP.node().setLinearDamping(0.5)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos.getX()+4, pos.getY(), pos.getZ())# 0, 0)
    bodyNP.setHpr(turn)
    
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(2, 0.1, 3)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyB)
    
    pivotA = Point3(2, 0, -3)
    pivotB = Point3(2, 0, -3)
    
    hinge = BulletHingeConstraint(bodyA, bodyB, pivotA, pivotB, axisA, axisB, True)
    hinge.setLimit(-90,0, softness=1.0, bias=0.3, relaxation=1.0)
    self.world.attachConstraint(hinge)
    
  def setupObstacleFive(self, pos, scale, turn):
    #box A
    shape = BulletBoxShape(Vec3(3, 0.1, 0.1)*scale)
    
    bodyA = BulletRigidBodyNode('Box A')
    bodyNP= self.worldNP.attachNewNode(bodyA)
    bodyNP.node().addShape(shape)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(3, 0.1, 0.1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyA)
    
    # Box B
    shape = BulletBoxShape(Vec3(3, 2, 0.1)*scale)
    
    bodyB = BulletRigidBodyNode('Box B')
    bodyNP = self.worldNP.attachNewNode(bodyB)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(1.0)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(3, 2, 0.1)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyB)
    
    # Hinge
    pivotA = Point3(0, 0, 0)
    pivotB = Point3(0, 0, 5)
    axisA = Vec3(1, 0, 0)
    axisB = Vec3(1, 0, 0)
    
    hinge = BulletHingeConstraint(bodyA, bodyB, pivotA, pivotB, axisA, axisB, True)
    hinge.setDebugDrawSize(2.0)
    hinge.setLimit(-50,50, softness=0.5, bias=0.3, relaxation=0.6)
    self.world.attachConstraint(hinge)
    
    # Box C
    shape = BulletBoxShape(Vec3(0.1, 0.1, 0.9)*scale)
    
    bodyC = BulletRigidBodyNode('Box C')
    bodyNP = self.worldNP.attachNewNode(bodyC)
    bodyNP.node().addShape(shape)
    bodyNP.node().setMass(1.0)
    bodyNP.node().setDeactivationEnabled(False)
    bodyNP.setCollideMask(BitMask32.allOn())
    bodyNP.setPos(pos)
    bodyNP.setHpr(turn)
    
    visNP = loader.loadModel('media/models/box.egg')
    visNP.setScale(Vec3(0.1, 0.1, 0.9)*2*scale)
    visNP.clearModelNodes()
    visNP.reparentTo(bodyNP)
    
    self.world.attachRigidBody(bodyC)
    
    pivotA = Point3(0, 0, -1.1)
    pivotB = Point3(0, 0, 1)
    
    hinge = BulletHingeConstraint(bodyA, bodyC, pivotA, pivotB, axisA, axisB, True)
    hinge.setLimit(-90,90, softness=1.0, bias=0.3, relaxation=1.0)
    self.world.attachConstraint(hinge)
    
  def setupGoal(self, pos):
      # Goal
      shape = BulletBoxShape(Vec3(1, 1, 1))

      body = BulletRigidBodyNode('Flag')

      self.flagNP = self.worldNP.attachNewNode(body)
      self.flagNP.node().addShape(shape)
      self.flagNP.setCollideMask(BitMask32.allOn())
      self.flagNP.setPos(pos)
      
      visNP = loader.loadModel('media/models/Flag.X')
      visNP.clearModelNodes()
      visNP.reparentTo(self.flagNP)
    
      self.world.attachRigidBody(body)

  
game = RonnieRacer()
run()