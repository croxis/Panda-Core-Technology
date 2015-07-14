


# Neccessary modules
from panda3d.core import GraphicsPipe, loadPrcFileData, WindowProperties,FrameBufferProperties
from panda3d.core import GraphicsOutput, Texture, Shader, CardMaker, NodePath, Vec4, Camera, OrthographicLens
from direct.showbase.ShowBase import ShowBase, TexturePool, PandaSystem
from direct.filter.FilterManager import FilterManager

from direct.gui.OnscreenImage import OnscreenImage


# CFG
loadPrcFileData("", """
win-size 1900 970
show-frame-rate-meter #t
sync-video 0
show-buffers #t
textures-power-2 none
    """)



def file_get_contents(filename):
    with open(filename) as f:
        return f.read()

def file_put_contents(filename, content, append = False):
    with open(filename, 'a' if append else 'w') as f:
        f.write(content)


def parseShaderContent(content):
    content = content.replace("\r", "")
    return content

# Generates a shader from a collection of files
def create_shader(files, has_geometry = False, name = ""):

    content = "//Cg\n"
    content += "//Cg profile gp4vp gp4fp "
    if has_geometry:
        content += "gp4gp"
    content += "\n\n"

    content += "//" * 30 + "\n"
    content += "//" + "\n"
    content += "// Auto-Generated-Shader '" + str(name) + "'\n"
    content += "//" + "\n"
    content += "// Generated from: \n" 

    for f in files:
        content += "//  - " + f + "\n"

    content += "//" + "\n"
    content += "//" * 30 + "\n"
    content += "\n\n"

    for f in files:
        content += "\n\n"
        content += "//" * 30
        content += "\n// FILE: "+f + "\n"
        content += "//" * 30
        content += "\n"
        c = file_get_contents(f)
        content += parseShaderContent(c) + "\n\n"

    dumped = "shader_dump/" + name + ".cg"

    file_put_contents(dumped, content)
    return loader.loadShader(dumped, Shader.SLCg)


print "Panda3D Version =",PandaSystem.getVersionString()




