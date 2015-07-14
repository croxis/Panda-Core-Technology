# -*- coding: utf-8 -*-
'''Code to model and show celestial bodies''' 
from panda3d.core import NodePath
from panda3d.core import Shader
from panda3d.core import Texture, TextureStage,  TexGenAttrib
from panda3d.core import Point3, Vec3, Vec4
from direct.task.Task import Task
# Import light!
from panda3d.core import PointLight

from math import sin, cos, pi, radians, degrees, sqrt, atan2
import math

# Data from: http://www.vendian.org/mncharity/dir3/starcolor/
colorDatabase = {'G2V': [255, 245, 242], 'M3V': [255, 206, 129], 'K2V': [255, 227, 196]}

starlights = []

class Body(NodePath):
    '''This is a physical body! Code relieved for bodies will be here.'''
    def __init__(self, name, bodyDB, isAtmo=False):
        '''We pass the name to the BaseObject, bodyDB will have vital info for us!'''
        NodePath.__init__(self, name)
        # Becuase the C++ Nodepath functins will not return any of these additions, we need a way to call our python extensions when using the C++ functions
        # Panda provides such a mechanism using the set/getPythonTag function. 
        NodePath.setPythonTag(self, 'subclass', self)
        self.reparentTo(render)
        self.setPos(0, 0, 0)
        self.cubemap = False
        # Set up grpahic components
        self.mesh = loader.loadModel("planet_sphere")
        self.mesh.setShaderAuto()
        self.atmo = None
        
        if '#' in bodyDB['texture']:
            self.cubemap = True
        
        if self.cubemap:
            self.mesh.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
            self.mesh.setTexProjector(TextureStage.getDefault(), render, self.mesh)
            self.mesh.setTexScale(TextureStage.getDefault(), 1,  1,  -1)
            self.mesh.setTexHpr(TextureStage.getDefault(), 90, -18, 90)
           
            texture = loader.loadCubeMap(bodyDB['texture'])
        else:
            texture = loader.loadTexture(bodyDB['texture'])
        texture.setMinfilter(Texture.FTLinearMipmapLinear)

        self.mesh.setTexture(texture, 1)
        
        if "spec" in bodyDB:
            sts = TextureStage('spec texture stage')
            sts.setMode(TextureStage.MGloss)
            stexture = loader.loadTexture(bodyDB['spec'])
            self.mesh.setTexture(sts,  stexture)

        if "glow" in bodyDB:
            gts = TextureStage('glow texture stage')
            gts.setMode(TextureStage.MGlow)
            gtexture = loader.loadTexture(bodyDB['glow'])
            self.mesh.setTexture(gts,  gtexture)

        self.mesh.reparentTo(render)
        
        #Atmo!
        if isAtmo:
            #self.atmo = loader.loadModel("planet_sphere")
            self.atmo = loader.loadModel("solar_sky_sphere") 

            self.atmo.reparentTo(render)
            self.atmo.setScale(1.025)
            
            outerRadius = self.atmo.getScale().getX()
            scale = 1/(outerRadius - self.mesh.getScale().getX())
            self.atmo.setShaderInput("fOuterRadius", outerRadius)
            self.atmo.setShaderInput("fInnerRadius", self.mesh.getScale().getX())
            self.atmo.setShaderInput("fOuterRadius2", outerRadius * outerRadius)
            self.atmo.setShaderInput("fInnerRadius2", self.mesh.getScale().getX() * self.mesh.getScale().getX()) 
            
            self.atmo.setShaderInput("fKr4PI", 0.000055 * 4 * 3.14159)
            self.atmo.setShaderInput("fKm4PI", 0.000015 * 4 * 3.14159)

            self.atmo.setShaderInput("fScale", scale)
            self.atmo.setShaderInput("fScaleDepth", 0.5)
            self.atmo.setShaderInput("fScaleOverScaleDepth", scale/0.5)

            # Currently hardcoded in shader
            self.atmo.setShaderInput("fSamples", 10.0)
            self.atmo.setShaderInput("nSamples", 10) 
            
            # These do sunsets and sky colors
            # Brightness of sun
            ESun = 15
            # Reyleight Scattering (Main sky colors)
            self.atmo.setShaderInput("fKrESun", 0.000055 * ESun)
            # Mie Scattering -- Haze and sun halos
            self.atmo.setShaderInput("fKmESun", 0.000015 * ESun)
            # Color of sun
            self.atmo.setShaderInput("v3InvWavelength", 1.0 / math.pow(0.650, 4),
                                            1.0 / math.pow(0.570, 4),
                                            1.0 / math.pow(0.465, 4))
                                            
            self.atmo.setShaderInput("v3CameraPos", base.camera.getPos().getX(),
                    base.camera.getPos().getY(),
                    base.camera.getPos().getZ())
            # Light vector from center of planet.       
            #lightv = light.getPos()
            lightv = base.bodies[0].mesh.getPos()
            lightdir = lightv / lightv.length()

            self.atmo.setShaderInput("v3LightPos", lightdir[0], lightdir[1], lightdir[2])
                
            self.atmo.setShaderInput("fCameraHeight", base.camera.getPos().length())
            self.atmo.setShaderInput("fCameraHeight2", base.camera.getPos().length()*base.camera.getPos().length())

            self.atmo.setShaderInput("g", 0.90)
            self.atmo.setShaderInput("g2", 0.81)
            self.atmo.setShaderInput("float", 2) 
            
            # All black
            #atmoShader = Shader.load(Shader.SLGLSL, "atmovertexshader.glsl", "atmofragmentshader.glsl")
            
            # None visible
            #atmoShader = Shader.load(Shader.SLGLSL, "SkyFromSpace.vert", "SkyFromSpace.frag")
            
            atmoShader = Shader.load("atmo.cg")
            
            self.atmo.setShader(atmoShader)
        
        # Initiate visual
        self.updateVisual(Task)
        taskMgr.add(self.updateVisual, 'planetRendering')
        self.setupRotation()
    
    def setupRotation(self):
        ''' Here we establish a rotation interval for the day/night cycle.
        This is also stored in data in Earth days so once again we need to convert into seconds.
        Idealy we would rotate this node and have the mesh attached. In practice this results in a great deal of jitter.'''
        rotation = 30
        dayPeriod = self.mesh.hprInterval(rotation, Vec3(360, 0, 0))
        dayPeriod.loop()
    
    def updateVisual(self, task):
        '''Updates the visual attributes and simulates sense of scale for distant objects.'''
        if self.atmo:
            """# Update atmosphere shader inputs
            # Atmosphere values
            #samples = 2.0
            samples = 10            
            #Kr = 0.0025
            Kr = 0.000055
            #Km = 0.0015
            Km = 0.000015
            #g = -0.95
            #g = -0.991
            g = 0.9
            g2 = 0.81
            ESun = 15.0
            Red = 0.65
            Green = 0.570
            Blue = 0.475
            
            exposure = 2
            wavelength = Vec3(0.731, 0.612, 0.455)
            invWavelength = Vec3(0,0,0)
            Red = 0.731
            Green = 0.612
            Blue = 0.455
            
            #scaleDepth = 0.25
            scaleDepth = 0.5
            
            #outerRadius = self.mesh.getScale()[0]*1.025
            outerRadius = abs(self.atmo.getScale().getX())
            innerRadius = self.mesh.getScale()[0]
            #scale = 1.0 / ((innerRadius * 1.025) - innerRadius)
            scale = 1/(outerRadius - self.mesh.getScale().getX()) 
            scaleOverScaleDepth = scale / scaleDepth;
            KrESun = Kr * ESun;
            KmESun = Km * ESun;
            Kr4PI = Kr * 4.0 * 3.14;
            Km4PI = Km * 4.0 * 3.14;

            invWavelength[0] = 1.0 / wavelength[0] ** 4.0
            invWavelength[1] = 1.0 / wavelength[1] ** 4.0
            invWavelength[2] = 1.0 / wavelength[2] ** 4.0

            
            #self.atmo.setShaderInput("v3CameraPos", base.camera.getPos())
            self.atmo.setShaderInput("v3CameraPos", base.camera.getPos().getX(),
                base.camera.getPos().getY(),
                base.camera.getPos().getZ()) 
                    
            #for light in starlights:
            #    self.atmo.setShaderInput("v3LightPos", light.getPos(render))
            # Light vector from center of planet.       
            lightv = base.bodies[0].mesh.getPos()
            lightdir = lightv / lightv.length()

            self.atmo.setShaderInput("v3LightPos", lightdir[0], lightdir[1], lightdir[2]) 

            #self.atmo.setShaderInput("v3InvWavelength", invWavelength)
            # Color of sun
            self.atmo.setShaderInput("v3InvWavelength", 1.0 / math.pow(0.650, 4),
                                            1.0 / math.pow(0.570, 4),
                                            1.0 / math.pow(0.465, 4)) 
            
            #cameraHeight = (base.camera.getPos()-self.mesh.getPos()).length()
            cameraHeight = base.camera.getPos().length()

            self.atmo.setShaderInput("fCameraHeight", cameraHeight)
            self.atmo.setShaderInput("fCameraHeight2", cameraHeight**2)
            
            self.atmo.setShaderInput("fInnerRadius", self.mesh.getScale()[0])
            self.atmo.setShaderInput("fInnerRadius2", self.mesh.getScale()[0]**2)
            
            

            self.atmo.setShaderInput("fOuterRadius", outerRadius)
            self.atmo.setShaderInput("fOuterRadius2", outerRadius**2)
            self.atmo.setShaderInput("fKrESun", Kr*ESun)
            self.atmo.setShaderInput("fKmESun", Km*ESun)
            self.atmo.setShaderInput("fKr4PI", Kr*4*math.pi)
            self.atmo.setShaderInput("fKm4PI", Km*4*math.pi)
            
            self.atmo.setShaderInput("fScale", scale)
            self.atmo.setShaderInput("fScaleDepth", scaleDepth)
            self.atmo.setShaderInput("fScaleOverScaleDepth", scaleOverScaleDepth)
            
            self.atmo.setShaderInput("g", g)
            self.atmo.setShaderInput("g2", g*g)
            self.atmo.setShaderInput("nSamples", 10)
            self.atmo.setShaderInput("fSamples", samples)

            self.atmo.setShaderInput("fexposure", 2.0)"""
            
            self.atmo.setShaderInput("v3CameraPos", base.camera.getPos().getX(),
                base.camera.getPos().getY(),
                base.camera.getPos().getZ())
            self.atmo.setShaderInput("fCameraHeight", base.camera.getPos().length())
            self.atmo.setShaderInput("fCameraHeight2", base.camera.getPos().length()*base.camera.getPos().length()) 
        
        return task.cont


