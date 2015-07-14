from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'frame-rate-meter-scale 0.035')
loadPrcFileData('', 'frame-rate-meter-side-margin 0.1')
loadPrcFileData('', 'show-frame-rate-meter 1')
loadPrcFileData('', 'window-title ' + "Planet Prototype")
loadPrcFileData('', "sync-video 0")
loadPrcFileData('', 'basic-shaders-only #f')
#loadPrcFileData('', 'dump-generated-shaders #t')
#loadPrcFileData('', 'pstats-tasks 1')
#loadPrcFileData('', 'want-pstats 1')
#loadPrcFileData('', 'threading-model Cull/Draw')

import direct.directbase.DirectStart
#base.setBackgroundColor(0.0, 0.0, 0.0) 

from panda3d.core import PointLight
light = PointLight('light')
lightnp = render.attachNewNode(light)
lightnp.set_pos(0, -1000, 0)
render.set_light(lightnp)

from panda3d.core import CullFaceAttrib, Shader
import math
#atmo = surface_mesh.make_atmosphere()
#atmo = loader.loadModel("planet_sphere")
atmo = loader.loadModel("solar_sky_sphere")
#atmosphere.reparent_to(planet.node_path)
#import shapeGenerator
#atmo = shapeGenerator.Sphere(segements=64)
atmo.reparent_to(render)
#atmo.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
atmo.set_scale(1.025)
atmo.set_shader(
    Shader.load(Shader.SLGLSL,
        'atmoshaders/oneil_sky_from_space_vert.glsl',
        'planet_atmosphere_frag.glsl'))
#atmo.node_path.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))


outerRadius = abs(atmo.get_scale().getX())
scale = 1/(outerRadius - planet.get_scale().getX())

atmo.set_shader_input("fOuterRadius", outerRadius)
atmo.set_shader_input("fInnerRadius", planet.get_scale().getX())
atmo.set_shader_input("fOuterRadius2", outerRadius * outerRadius)
atmo.set_shader_input("fInnerRadius2", planet.get_scale().getX() * planet.get_scale().getX())

#atmo.set_shader_input("fKr4PI", 0.0025 * 4 * 3.14159)
#atmo.set_shader_input("fKm4PI", 0.0015 * 4 * 3.14159)
atmo.setShaderInput("fKr4PI", 0.000055 * 4 * 3.14159)
atmo.setShaderInput("fKm4PI", 0.000015 * 4 * 3.14159) 

atmo.set_shader_input("fScale", scale)
atmo.set_shader_input("fScaleDepth", 0.25)
#atmo.setShaderInput("fScaleDepth", 0.5) 
#atmo.set_shader_input("fScaleOverScaleDepth", scale/0.5)
atmo.set_shader_input("fScaleOverScaleDepth", scale/0.25)

# These do sunsets and sky colors
# Brightness of sun
ESun = 15
# Reyleight Scattering (Main sky colors)
atmo.set_shader_input("fKrESun", 0.0025 * ESun)
# Mie Scattering -- Haze and sun halos
atmo.set_shader_input("fKmESun", 0.0015 * ESun)
# Color of sun
atmo.set_shader_input("v3InvWavelength", 1.0 / math.pow(0.650, 4),
                                  1.0 / math.pow(0.570, 4),
                                  1.0 / math.pow(0.475, 4))
                                 
atmo.set_shader_input("g", 0.90)
atmo.set_shader_input("g2", 0.81)
atmo.set_shader_input("float", 2)


def shaderUpdate(task):
    #TODO: Convert to relative positions, not world coords
    atmo.set_shader_input("v3CameraPos", base.camera.getPos().getX(),
        base.camera.getPos().getY(),
        base.camera.getPos().getZ())
    atmo.set_shader_input("fCameraHeight", base.camera.getPos().length())
    atmo.set_shader_input("fCameraHeight2", base.camera.getPos().length()
        *base.camera.getPos().length())
    # Light vector from center of planet.       
    lightv = lightnp.getPos()
    lightdir = lightv / lightv.length()
    atmo.set_shader_input("v3LightPos", lightdir[0], lightdir[1], lightdir[2]) 
    return task.cont

taskMgr.add(shaderUpdate, 'shaderUpdate')


def toggleWireframe():
    base.toggleWireframe()

base.accept('w', toggleWireframe)

run()
