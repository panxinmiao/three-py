from ....math.vector3 import Vector3

_vector3 = Vector3()

def getDirectionVector( light, camera, directionVector:Vector3 ):

    directionVector.setFromMatrixPosition( light.matrixWorld )
    _vector3.setFromMatrixPosition( light.target.matrixWorld )
    directionVector.sub( _vector3 )
    directionVector.transformDirection( camera.matrixWorldInverse )