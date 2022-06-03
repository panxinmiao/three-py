import math, random

MACHINE_EPSILON = (
    7.0 / 3 - 4.0 / 3 - 1
)  # the difference between 1 and the smallest floating point number greater than 1

DEG2RAD = math.pi / 180
RAD2DEG = 180 / math.pi

def clamp(x: float, left: float, right: float) -> float:
    return max(left, min(right, x))


def euclideanModulo( n, m ):
    return ( ( n % m ) + m ) % m

# Linear mapping from range <a1, a2> to range <b1, b2>
def mapLinear( x, a1, a2, b1, b2 ):
    return b1 + ( x - a1 ) * ( b2 - b1 ) / ( a2 - a1 )

def inverseLerp( x, y, value ):
    if ( x != y ):
        return ( value - x ) / ( y - x )
    else:
        return 0

# https://en.wikipedia.org/wiki/Linear_interpolation

def lerp( x, y, t ):
    return ( 1 - t ) * x + t * y

# http://www.rorydriscoll.com/2016/03/07/frame-rate-independent-damping-using-lerp/
def damp( x, y, lam, dt ):
    return lerp( x, y, 1 - math.exp( - lam * dt ) )


# https://www.desmos.com/calculator/vcsjnyz7x4
def pingpong( x, length = 1 ):
    return length - abs( euclideanModulo( x, length * 2 ) - length )

# http://en.wikipedia.org/wiki/Smoothstep
def smoothstep( x, min, max ):
    if x <= min:
        return 0
    if x >= max:
        return 1
    x = ( x - min ) / ( max - min )
    return x * x * ( 3 - 2 * x )

def smootherstep( x, min, max ):
    if x <= min:
        return 0
    if x >= max:
        return 1

    x = ( x - min ) / ( max - min )
    return x * x * x * ( x * ( x * 6 - 15 ) + 10 )


# Random integer from <low, high> interval
def randInt( low, high ):
    return low + math.floor( random.random() * ( high - low + 1 ) )

# Random float from <low, high> interval
def randFloat( low, high ):
    return low + random.random() * ( high - low )


# Random float from <-range/2, range/2> interval
def  randFloatSpread( range ):
    return range * ( 0.5 - random.random() )

# Deterministic pseudo-random float in the interval [ 0, 1 ]
# def seededRandom( s ):
#     pass

def degToRad( degrees ):
    return degrees * DEG2RAD

def radToDeg( radians ):
    return radians * RAD2DEG

def isPowerOfTwo( value ):
    return ( value & ( value - 1 ) ) == 0 and value != 0

def ceilPowerOfTwo( value ):
    return math.pow( 2, math.ceil( math.log( value ) / math.log(2) ) )

def floorPowerOfTwo( value ):
    return math.pow( 2, math.floor( math.log( value ) / math.log(2) ) )
