from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'frame-rate-meter-scale 0.035')
loadPrcFileData('', 'frame-rate-meter-side-margin 0.1')
loadPrcFileData('', 'show-frame-rate-meter 1')
loadPrcFileData('', 'window-title ' + "Planet Prototype")
loadPrcFileData('', "sync-video 0")
loadPrcFileData('', 'basic-shaders-only #f')
#loadPrcFileData('', 'dump-generated-shaders #t')


import direct.directbase.DirectStart
from panda3d.core import PointLight, Shader

### Planet Generator ###
from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexData
from panda3d.core import GeomVertexFormat, GeomVertexWriter
from panda3d.core import NodePath, Shader, Vec3


def myNormalize(myVec):
    myVec.normalize()
    return myVec

format = GeomVertexFormat.getV3n3c4t2()
vdata = GeomVertexData('quadFace', format, Geom.UHDynamic)
vertex = GeomVertexWriter(vdata, 'vertex')
normal = GeomVertexWriter(vdata, 'normal')
color = GeomVertexWriter(vdata, 'color')
texcoord = GeomVertexWriter(vdata, 'texcoord')


def create_mesh(parentnp, debug=False):
    '''This creates a simple 17x17 grid mesh for the sides of our cube.
    The ultimate goal is to use a LOD system, probably based on quadtrees.
    If debug is true then we get a color gradiant on our vertexes.'''
    x = -1.0
    y = -1.0
    vertex_count = 0
    u = 0.0
    v = 0.0

    WIDTH_STEP = 2/16.0

    while y <= 1.0:
        while x <= 1.0:
            vertex.addData3f(x, y, 0)
            normal.addData3f(myNormalize((Vec3(2*x-1, 2*y-1, 2*0-1))))
            if debug:
                color.addData4f(1.0, u, v, 1.0)
            texcoord.addData2f(u, v)
            vertex_count += 1
            x += WIDTH_STEP
            u += WIDTH_STEP/2.0
        x = -1.0
        u = 0
        y += WIDTH_STEP
        v += WIDTH_STEP/2.0

    print vertex_count
    triangles = []

    for y in range(0, 16):
        for x in range(0, 16):
            v = 17 * y + x
            tri = GeomTriangles(Geom.UHDynamic)
            tri.addVertex(v)
            tri.addVertex(v+1)
            tri.addVertex(v+17)
            tri.closePrimitive()
            triangles.append(tri)

            tri = GeomTriangles(Geom.UHDynamic)
            tri.addVertex(v+1)
            tri.addVertex(v+18)
            tri.addVertex(v+17)
            
            tri.closePrimitive()
            triangles.append(tri)

    mesh = Geom(vdata)
    for t in triangles:
        mesh.addPrimitive(t)
    mnode = GeomNode('quadface')
    mnode.addGeom(mesh)
    nodePath = parentnp.attachNewNode(mnode)
    return nodePath


class Surface(object):
    '''planet is a parent nodepath that the 6 side mesh nodepaths will parent to.
    planet can be moved, scale, and rotated with no problems'''
    def __init__(self, name='planet', debug=False):
        '''Debug will generate colored pixles for fun time'''
        self.node_path = NodePath(name)
        shaders = Shader.load(Shader.SLGLSL, 'planet_surface_vert.glsl', 'planet_surface_frag.glsl')
        self.node_path.setShader(shaders)

        self.sides = []
        for i in range(0, 6):
            m = create_mesh(self.node_path, debug)
            self.sides.append(m)

        '''The side meshes are rotated here. They are moved to their correct
        position in the shader'''
        self.sides[0].set_hpr(90, 90, 0)
        self.sides[1].set_hpr(-90, 90, 0)
        self.sides[2].set_hpr(0, 0, 0)
        self.sides[3].set_hpr(0, 180, 0)
        self.sides[4].set_hpr(0, 90, 0)
        self.sides[5].set_hpr(180, 90, 0)

    def set_pos(self, *args):
        self.node_path.set_pos(args)

    def set_scale(self, *args):
        self.node_path.set_scale(args)

    def reparent_to(self, *args):
        self.node_path.reparent_to(args)

    def set_texture(self, texture_path):
        '''Textures the surface. texture_path is a string in the same format as
        loader.loadCubeMap('texture_#.png') for a multifile cubemap. The orientation
        is a little different than what is described in the panda manual.

        North pole is z-up'''
        for i in range(0, 6):
            tex = loader.loadTexture(texture_path.replace('#', str(i)))
            self.sides[i].set_texture(tex)


def make_planet(name='planet', debug=False):
    return Surface(name, debug)

### END PLANET GENERATOR ###


planet = make_planet()
planet.reparent_to(render)

light = PointLight('light')
lightnp = render.attachNewNode(light)
lightnp.set_pos(0, -10, 0)
render.set_light(lightnp)

#axis = loader.loadModel('zup-axis')
#axis.reparent_to(render)

sphere = loader.loadModel('smiley')
sphere.set_pos(3, 0, 0)
sphere.reparent_to(render)
shaders = Shader.load(Shader.SLGLSL, 'phong_vert.glsl', 'phong_frag2.glsl')
sphere.setShader(shaders)

shaders = Shader.load(Shader.SLGLSL, 'planet_surface_phong_vert.glsl', 'phong_frag2.glsl')
planet.node_path.setShader(shaders)

def toggleWireframe():
    base.toggleWireframe()

base.accept('w', toggleWireframe)

run()
