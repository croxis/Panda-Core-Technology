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

import AtmosphericScattering
atmo = AtmosphericScattering.AtmosphericScattering()
atmo.init()



def shaderUpdate(task):
    #TODO: Convert to relative positions, not world coords
    return task.cont

taskMgr.add(shaderUpdate, 'shaderUpdate')


def toggleWireframe():
    base.toggleWireframe()

base.accept('w', toggleWireframe)

run()
