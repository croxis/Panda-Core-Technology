//Abstract class that represents a connection to another computer

//TODO: Packet ordering
//Acks
//RTT
//Packet throttling

//We have 464 bits for UDP
//398 bits after our protocol headers

class Connection(object):
    def __init__(self, ip, port, idhash=0):
        self.ip = id
        self.port = port
        self.idhash = idhash
        self.localpacketcount = 0
        self.remotepacketcount = 0
        self.receivedPackets = []
        self.goodrtt = True
        
    def buildDatagram(protocol):
        datagram = PyDatagram()
        datagram.addUint8(protocol)
        datagram.addUint8(self.packetcount)
        datagram.addUint8(self.packetcount)//ack
        datagram.addUint16(self.packetcount)//ack32
        datagram.addUint16(self.idhash)
        self.packetcount += 1
        if self.packetcount > 255:
            self.packetcount = 0
        return datagram
    
    def sequenceMoreRecent(s1, s2, maxSequence):
        //Used to determine if wrap around sequence is part of the next packetcount, ie 254, 255, 0, 1
        //returns bool
        return (s1 > s2) and (s1 - s2 <= maxSequence/2) || (s2 > s1) and (s2-s1 > maxSequence/2)
    
        
class ServerConnection(Connection):
    //Representation of a server on the client
    def login(username, hashpassword):
        datagram = self.buildDatagram(100)
        datagram.addString(username)
        datagram.addString(hashpassword)
        return datagram