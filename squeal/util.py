import array
import struct
import socket
import fcntl
import simplejson
from squeal.isqueal import *

def all_interfaces():
    max_possible = 128  # arbitrary. raise if needed.
    bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', '\0' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(),
        0x8912,  # SIOCGIFCONF
        struct.pack('iL', bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tostring()
    return [namestr[i:i+32].split('\0', 1)[0] for i in range(0, outbytes, 32)]

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def guess_ip():
    candidates = filter(lambda x: not x.startswith("127."), map(get_ip_address, all_interfaces()))
    if candidates:
        return candidates[0]

class AdaptiveJSONEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        a = IJSON(obj, None)
        if a is not None:
            return a.json()
        return simplejson.JSONEncoder.default(self, obj)

def dumps(ob):
    return simplejson.dumps(ob, cls=AdaptiveJSONEncoder)
