# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from panda3d.core import loadPrcFileData

from direct.showbase.ShowBase import ShowBase


base = ShowBase()
base.setSleep(0.001)


import random

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.fmtfuncs import red, bold, green, on_blue, yellow
r = 0

print(yellow('the following code takes over the screen'))
with FullscreenWindow() as window:
    print(red(on_blue(bold('Press escape to exit'))))
    with Input() as input_generator:
        a = FSArray(window.height, window.width)
        a[r, 0] = [repr("Test " + str(r))]
        window.render_to_terminal(a)
        r += 1
        for c in input_generator:
            if c == '<ESC>':
                break
            elif c == '<SPACE>':
                a = FSArray(window.height, window.width)
            else:
                row = random.choice(range(window.height))
                column = random.choice(range(window.width-len(repr(c))))
                color = random.choice([red, green, on_blue, yellow])
                a[row, column:column+len(repr(c))] = [color(repr(c))]
            window.render_to_terminal(a)
        a = FSArray(window.height, window.width)
        
print(r)

#base.run()