class Star(Body):
    '''This is a star! It will require some additional data and different data from planets. This is our main light caster in the solar system. Just as we need to simulate mesh distance, we will need to simulate light intensity as well.'''
    def __init__(self, name, bodyDB):
        Body.__init__(self, name, bodyDB)
        self.mesh.reparentTo(render)
        self.spectral = bodyDB['spectral']
        
        # We use the data from the spectral database to properly color our star.
        color = colorDatabase[self.spectral]
        self.mesh.setColor(color[0]/255.0,color[1]/255.0,color[2]/255.0,1)
        
        # We will use a point light to cast our main light
        self.light = self.mesh.attachNewNode( PointLight( "sunPointLight" ) )
        # Color is set by spectral type. THIS IS NOT PROPER BLACKBODY!
        self.light.node().setColor( Vec4(color[0]/255.0,color[1]/255.0,color[2]/255.0,1) )
        # Attenuation controls how the light fades with distance. The numbers are
        # The three values represent the three constants (constant, linear, and
        # quadratic) in the internal lighting equation. The higher the numbers the
        # shorter the light goes.
        #self.light.node().setAttenuation( Vec3( .1, 0.04, 0.0 ) ) 
        texture1 = loader.loadTexture('sun_1k_tex.jpg')
        ts1 = TextureStage('textures1')
        ts1.setMode(TextureStage.MGlow)
        self.mesh.setTexture(ts1, texture1)
        render.setLight( self.light )
        starlights.append(self.light)
