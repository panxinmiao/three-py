from ..structure import NoneAttribute
import math

class Cylindrical(NoneAttribute):
    def __init__(self, radius: float = 1.0, theta: float = 0.0, y: float = 0.0) -> None:
        self.radius = radius
        self.theta = theta
        self.y = y

    def set( self, radius, theta, y ):
        self.radius = radius
        self.theta = theta
        self.y = y
        return self


    def copy( self, other:'Cylindrical' ):
        self.radius = other.radius
        self.theta = other.theta
        self.y = other.y
        return self

    def setFromVector3( self, v ):
        return self.setFromCartesianCoords( v.x, v.y, v.z )

    def setFromCartesianCoords( self, x, y, z ):

        self.radius = math.sqrt( x * x + z * z )
        self.theta = math.atan2( x, z )
        self.y = y

        return self

    def clone(self):
        Cylindrical().copy( self )