from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader, ConnectionWriter, PointerToConnection, NetAddress, NetDatagram
from direct.distributed import PyDatagramIterator

import protocol

#TODO: An account manager service is needed
#This will be needed to link user name and password to in game assets
userDatabase = {}
newAccounts = True

serverPacketCount = {} # {ip: number}

class SN:
    def __init__(self):
        self.cManager = QueuedConnectionManager()
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.port_address = 9099  # No-other TCP/IP services are using this port
        self.udpSocket = self.cManager.openUDPConnection(self.port_address)
        self.cReader.addConnection(self.udpSocket)
        

        taskMgr.add(self.tskReaderPolling,"Poll the connection reader", -40)



    def tskReaderPolling(self, taskdata):
        if self.cReader.dataAvailable():
            datagram=NetDatagram()  # catch the incoming data in this instance
            # Check the return value; if we were threaded, someone else could have
            # snagged this data before we did
            if self.cReader.getData(datagram):
                myIterator = PyDatagramIterator.PyDatagramIterator(datagram)
                msgID = myIterator.getUint8()

                #If not in our protocol range then we just reject
                if msgID < 0 or msgID > 200:
                    return taskdata.cont

                #Order of these will need to be optimized later
                #We now pull out the rest of our headers
                remotePacketCount = myIterator.getUint8()
                ack = myIterator.getUint8()
                acks = myIterator.getUint16()
                hashID = myIterator.getUint16()
                sourceOfMessage = datagram.getConnection()

                if msgID == protocol.LOGIN:
                    userName = myIterator.getString()
                    password = myIterator.getString()
                    print userName,  password



        return taskdata.cont
