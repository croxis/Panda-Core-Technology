usageText = """
Usage:

  %(prog)s [opts]

Options:

  -s Run a server
  -c Run a client

  -t Don't run threaded network

  -p [server:][port]
     game server and/or port number to contact

  -l output.log
     optional log filename

If no options are specified, the default is to run a solo client-server."""

import getopt
import sys
from pandac.PandaModules import loadPrcFileData

import os

def usage(code, msg = ''):
    print >> sys.stderr, usageText % {'prog' : os.path.split(sys.argv[0])[1]}
    print >> sys.stderr, msg
    sys.exit(code)

try:
    opts, args = getopt.getopt(sys.argv[1:], 'sacr:tp:l:h')
except getopt.error, msg:
    usage(1, msg)

runServer = False
runClient = False
logFilename = None
threadedNet = False

for opt, arg in opts:
    if opt == '-s':
        runServer = True
    elif opt == '-c':
        runClient = True
    elif opt == '-h':
        usage(0)
    else:
        print 'illegal option: ' + flag
        sys.exit(1)

if logFilename:
    # Set up Panda's notify output to write to the indicated file.
    mstream = MultiplexStream()
    mstream.addFile(logFilename)
    mstream.addStandardOutput()
    Notify.ptr().setOstreamPtr(mstream, False)

    # Also make Python output go to the same place.
    sw = StreamWriter(mstream, False)
    sys.stdout = sw
    sys.stderr = sw

    # Since we're writing to a log file, turn on timestamping.
    loadPrcFileData('', 'notify-timestamp 1')

if not runClient:
    # Don't open a graphics window on the server.  (Open a window only
    # if we're running a normal client, not one of the server
    # processes.)
    loadPrcFileData('', 'window-type none\naudio-library-name null')

if runClient:
    loadPrcFileData( '', 'frame-rate-meter-scale 0.035' )
    loadPrcFileData( '', 'frame-rate-meter-side-margin 0.1' )
    loadPrcFileData( '', 'show-frame-rate-meter 1' )
    #loadPrcFileData( '', 'window-title '+title )
    loadPrcFileData('', "sync-video 0")

#loadPrcFileData('', 'want-pstats 1')
#loadPrcFileData('', 'pstats-max-rate 30')
#loadPrcFileData('', "notify-level-ClientRepository debug")
#loadPrcFileData('', "notify-level-ServerRepository debug")

from direct.directbase.DirectStart import *

    
if runServer:
    from server import SN
    base.server = SN()
    #from ITFServerRepository import ITFServerRepository
    #from ITFAIRepository import ITFAIClientRepository
    #base.server = ITFServerRepository(threadedNet = threadedNet)
    #base.air = ITFAIClientRepository(threadedNet = threadedNet)

if runClient:
    import client
    
if runClient and not runServer:
    base.setSleep(0.001)
if not runClient and runServer:
    base.setSleep(0.001)

run()
 
