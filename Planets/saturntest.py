# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from panda3d.core import Material, NodePath, Point3, Shader, Texture, VBase4
from panda3d.core import Vec3, VirtualFileSystem, TransparencyAttrib
from panda3d.core import loadPrcFileData, loadPrcFile
from direct.showbase.ShowBase import ShowBase

from surface_mesh import ProceduralGasGiant, Body
import shapeGeneratorAdvanced
import shapeGenerator
import math
import appdirs

### Adjust imports for person projects as needed ###
from spacedrive.renderpipeline import DirectionalLight, RenderingPipeline
import spacedrive.renderpipeline as renderpipeline
###                 ###

__author__ = 'croxis'


class Ring(Body):
    """Ring system. Parent to parent planet."""
    def __init__(self, name, scale=1, debug=False, outer_radius=3.0, inner_radius=1.15):
        """Debug will generate colored pixels for fun time. self.init()
        is called for specific body type inits."""
        self.name = name
        self.node_path = NodePath(name)
        base.accept('h', self.node_path.hide)
        base.accept('j', self.node_path.show)
        self.init(scale=scale, debug=debug, outer_radius=outer_radius, inner_radius=inner_radius)

    def init(self, scale=1, debug=False, outer_radius=3.0, inner_radius=1.15):
        # http://johnwhigham.blogspot.com/2011/11/planetary-rings.html
        # Px shader use to clip to make smooth. Must extend outer radius for this
        numSides = 16.0
        vert_radius = outer_radius/math.cos(math.pi/numSides)
        print("Vert radius:", vert_radius)
        self.node_path = shapeGenerator.Circle(outer_radius=vert_radius, inner_radius=inner_radius)
        #self.node_path.set_transparency(TransparencyAttrib.MBinary, 1)
         # create sane material defaults
        self.material = Material()
        self.material.set_diffuse(VBase4(0.7))
        self.material.set_ambient(VBase4(0.0))
        self.material.set_emission(VBase4(0.0))
        self.material.set_shininess(0.0)
        self.material.set_specular(VBase4(0.224, 0.0, 0.5, 0))
        self.node_path.set_material(self.material)
        self.node_path.setTwoSided(True)

    def load_shaders(self):
        #shaders = Shader.load(Shader.SL_GLSL,
        #                      'ring_vertex.glsl',
        #                      'ring_fragment.glsl')
        #self.node_path.set_shader(shaders, 51)
        pass

    def load_texture_special(self):
        diffuse = base.loader.loadTexture('ring_color.png', 'ring_alpha.png')
        #Dust rings alpha might be needed
        diffuse.setAnisotropicDegree(2)
        diffuse.setMinfilter(Texture.FTLinearMipmapLinear)
        self.node_path.set_texture(diffuse)


# Will use an icosphere as there is no "land" to worry about.
class GasGiant(ProceduralGasGiant):
    def init(self, scale=1, debug=False):
        self.node_path = shapeGeneratorAdvanced.GasIcoSphere(1, 5)
        # create sane material defaults
        self.material = Material()
        self.material.set_diffuse(VBase4(0.13))
        self.material.set_ambient(VBase4(0.0))
        self.material.set_emission(VBase4(0.0))
        self.material.set_shininess(0.0)
        self.material.set_specular(VBase4(0.01))
        self.node_path.set_material(self.material)

    def load_shaders(self):
        shaders = Shader.load(Shader.SL_GLSL,
                              'gas_giant_vertex.glsl',
                              'gas_giant_fragment.glsl',
                              '',
                              "Shader/DefaultShaders/Opaque/tesscontrol.glsl",
                              "Shader/DefaultShaders/Opaque/tesseval.glsl")
        shaders = Shader.load(Shader.SL_GLSL,
                              'gas_giant_vertex.glsl',
                              'gas_giant_fragment.glsl')
        #convertToPatches(self.node_path)
        self.node_path.set_shader(shaders, 51)

    def load_texture_special(self):
        diffuse = base.loader.loadTexture('saturn_color.png')
        self.node_path.set_texture(diffuse)


def toggleSceneWireframe():
    base.wireframe = not base.wireframe
    print("Toggling wireframe:", base.wireframe)
    if base.wireframe:
        base.render.setRenderModeWireframe()
    else:
        base.render.clearRenderMode()


def toggleSceneWireframe2():
    base.planetframe = not base.planetframe
    print("Toggling planetframe:", base.planetframe)
    if base.planetframe:
        saturn.node_path.setRenderModeWireframe()
        rings.node_path.setRenderModeWireframe()
    else:
        saturn.node_path.clearRenderMode()
        rings.node_path.clearRenderMode()


database = {'atmosphere': 1,
            'semimajor': 149598261, 'period': 365.256363004,
            'textures': {
                'diffuse': 'Planets/Earth/textures/earth_#.png',
                'specular': 'Planets/Earth/textures/earth_spec_#.png',
                'night': 'Planets/Earth/textures/earth_night_#.png'},
            'orbit': {'a': 1.00000018,
                      'e': 'lambda d: 0.01673163 - 3.661e-07 * d',
                      'w': 'lambda d: 108.04266274 + 0.0031795260 * d',
                      'i': 'lambda d: -0.00054346 + -0.0001337178 * d',
                      'M': 'lambda d: -2.4631431299999917',
                      'N': 'lambda d: -5.11260389 + -0.0024123856 * d'},
            'mass': 5.9742e+24, 'radius': 58232,
            'rotation': 1,
            'type': 'solid'}


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
    render_pipeline.loadSettings('pipeline_noScatter.ini')
    vfs = VirtualFileSystem.getGlobalPtr()
    render_pipeline.create()
    #sandbox.base.camLens.set_far(100000)
    skybox = render_pipeline.getDefaultSkybox(scale=base.camLens.get_far()*0.8)
    skybox.set_scale(base.camLens.get_far()*0.8)
    skybox.reparent_to(base.render)

    scale = 10
    saturn = GasGiant("Saturn")
    #saturn.set_scale(database['radius']/2.0)
    saturn.set_scale(scale)
    #pos = database['radius']/2.0 * 2.5
    pos = 5
    pos = 0
    print("Saturn position:", pos)
    saturn.set_pos(Point3(0, pos, 0))
    saturn.load_texture_special()
    saturn.load_shaders()
    saturn.reparent_to(base.render)

    rings = Ring("Rings")
    rings.set_pos(Point3(0, pos, 0))
    rings.set_scale(scale)
    rings.load_texture_special()
    render_pipeline.setEffect(rings.node_path, "Ring.effect", {
        "transparent": True
    })
    rings.reparent_to(base.render)

    sun_light = DirectionalLight()
    sun_light.setDirection(Vec3(10, pos, 5))
    sun_light.setPssmTarget(base.cam, base.camLens)
    sun_light.setColor(Vec3(1.0))
    sun_light.setShadowMapResolution(2048)
    sun_light.setCastsShadows(True)  # Must go last
    render_pipeline.addLight(sun_light)

    base.accept("f3", toggleSceneWireframe)
    base.accept("f4", toggleSceneWireframe2)
    render_pipeline.reloadShaders()
    render_pipeline.onSceneInitialized()

    base.run()
