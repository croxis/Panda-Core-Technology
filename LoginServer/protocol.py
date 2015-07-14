#Client to server even
#Server to client odd
#If both will probably be even

# Packet structure
# msgID = myIterator.getUint8()
# remotePacketCount = myIterator.getUint8()
# ack = myIterator.getUint8()
# acks = myIterator.getUint16()
# hashID = myIterator.getUint16()

#Protocol space
#0-99 common game elements
#100-199 login and server handshaking and admin stuff

LOGIN = 100
LOGIN_DENIED = 101
LOGIN_ACCEPT = 103

CHAT = 104
