#!/bin/sh
cd ~/src/SandBox/
sudo python2 setup.py install
cd ~/src/SpaceDrive/
sudo python2 setup.py install
cd ~/src/Panda-Core-Technology/
panda3d ppackage.p3d -i build make.pdef
#scp -rp build/* croxis@croxis.net:/home/croxis/www/p3d
