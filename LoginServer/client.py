from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader, ConnectionWriter, PointerToConnection, NetAddress, NetDatagram
from direct.distributed.PyDatagram import PyDatagram

import protocol

port_address=9099  # same for client and server
ip_address="127.0.0.1"

packetCount = 0
 
cManager = QueuedConnectionManager()
cReader = QueuedConnectionReader(cManager, 0)
cWriter = ConnectionWriter(cManager,0)
 
myConnection=cManager.openUDPConnection()
   
myPyDatagram = PyDatagram()
myPyDatagram.addUint8(protocol.LOGIN)
myPyDatagram.addUint8(packetCount)
myPyDatagram.addUint8(0)
myPyDatagram.addUint16(0)
myPyDatagram.addUint16(0)
myPyDatagram.addString("HUser name")
myPyDatagram.addString("Hashed password")

serverAddress = NetAddress()
serverAddress.setHost(ip_address, port_address)

cWriter.send(myPyDatagram, myConnection, serverAddress) 
print "Sending packet"

