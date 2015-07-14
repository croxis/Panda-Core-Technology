from pandac.PandaModules import loadPrcFileData

loadPrcFileData( '', 'frame-rate-meter-scale 0.035' )
loadPrcFileData( '', 'frame-rate-meter-side-margin 0.1' )
loadPrcFileData( '', 'show-frame-rate-meter 1' )
loadPrcFileData( '', 'window-title Atmosphere Demo' )
loadPrcFileData('', "sync-video 0")

loadPrcFileData("", "basic-shaders-only #f")


from direct.directbase.DirectStart import *

from panda3d.core import Point3
from direct.showbase.DirectObject import DirectObject 

render.setShaderAuto()
base.setBackgroundColor(0.0, 0.0, 0.0) 
#base.disableMouse()

# Store celestial bodies here
# Later we will iterate through this list and adjust the scale of each body one by one.
# Although now we are using bodies as nodes themselves this may become redundant.
base.bodies = []
import celestialBodies

sun = celestialBodies.Star('sun', { 
            "spectral": "G2V", 
            "texture": "sun_1k_tex.jpg", })
#sun.mesh.setPos(1050,0,0)
sun.mesh.setScale(5)
sun.mesh.setPos(1050,0,0)
base.bodies.append(sun)

earth = celestialBodies.Body('earth', {
                    "texture": "earth_#.png", 
                    "normal": "Earth_NormalMap_2.jpg",
                    "spec": "earth_spec.png",
                    "height": "srtm_ramp2.world.5400x2700.jpg",
                    "glow": "earth_glow.png"}, isAtmo=True)    
#moon = celestialBodies.Body(name, DB, parentNode) 


base.bodies.append(earth)


run()