class AtmosphericScattering:
    
    def __init__(self):
        pass

    # Prepares a FBO Texture
    def prepBuffTx(self, tx):
        tx.setWrapU(Texture.WMClamp)
        tx.setWrapV(Texture.WMClamp)
        tx.setComponentType(Texture.T_float)
        tx.setFormat(Texture.FRgb16)
        tx.setMinfilter(Texture.FTLinear)
        tx.setMagfilter(Texture.FTLinear)

    # Renders a frame (also updates the buffers)
    def flush(self):
        base.graphicsEngine.renderFrame()
        return True

    # Stop buffer-rendering
    def disableBuffer(self, buf):
        # buf.getDisplayRegion(0).setActive(False)
        buf.setActive(0)
        return True

    # Adds a buffer to the list of buffers which should get removed after the precomputation
    # Also adds the corresponding buffer tex to a list
    def addCleanupBufferTex(self, buf, tex):
        self.buffers_cleanup.append(buf)
        self.textures_cleanup.append(tex)
        return True

    # Marks a texture dirty
    def addCleanupTex(self, tex):
        self.textures_cleanup.append(tex)
        return True

    # Adds a buffer to the list of buffers which should get removed after the precomputation
    def addCleanupBuffer(self, buf):
        self.buffers_cleanup.append(buf)
        return True

    # Returns common shader-header files
    def getCommonFiles(self):
        return [
                self.shader_root_dir + "constants.cg",
                self.shader_root_dir + "common.cg"
        ]

    # The actual precomputing
    def init(self):

        self.flush()

        self.RES_H = 32
        self.buffers_cleanup = []
        self.textures_cleanup = []

        self.shader_root_dir = "scattering/"

        prog_transmittance = create_shader(self.getCommonFiles() + [
                self.shader_root_dir + "transmittance.cg"
            ], False, "transmittance")

        prog_inscatter1 = create_shader(self.getCommonFiles() + [
                self.shader_root_dir + "inscatter1.cg"
            ], True, "inscatter1")

        prog_irradiance1 = create_shader(self.getCommonFiles() + [
                self.shader_root_dir + "irradiance1.cg"
            ], False, "irradiance1") 

        prog_copyIrradiance = create_shader(self.getCommonFiles() + [
                self.shader_root_dir + "copyIrradiance.cg"
            ], False, "copyIrradiance") 

        prog_copyInscatter1 = create_shader(self.getCommonFiles() + [
                self.shader_root_dir + "copyInscatter1.cg"
            ], True, "copyInscatter1") 

        prog_inscatterS = create_shader(self.getCommonFiles() + [
                self.shader_root_dir + "inscatterS.cg"
            ], True, "inscatterS") 

        prog_irradianceN = create_shader(self.getCommonFiles() + [
                self.shader_root_dir + "irradianceN.cg"
            ], False, "irradianceN") 

        prog_inscatterN = create_shader(self.getCommonFiles() + [
                self.shader_root_dir + "inscatterN.cg"
            ], True, "inscatterN") 

        prog_inscatterADD = create_shader(self.getCommonFiles() + [
                self.shader_root_dir + "copyInscatterADD.cg"
            ], True, "copyInscatterADD") 

        # computes transmittance texture T 
        self.tx_T = Texture()
        self.prepBuffTx(self.tx_T)
        quad, buf = self.renderQuadInto(256,64, self.tx_T)
        quad.setShader(prog_transmittance)
        self.flush() and self.disableBuffer(buf) and self.addCleanupBufferTex(buf, self.tx_T)

        base.graphicsEngine.extract_texture_data(self.tx_T, base.win.getGsg())
        self.tx_T.write("buffer_dump/0_transmittance.png")

        # computes irradiance texture deltaE
        self.tx_deltaE = Texture()
        self.prepBuffTx(self.tx_deltaE)
        quad, buf = self.renderQuadInto(64,16, self.tx_deltaE)
        quad.setShader(prog_irradiance1)
        quad.setShaderInput("tx_transmittance", self.tx_T)
        self.flush() and self.disableBuffer(buf) and self.addCleanupBufferTex(buf, self.tx_deltaE)

        base.graphicsEngine.extract_texture_data(self.tx_deltaE, base.win.getGsg())
        self.tx_deltaE.write("buffer_dump/1_deltaE.png")

        # computes single scattering texture deltaS
        # Rayleigh and Mie separated in deltaSR + deltaSM
        self.tx_deltaSR = Texture()
        self.tx_deltaSR.setup2dTextureArray(self.RES_H)

        self.tx_deltaSM = Texture()
        self.tx_deltaSM.setup2dTextureArray(self.RES_H)

        self.prepBuffTx(self.tx_deltaSR)
        self.prepBuffTx(self.tx_deltaSM)
        quad, buf = self.renderQuadInto(256,128, self.tx_deltaSR, GraphicsOutput.RTMBindLayered, self.tx_deltaSM)
        quad.setShader(prog_inscatter1)
        quad.setShaderInput("tx_transmittance", self.tx_T)
        self.flush() and self.disableBuffer(buf) and self.addCleanupBufferTex(buf, self.tx_deltaSR) and self.addCleanupTex(self.tx_deltaSM)

        base.graphicsEngine.extract_texture_data(self.tx_deltaSR, base.win.getGsg())
        self.tx_deltaSR.write("buffer_dump/2.0_deltaSR.png")


        # copies deltaE into irradiance texture E
        self.tx_E = Texture()
        self.prepBuffTx(self.tx_E)
        quad, buf = self.renderQuadInto(64, 16, self.tx_E) 
        quad.setShader(prog_copyIrradiance)
        quad.setShaderInput("k" , 0.0)
        quad.setShaderInput("tx_deltaE", self.tx_deltaE)
        self.flush() and self.disableBuffer(buf) and self.addCleanupBufferTex(buf, self.tx_E)

        # copies deltaS into inscatter texture S
        self.tx_S = Texture()
        self.tx_S.setup2dTextureArray(self.RES_H)
        self.prepBuffTx(self.tx_S)
        quad, buf = self.renderQuadInto(256,128, self.tx_S, GraphicsOutput.RTMBindLayered)
        quad.setShaderInput("tx_deltaSR", self.tx_deltaSR)
        quad.setShaderInput("tx_deltaSM", self.tx_deltaSM)
        quad.setShader(prog_copyInscatter1)
        self.flush() and self.disableBuffer(buf) and self.addCleanupBufferTex(buf, self.tx_S)


        self.tx_E = Texture()
        self.prepBuffTx(self.tx_E)

        self.tx_S = Texture()
        self.tx_S.setup2dTextureArray(self.RES_H)
        self.prepBuffTx(self.tx_S)


        for i in xrange(3):
            order = i + 2  # 2, 3, 4
            first = 1.0 if i == 0.0 else 0.0

            # computes deltaJ
            self.tx_deltaJ = Texture()
            self.tx_deltaJ.setup2dTextureArray(self.RES_H)
            self.prepBuffTx(self.tx_deltaJ)
            quad,buf = self.renderQuadInto(256,128, self.tx_deltaJ, GraphicsOutput.RTMBindLayered)
            quad.setShader(prog_inscatterS)
            quad.setShaderInput("first", first)
            quad.setShaderInput("tx_transmittance", self.tx_T)
            quad.setShaderInput("tx_deltaE", self.tx_deltaE)
            quad.setShaderInput("tx_deltaSR", self.tx_deltaSR)
            quad.setShaderInput("tx_deltaSM", self.tx_deltaSM)
            self.flush() and self.disableBuffer(buf) and self.addCleanupBufferTex(buf, self.tx_deltaJ)

            base.graphicsEngine.extract_texture_data(self.tx_deltaJ, base.win.getGsg())
            self.tx_deltaJ.write("buffer_dump/3_deltaJ_" + str(i) + ".png")
           

            # computes deltaE
            self.tx_deltaE = Texture()
            self.prepBuffTx(self.tx_deltaE)
            quad,buf = self.renderQuadInto(64,16, self.tx_deltaE)
            quad.setShader(prog_irradianceN)
            quad.setShaderInput("first", first)
            quad.setShaderInput("tx_transmittance", self.tx_T)
            quad.setShaderInput("tx_deltaSR", self.tx_deltaSR)
            quad.setShaderInput("tx_deltaSM", self.tx_deltaSM)
            self.flush() and self.disableBuffer(buf) and self.addCleanupBufferTex(buf, self.tx_deltaE)

            base.graphicsEngine.extract_texture_data(self.tx_deltaE, base.win.getGsg())
            self.tx_deltaE.write("buffer_dump/3_deltaE_" + str(i) + ".png")
           
            # computes deltaS
            self.tx_deltaS = Texture()
            self.tx_deltaS.setup2dTextureArray(self.RES_H)
            quad, buf = self.renderQuadInto(256, 128, self.tx_deltaS, GraphicsOutput.RTMBindLayered)
            quad.setShader(prog_inscatterN)
            quad.setShaderInput("first", first)
            quad.setShaderInput("tx_transmittance", self.tx_T)
            quad.setShaderInput("tx_deltaJ", self.tx_deltaJ)
            self.flush() and self.disableBuffer(buf) and self.addCleanupBufferTex(buf, self.tx_deltaS)

            base.graphicsEngine.extract_texture_data(self.tx_deltaS, base.win.getGsg())
            self.tx_deltaS.write("buffer_dump/3_deltaS_" + str(i) + ".png")

            # adds deltaE into irradiance texture E
            tx_E_dst = Texture()
            self.prepBuffTx(tx_E_dst)
            quad,buf = self.renderQuadInto(64, 16, tx_E_dst)
            quad.setShader(loader.loadShader(self.shader_root_dir + "copyIrradianceADD.cg"))
            quad.setShaderInput("tx_add_to", self.tx_E)
            quad.setShaderInput("k" , 1.0)
            quad.setShaderInput("tx_deltaE", self.tx_deltaE)
            self.flush() and self.disableBuffer(buf) and self.addCleanupBuffer(buf)
            self.tx_E = tx_E_dst
            self.addCleanupBufferTex(buf, tx_E_dst)
            

            base.graphicsEngine.extract_texture_data(self.tx_E, base.win.getGsg())
            self.tx_E.write("buffer_dump/3_irradianceE_"+str(i) + ".png")

            # adds deltaS into inscatter texture S 
            tx_S_dst = Texture()
            tx_S_dst.setup2dTextureArray(self.RES_H)
            self.prepBuffTx(tx_S_dst)
            quad,buf = self.renderQuadInto(256, 128, tx_S_dst, GraphicsOutput.RTMBindLayered)
            quad.setShader(prog_inscatterADD)  
            quad.setShaderInput("tx_deltaS", self.tx_deltaS)
            quad.setShaderInput("tx_add_to", self.tx_S)
            self.tx_S = tx_S_dst
            self.flush() and self.disableBuffer(buf) and self.addCleanupBuffer(buf)

            base.graphicsEngine.extract_texture_data(self.tx_S, base.win.getGsg())
            self.tx_S.write("buffer_dump/3_inscatterS_"+str(i) + ".png")


        base.graphicsEngine.extract_texture_data(self.tx_E, base.win.getGsg())
        self.tx_E.write("buffer_dump/4_irradianceE.png")

        base.graphicsEngine.extract_texture_data(self.tx_S, base.win.getGsg())
        self.tx_S.write("buffer_dump/4_inscatterS.png")

        self.flush()

        # for buf_index, buf in enumerate(self.buffers_cleanup):
        #     base.graphicsEngine.removeWindow(buf)



    def renderQuadInto(self, xsize, ysize, colortex=None, cmode = GraphicsOutput.RTMBindOrCopy, auxtex = None):

        buffer = self.createBuffer("filter-stage", xsize, ysize, colortex, cmode, auxtex)

        if (buffer == None):
            return None

        cm = CardMaker("filter-stage-quad")
        cm.setFrameFullscreenQuad()
        quad = NodePath(cm.generate())
        quad.setDepthTest(0)
        quad.setDepthWrite(0)
        quad.setColor(Vec4(1,0.5,0.5,1))

        quadcamnode = Camera("filter-quad-cam")
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setFilmOffset(0, 0)
        lens.setNearFar(-1000, 1000)
        quadcamnode.setLens(lens)
        quadcam = quad.attachNewNode(quadcamnode)
        
        buffer.getDisplayRegion(0).setCamera(quadcam)
        buffer.getDisplayRegion(0).setActive(1)

        return quad, buffer


    def createBuffer(self, name, xsize, ysize, colortex, cmode, auxtex):

        winprops = WindowProperties.size(xsize, ysize)
        props = FrameBufferProperties()
        props.setColorBits(48)
        props.setRgbColor(0)

        if auxtex:
            props.setAuxHrgba(1)

        buffer = base.graphicsEngine.makeOutput(
            base.win.getPipe(), name, 1,
            props, winprops, GraphicsPipe.BFRefuseWindow,
            base.win.getGsg(), base.win)

        if (buffer == None):
            return buffer

        buffer.addRenderTexture(colortex, cmode, GraphicsOutput.RTPColor)

        if auxtex:
            buffer.addRenderTexture(auxtex, cmode, GraphicsOutput.RTPAuxHrgba0)

        buffer.setSort(-1)
        buffer.disableClears()
        buffer.getDisplayRegion(0).disableClears()
        return buffer



class World(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)


base = World()
a = AtmosphericScattering()
a.init()

base.run()
