from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'frame-rate-meter-scale 0.035')
loadPrcFileData('', 'frame-rate-meter-side-margin 0.1')
loadPrcFileData('', 'show-frame-rate-meter 1')
loadPrcFileData('', 'window-title ' + "Planet Prototype")
loadPrcFileData('', "sync-video 0")
loadPrcFileData('', 'basic-shaders-only #f')
#loadPrcFileData('', "show-buffers #t")
#loadPrcFileData('', 'dump-generated-shaders #t')
#loadPrcFileData('', 'pstats-tasks 1')
#loadPrcFileData('', 'want-pstats 1')
#loadPrcFileData('', 'threading-model Cull/Draw')

import direct.directbase.DirectStart

from direct.filter.FilterManager import FilterManager
from panda3d.core import CardMaker, NodePath, Shader, Texture

'''const float Rg = 6360.0;
const float Rt = 6420.0;
const float RL = 6421.0;
'''
TRANSMITTANCE_W = 256;
TRANSMITTANCE_H = 64;

transmittance_buffer = base.win.makeTextureBuffer(
    "transmittance_buffer",
    TRANSMITTANCE_W,
    TRANSMITTANCE_H
    )

'''texture = transmittance_buffer.getTexture()
transmittance_buffer.setSort(-100)
transmittance_camera = base.makeCamera(transmittance_buffer)
transmittance_scene = NodePath('transmittance scene')
transmittance_scene.setShaderInput("g_Rg", 1.0)
transmittance_scene.setShaderInput("Rt", 1.0094)
transmittance_scene.setShaderInput("RL", 1.15)
shader = Shader.load(Shader.SLGLSL, "atmoshaders/simple_vertex.glsl", "atmoshaders/transmittance.glsl")
cm = CardMaker('card')
card = transmittance_scene.attachNewNode(cm.generate())
card.setShader(shader)
transmittance_camera.reparent_to(transmittance_scene)'''

'''manager = FilterManager(base.win, base.cam)
tex = Texture()
quad = manager.renderSceneInto(colortex=tex)
quad.setShaderInput("g_Rg", 1.0)
quad.setShaderInput("Rt", 1.0094)
quad.setShaderInput("RL", 1.15)
shader = Shader.load(Shader.SLGLSL, "atmoshaders/simple_vertex.glsl", "atmoshaders/transmittance.glsl")
quad.setShader(shader)'''


def shader_update(task):
    #quad.setShaderInput()
    return task.cont


#taskMgr.add(shader_update, 'shaderUpdate')

#texture.write('test.png')

import surface_mesh
np = surface_mesh.create_mesh(render)
np.setShaderInput("Rg", 6360.0)
np.setShaderInput("Rt", 6420.0)
np.setShaderInput("RL", 6421.0)
shader = Shader.load(Shader.SLGLSL, "atmoshaders/simple_vertex.glsl", "atmoshaders/transmittance.glsl")
np.set_shader(shader)
#np.set_texture(texture)

def shaderUpdate(task):
    #print(base.camera.get_pos())
    return task.cont

taskMgr.add(shaderUpdate, 'shaderUpdate')

def toggleWireframe():
    base.toggleWireframe()

base.accept('w', toggleWireframe)

run()
