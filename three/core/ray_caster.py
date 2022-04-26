from ..structure import NoneAttribute, Dict
from ..math.ray import Ray
from .layers import Layers

import math, three

class Raycaster(NoneAttribute):

    def __init__(self, origin, direction, near = 0, far = math.inf) -> None:
        super().__init__()

        self.ray = Ray(origin, direction)

        # direction is assumed to be normalized (for accurate distance calculations)

        self.near = near
        self.far = far
        self.camera = None
        self.layers = Layers()

        self.params = Dict({
            'Mesh': {},
            'Line': { 'threshold': 1 },
            'LOD': {},
            'Points': { 'threshold': 1 },
            'Sprite': {}
        })

    def set(self, origin, direction):
        
        # direction is assumed to be normalized (for accurate distance calculations)

        self.ray.set( origin, direction )

    def setFromCamera( self, coords, camera:'three.Camera' ):

        if camera.isPerspectiveCamera:

            self.ray.origin.setFromMatrixPosition( camera.matrixWorld )
            self.ray.direction.set( coords.x, coords.y, 0.5 ).unproject( camera ).sub( self.ray.origin ).normalize()
            self.camera = camera

        elif camera.isOrthographicCamera:

            self.ray.origin.set( coords.x, coords.y, ( camera.near + camera.far ) / ( camera.near - camera.far ) ).unproject( camera ) # set origin in plane of camera
            self.ray.direction.set( 0, 0, - 1 ).transformDirection( camera.matrixWorld )
            self.camera = camera

        else:
            raise( 'THREE.Raycaster: Unsupported camera type: ' + camera.type )

    def intersectObject( self, object, recursive = True, intersects = None ):

        intersects = intersects or []

        _intersectObject( object, self, intersects, recursive )

        intersects.sort( 'distance' )

        return intersects


    def intersectObjects( self, objects, recursive = True, intersects = None ):

        intersects = intersects or []

        for object in objects:
            _intersectObject( object, self, intersects, recursive )


        intersects.sort( 'distance' )

        return intersects


def _intersectObject( object:'three.Object3D', raycaster:'Raycaster', intersects, recursive = True ):
    if object.layers.test( raycaster.layers ):
        object.raycast( raycaster, intersects )

    if recursive:
        children = object.children
        for child in children:
            _intersectObject( child, raycaster, intersects, True )

