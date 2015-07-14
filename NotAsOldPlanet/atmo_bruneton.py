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
import surface_mesh
atmo = surface_mesh.create_mesh(render)
#atmo = surface_mesh.make_atmosphere()
#atmo = loader.loadModel("planet_sphere")
#atmo = loader.loadModel("solar_sky_sphere")
#atmosphere.reparent_to(planet.node_path)
#import shapeGenerator
#atmo = shapeGenerator.Sphere(segements=64)
atmo.reparent_to(render)
#atmo.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
#atmo.set_scale(1.025)

atmo.setShaderInput("Rg", 6360.0)
atmo.setShaderInput("Rt", 6420.0)
atmo.setShaderInput("RL", 6421.0)

atmo.set_shader(
    Shader.load(Shader.SLGLSL,
        'atmoshaders/simple_vertex.glsl',
        'atmoshaders/transmittance.glsl'))
#atmo.node_path.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))



def shaderUpdate(task):
    #TODO: Convert to relative positions, not world coords
    return task.cont

taskMgr.add(shaderUpdate, 'shaderUpdate')


def toggleWireframe():
    base.toggleWireframe()

base.accept('w', toggleWireframe)

run()
