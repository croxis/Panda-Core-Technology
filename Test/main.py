from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from direct.directnotify.DirectNotify import DirectNotify

from panda3d.core import CardMaker, PNMImage, Texture, TransparencyAttrib
from panda3d.core import loadPrcFile, loadPrcFileData
from direct.showbase.ShowBase import ShowBase

loadPrcFileData('', 'frame-rate-meter-scale 0.035')
loadPrcFileData('', 'frame-rate-meter-side-margin 0.1')
loadPrcFileData('', 'show-frame-rate-meter 1')
loadPrcFileData('', 'window-title Panda3d bug test')
loadPrcFileData('', "sync-video 0")
loadPrcFileData('', 'task-timer-verbose 1')
loadPrcFileData('', 'pstats-tasks 1')
loadPrcFileData('', 'want-pstats 1')
loadPrcFileData("", "textures-power-2 none")

base = ShowBase()
cardMaker = CardMaker("browser2d")
cardMaker.setFrameFullscreenQuad()
node = cardMaker.generate()
node_path = sandbox.base.render2d.attachNewNode(node)
node_path.setTransparency(TransparencyAttrib.MAlpha)

base.run()