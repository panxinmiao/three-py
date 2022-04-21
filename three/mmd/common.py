# coding: utf-8
"""
common utilities.
"""
import math
import struct
import io
from three import Vector2, Vector3, Vector4, Quaternion


"""
utilities
"""
def radian_to_degree(x):
    """darian to deglee"""

    return x/math.pi * 180.0


class ParseException(Exception):
    """
    Exception in reader
    """
    def __init__(self, message):
        self.message=message


def readall(path):
    """read all bytes from path
    """
    with open(path, "rb") as f:
        return f.read()


class BinaryReader(object):
    """general BinaryReader
    """
    def __init__(self, ios):
        current=ios.tell()
        #ios.seek(0, io.SEEK_END)
        ios.seek(0, 2)
        self.end=ios.tell()
        ios.seek(current)
        self.ios=ios

    def __str__(self):
        return "<BinaryReader %d/%d>" % (self.ios.tell(), self.end)

    def is_end(self):
        #print(self.ios.tell(), self.end)
        return self.ios.tell()>=self.end
        #return not self.ios.readable()

    def unpack(self, fmt, size):
        result=struct.unpack(fmt, self.ios.read(size))
        return result[0]

    def read_int(self, size):
        if size==1:
            return self.unpack("b", size)
        if size==2:
            return self.unpack("h", size)
        if size==4:
            return self.unpack("i", size)
        print("not reach here")
        raise ParseException("invalid int size: "+size)

    def read_uint(self, size):
        if size==1:
            return self.unpack("B", size)
        if size==2:
            return self.unpack("H", size)
        if size==4:
            return self.unpack("I", size)
        print("not reach here")
        raise ParseException("invalid int size: "+size)

    def read_float(self):
        return self.unpack("f", 4)

    def read_vector2(self):
        return Vector2(
            self.read_float(), 
            self.read_float()
        )

    def read_vector3(self):
        return Vector3(
            self.read_float(), 
            self.read_float(), 
            self.read_float()
        )

    def read_vector4(self):
        return Vector4(
            self.read_float(), 
            self.read_float(), 
            self.read_float(),
            self.read_float()
        )

    def read_quaternion(self):
        return Quaternion(
            self.read_float(), 
            self.read_float(), 
            self.read_float(),
            self.read_float()
        )

    def read_quaternion(self):
        return Quaternion(
            self.read_float(), 
            self.read_float(), 
            self.read_float(),
            self.read_float()
        )

    #TODO RGBA Class
    def read_rgba(self):
        return Vector4(
            self.read_float(), 
            self.read_float(), 
            self.read_float(),
            self.read_float()
        )

    #TODO RGBA Class
    def read_rgb(self):
        return Vector3(
            self.read_float(), 
            self.read_float(), 
            self.read_float()
        )


class WriteException(Exception):
    """
    Exception in writer
    """
    pass


class BinaryWriter(object):
    def __init__(self, ios):
        self.ios=ios

    def write_bytes(self, v, size=None):
        if size:
            self.ios.write(struct.pack("={0}s".format(size), v))
        else:
            self.ios.write(v)

    def write_float(self, v):
        self.ios.write(struct.pack("f", v))

    def write_int(self, v, size):
        if size==1:
            self.ios.write(struct.pack("b", v))
        elif size==2:
            self.ios.write(struct.pack("h", v))
        elif size==4:
            self.ios.write(struct.pack("i", v))
        else:
            raise io.WriteError("invalid int uint size")

    def write_uint(self, v, size):
        if v==-1:
            if size==1:
                self.ios.write(struct.pack("B", 255))
            elif size==2:
                self.ios.write(struct.pack("H", 65535))
            elif size==4:
                self.ios.write(struct.pack("I", 4294967295))
            else:
                raise io.WriteError("invalid int uint size")
        else:
            if size==1:
                self.ios.write(struct.pack("B", v))
            elif size==2:
                self.ios.write(struct.pack("H", v))
            elif size==4:
                self.ios.write(struct.pack("I", v))
            else:
                raise io.WriteError("invalid int uint size")

    def write_vector2(self, v):
        self.ios.write(struct.pack("=2f", v.x, v.y))

    def write_vector3(self, v):
        self.ios.write(struct.pack("=3f", v.x, v.y, v.z))

    def write_rgb(self, v):
        self.ios.write(struct.pack("=3f", v.r, v.g, v.b))

    def write_rgba(self, v):
        self.ios.write(struct.pack("=4f", v.r, v.g, v.b, v.a))


class DifferenceException(Exception):
    def __init__(self, message):
        self.message=message


class Diff(object):
    def _diff(self, rhs, key):
        l=getattr(self, key)
        r=getattr(rhs, key)
        if l!=r:
            raise DifferenceException("{lhs}.{key}:{lvalue} != {rhs}.{key}:{rvalue}".format(
                key=key, lhs=self, rhs=rhs, lvalue=l, rvalue=r))

    def _diff_array(self, rhs, key):
        la=getattr(self, key)
        ra=getattr(rhs, key)
        if len(la)!=len(ra):
            raise DifferenceException("%s diffrence %d with %d" % (key, len(la), len(ra)))
        for i, (l, r) in enumerate(zip(la, ra)):
            if isinstance(l, Diff):
                try:
                    l.diff(r)
                except DifferenceException as e:
                    raise DifferenceException(
                            "{lhs}.{key}[{i}] with {rhs}.{key}[{i}]: {message}".format(
                                lhs=self, rhs=rhs, key=key, i=i, message=e.message))
            else:
                if l!=r:
                    raise DifferenceException("{lhs}.{key}[{i}] != {rhs}.{key}[{i}]".format(
                        lhs=self, rhs=rhs, key=key, i=i))

    def __ne__(self, rhs):
        return not self.__eq__(rhs)


class TextReader(object):
    """ base class for text format
    """
    __slots__=[
            "eof", "ios", "lines",
            ]
    def __init__(self, ios):
        self.ios=ios
        self.eof=False
        self.lines=0

    def getline(self):
        line=self.ios.readline()
        self.lines+=1
        if not line:
            self.eof=True
            return None
        return line.strip()

    def printError(self, method, msg):
        print("%s:%s:%d" % (method, msg, self.lines))