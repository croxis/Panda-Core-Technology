from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from panda3d.core import Material, Point3
from panda3d.core import Texture
from panda3d.core import VBase4, Vec3
from panda3d.core import Shader
from panda3d.core import loadPrcFileData, loadPrcFile
from direct.showbase.ShowBase import ShowBase

from surface_mesh import ProceduralGasGiant, Body, create_side
import shapeGeneratorAdvanced
import shapeGenerator
import math
import appdirs

from panda3d.core import VirtualFileSystem

### Adjust imports for person projects as needed ###
from spacedrive.renderpipeline import DirectionalLight
from spacedrive.renderpipeline.Code.MovementController import MovementController
from spacedrive.renderpipeline.Code.RenderingPipeline import RenderingPipeline
import spacedrive.renderpipeline as renderpipeline
###                 ###


class Surface(Body):
    """Planet is a parent nodepath that the 6 side mesh nodepaths will parent
    to. Planet can be moved, scale, and rotated with no problems"""

    def init(self, scale, debug):
        self.sides = []
        for i in range(0, 6):
            m = create_side(self.node_path, debug, invert=True)
            m.set_scale(scale)
            self.sides.append(m)

        '''The side meshes are rotated here. They are moved to their correct
        position in the shader.'''
        self.sides[0].set_hpr(90, 90, 0)
        self.sides[1].set_hpr(-90, 90, 0)
        self.sides[2].set_hpr(0, 0, 0)
        self.sides[3].set_hpr(0, 180, 0)
        self.sides[4].set_hpr(0, 90, 0)
        self.sides[5].set_hpr(180, 90, 0)
        # create sane material defaults
        self.material = Material()
        self.material.set_diffuse(VBase4(0.7))
        self.material.set_ambient(VBase4(0.0))
        self.material.set_emission(VBase4(0.0))
        self.material.set_shininess(0.0)
        self.material.set_specular(VBase4(0.2, 0.0, 0.2, 0.0))

        for m in self.sides:
            m.set_material(self.material)
            '''m.set_shader_input('colorTexture', tex)
            m.set_shader_input('nightTesture', tex)
            m.set_shader_input('glossTexture', tex)'''

    def set_textures(self, texture_paths={}):
        """MultiTextures the surface. t_path is a string in the same format as
        loader.loadCubeMap('texture_#.png') for a multifile cubemap. The
        orientation is a little different than what is described in the panda
        manual.

        North pole is z-up."""
        for i in range(0, 6):
            diffuse = base.loader.loadTexture(texture_paths['diffuse'].replace('#',
                                                                           str(i)))
            diffuse.setMinfilter(Texture.FTLinearMipmapLinear)
            diffuse.setAnisotropicDegree(4)
            self.sides[i].set_texture(diffuse)

    def set_ambient(self, r, g, b, a):
        self.material.set_ambient(
            VBase4(float(r), float(g), float(b), float(a)))

    def set_diffuse(self, r, g, b, a):
        self.material.set_diffuse(
            VBase4(float(r), float(g), float(b), float(a)))

    def set_specular(self, r, g, b, a):
        self.material.set_specular(
            VBase4(float(r), float(g), float(b), float(a)))

    def set_shininess(self, n):
        self.material.set_shininess(n)

database = {'atmosphere': 1,
            'semimajor': 149598261, 'period': 365.256363004,
            'textures': {
                'diffuse': 'Textures/earth_#.png',
                'specular': 'Textures/earth_spec_#.png',
                'night': 'Textures/earth_night_#.png'},
            'orbit': {'a': 1.00000018,
                      'e': 'lambda d: 0.01673163 - 3.661e-07 * d',
                      'w': 'lambda d: 108.04266274 + 0.0031795260 * d',
                      'i': 'lambda d: -0.00054346 + -0.0001337178 * d',
                      'M': 'lambda d: -2.4631431299999917',
                      'N': 'lambda d: -5.11260389 + -0.0024123856 * d'},
            'mass': 5.9742e+24, 'radius': 6371000,
            'rotation': 1,
            'type': 'solid'}

def toggleSceneWireframe():
    base.wireframe = not base.wireframe
    print("Toggling wireframe:", base.wireframe)
    if base.wireframe:
        base.render.setRenderModeWireframe()
    else:
        base.render.clearRenderMode()


if __name__ == '__main__':
    loadPrcFile("configuration.prc")
    loadPrcFileData('', 'frame-rate-meter-scale 0.035')
    loadPrcFileData('', 'frame-rate-meter-side-margin 0.1')
    loadPrcFileData('', 'show-frame-rate-meter 1')
    loadPrcFileData('', 'window-title Saturn Test')
    loadPrcFileData('', "sync-video 0")
    loadPrcFileData('', 'task-timer-verbose 1')
    loadPrcFileData('', 'pstats-tasks 1')
    loadPrcFileData('', 'want-pstats 1')
    loadPrcFileData("", "textures-power-2 none")
    loadPrcFileData("", "win-size 1600 960")
    base = ShowBase()
    base.setSleep(0.001)
    base.wireframe = False
    base.planetframe = False
    render_pipeline = RenderingPipeline(base)
    cache_dir = appdirs.user_cache_dir('spacedrive', 'croxis')
    render_pipeline.getMountManager().setBasePath(os.path.dirname(os.path.realpath(renderpipeline.__file__)))
    render_pipeline.getMountManager().setWritePath(
        os.path.join(cache_dir, 'Shaders'))
    render_pipeline.loadSettings('pipeline.ini')
    vfs = VirtualFileSystem.getGlobalPtr()
    render_pipeline.create()
    #sandbox.base.camLens.set_far(100000)
    skybox = render_pipeline.getDefaultSkybox(scale=base.camLens.get_far()*0.8)
    skybox.set_scale(base.camLens.get_far()*0.8)
    skybox.reparent_to(base.render)

    mesh = Surface("Earth")
    mesh.set_textures(database['textures'])
    mesh.set_scale(6371)
    pos = 6371 + 9000
    mesh.set_pos(Point3(0, pos, 0))
    render_pipeline.setEffect(mesh.node_path, "Effects/Earth.effect")
    mesh.reparent_to(base.render)

    sun_light = DirectionalLight()
    sun_pos = Vec3(10000, pos, 0)
    sun_light.setSunDistance(20000)
    sun_light.setPos(sun_pos)
    sun_light.setPssmTarget(base.cam, base.camLens)
    sun_light.setColor(Vec3(1.0))
    sun_light.setShadowMapResolution(2048)
    sun_light.setCastsShadows(True)
    render_pipeline.addLight(sun_light)

    scattering = render_pipeline.getScattering()
    scattering.adjustSetting("atmosphereOffset", Vec3(0, pos, 0))
    scattering.adjustSetting("atmosphereScale", Vec3(1.0))
    render_pipeline.setScatteringSource(sun_light)

    controller = MovementController(base)
    controller.setup()

    base.accept("f3", toggleSceneWireframe)
    render_pipeline.reloadShaders()
    render_pipeline.onSceneInitialized()



    base.run()