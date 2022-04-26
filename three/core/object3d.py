from warnings import warn
import uuid
from . import EventDispatcher
from ..structure import Dict
from ..math import Vector3, Matrix4, Quaternion, Matrix3, Euler
from .id_provider import IdProvider
from .layers import Layers
from typing import List

id_provider = IdProvider()

#_m1 = Matrix4()
# TODO 重写

_v1 = Vector3()
_q1 = Quaternion()
_m1 = Matrix4()
_target = Vector3()

_position = Vector3()
_scale = Vector3()
_quaternion = Quaternion()

_xAxis = Vector3( 1, 0, 0 )
_yAxis = Vector3( 0, 1, 0 )
_zAxis = Vector3( 0, 0, 1 )

_addedEvent = { type: 'added' }
_removedEvent = { type: 'removed' }

class Object3D(EventDispatcher):
    DefaultUp = Vector3( 0, 1, 0 )
    _v = Vector3()
    _m = Matrix4()
    _q = Quaternion()

    def __init__(self, name = ''):
        super().__init__()

        self._uuid = uuid.uuid1()
        self.visible = True
        self._name = name
        self._type = "Object3D"
        
        # Init parent and children
        self._parent: Object3D = None
        self._children: List[Object3D] = []

        self.up = Object3D.DefaultUp.clone()

        self.position = Vector3()
        self.rotation = Euler()
        self.quaternion = Quaternion()
        self.scale = Vector3(1, 1, 1)

        def onRotationChange():
            self.quaternion.setFromEuler( self.rotation, False )

        def onQuaternionChange():
            self.rotation.setFromQuaternion( self.quaternion, None, False )

        self.rotation._onChange( onRotationChange )
        self.quaternion._onChange( onQuaternionChange )

        self._transformHash = ()

        self.modelViewMatrix = Matrix4()
        self.normalMatrix = Matrix3()

        self._matrix = Matrix4()
        self.matrixWorld = Matrix4()
        self.matrixAutoUpdate = True
        self.matrixWorldNeedsUpdate = False

        self.castShadow = False
        self.receiveShadow = False

        self.frustumCulled = True
        self.renderOrder = 0

        self.animations = []

        self.userData = Dict({})

        self._id = id_provider.claim_id(self)

        self.layers = Layers()


    def __del__(self):
        id_provider.release_id(self, self.id)
        

    @property
    def id(self):
        return self._id

    @property
    def uuid(self):
        return str(self._uuid)
    
    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def parent(self):
        """Object's parent in the scene graph (read-only).
        An object can have at most one parent.
        """
        return self._parent

    @property
    def children(self):
        """The child objects of self wold object (read-only tuple).
        Use ``.add()`` and ``.remove()`` to change self list.
        """
        return tuple(self._children)

    @property
    def matrix(self):
        """The (settable) transformation matrix."""
        return self._matrix

    @matrix.setter
    def matrix(self, matrix):
        self._matrix.copy(matrix)
        self._matrix.decompose(self.position, self.rotation, self.scale)
        self.matrixWorldNeedsUpdate = True

    def onBeforeRender(self, *args):
        pass

    def onAfterRender(self, *args):
        pass

    def applyMatrix4( self, matrix:' Matrix4' ):
        if self.matrixAutoUpdate:
            self.updateMatrix()

        self.matrix.premultiply( matrix )
        self.matrix.decompose( self.position, self.quaternion, self.scale )

    def applyQuaternion( self, q:' Quaternion' ):
        self.quaternion.premultiply( q )
        return self

    def setRotationFromAxisAngle( self, axis, angle ):
        # assumes axis is normalized
        self.quaternion.setFromAxisAngle( axis, angle )

    def setRotationFromEuler( self, euler:'Euler' ):
        self.quaternion.setFromEuler( euler, True )

    def setRotationFromMatrix( self, m:'Matrix4' ):
        # assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)
        self.quaternion.setFromRotationMatrix( m )

    def setRotationFromQuaternion( self, q ):
        # assumes q is normalized
        self.quaternion.copy( q )

    def rotateOnAxis( self, axis, angle ):
        # rotate object on axis in object space
        # axis is assumed to be normalized
        _q1.setFromAxisAngle( axis, angle )
        self.quaternion.multiply( _q1 )
        return self

    def rotateOnWorldAxis( self, axis, angle ):
        # rotate object on axis in world space
        # axis is assumed to be normalized
        # method assumes no rotated parent
        _q1.setFromAxisAngle( axis, angle )
        self.quaternion.premultiply( _q1 )
        return self

    def rotateX( self, angle ):
        return self.rotateOnAxis( _xAxis, angle )

    def rotateY( self, angle ):
        return self.rotateOnAxis( _yAxis, angle )

    def rotateZ( self, angle ):
        return self.rotateOnAxis( _zAxis, angle )

    def translateOnAxis( self, axis, distance ):
        # translate object by distance along axis in object space
        # axis is assumed to be normalized
        _v1.copy( axis ).applyQuaternion( self.quaternion )
        self.position.add( _v1.multiplyScalar( distance ) )
        return self

    def translateX(self, distance ):
        return self.translateOnAxis( _xAxis, distance )

    def translateY( self, distance ):
        return self.translateOnAxis( _yAxis, distance )

    def translateZ( self, distance ):
        return self.translateOnAxis( _zAxis, distance )

    def localToWorld( self, vector: 'Vector3' ):
        return vector.applyMatrix4( self.matrixWorld )

    def worldToLocal( self, vector: 'Vector3' ):
        return vector.applyMatrix4( _m1.copy( self.matrixWorld ).invert() )

    def lookAt( self, x, y=None, z=None ):
        # This method does not support objects having non-uniformly-scaled parent(s)
        if x.isVector3:
            _target.copy( x )
        else:
            _target.set( x, y, z )

        parent = self.parent

        self.updateWorldMatrix( True, False )

        _position.setFromMatrixPosition( self.matrixWorld )

        if self.isCamera or self.isLight:
            _m1.lookAt( _position, _target, self.up )
        else:
            _m1.lookAt( _target, _position, self.up )


        self.quaternion.setFromRotationMatrix( _m1 )

        if parent:
            _m1.extractRotation( parent.matrixWorld )
            _q1.setFromRotationMatrix( _m1 )
            self.quaternion.premultiply( _q1.invert() )


    
    def add(self, *objects:'Object3D'):
        """Adds object as child of self object. Any number of
        objects may be added. Any other current parent on an object passed
        in here will be removed, since an object can have at most one
        parent.
        """
        for obj in objects:
            if obj == self:
                warn ( f'THREE.Object3D.add: object can\'t be added as a child of itself. {object}')
                continue
            
            if obj and obj.isObject3D:
                if obj._parent is not None:
                    obj._parent.remove(obj)

                obj._parent = self
                self._children.append(obj)
                obj.dispatchEvent( _addedEvent )
            
            else:
                warn( f'THREE.Object3D.add: object not an instance of THREE.Object3D. [object]' )

        return self

    def remove(self, *objects:'Object3D'):
        """Removes object as child of self object. Any number of objects may be removed.
        If a given object is not a child, it is ignored.
        """
        for obj in objects:

            try:
                self._children.remove(obj)
                obj._parent = None

                obj.dispatchEvent( _removedEvent )
            except ValueError:
                pass
        return self

    def removeFromParent(self):
        parent = self.parent

        if parent != None: 
            parent.remove( self )
        return self

    def clear(self):
        for obj in self.children:
            obj.parent = None
            obj.dispatchEvent( _removedEvent )

        self._children.clear()
        return self

    def attach( self, object:'Object3D' ):

		# adds object as a child of self, while maintaining the object's world transform

		# Note: This method does not support scene graphs having non-uniformly-scaled nodes(s)

        self.updateWorldMatrix( True, False )
        _m1.copy( self.matrixWorld ).invert()

        if object._parent:
            object._parent.updateWorldMatrix( True, False )
            _m1.multiply( object.parent.matrixWorld )

        object.applyMatrix4( _m1 )
        self.add( object )
        object.updateWorldMatrix( False, True )
        return self

    def getObjectById( self, id ):
        return self.getObjectByProperty( 'id', id )

    def getObjectByName( self, name ):
        return self.getObjectByProperty( 'name', name )

    def getObjectByProperty( self, name, value ):
        if getattr(self, name) == value:
            return self
        
        for child in self._children:
            object = child.getObjectByProperty( name, value )

            if object:
                return object

        return None

    def getWorldPosition( self, target:'Vector3' ):
        self.updateWorldMatrix( True, False )
        return target.setFromMatrixPosition( self.matrixWorld )

    def getWorldQuaternion( self, target:'Quaternion' ):
        self.updateWorldMatrix( True, False )
        self.matrixWorld.decompose( _position, target, _scale )
        return target

    def getWorldScale( self, target:'Vector3' ):
        self.updateWorldMatrix( True, False )
        self.matrixWorld.decompose( _position, _quaternion, target )
        return target

    def getWorldDirection(self, target:'Vector3' ):
        self.updateWorldMatrix( True, False )
        e = self.matrixWorld.elements
        return target.set( e[ 8 ], e[ 9 ], e[ 10 ] ).normalize()

    def raycast( self, raycaster, intersects ):
        warn(f'{self.__class__.name}.raycast() has not been implemented yet.')

    def traverse(self, callback, skip_invisible=False):
        """Executes the callback on self object and all descendants.
        """
        if skip_invisible and not self.visible:
            return
        callback(self)
        for child in self._children:
            child.traverse(callback, skip_invisible)

    def traverseVisible(self, callback ):
        self.traverse(callback, True)

    def traverseAncestors( self, callback ):
        parent = self.parent
        if parent:
            callback( parent )
            parent.traverseAncestors( callback )

    def updateMatrix(self):
        self._matrix.compose( self.position, self.quaternion, self.scale )
        self.matrixWorldNeedsUpdate = True

    def updateMatrixWorld( self, force= False ):
        if self.matrixAutoUpdate:
            self.updateMatrix()

        if self.matrixWorldNeedsUpdate or force:
            if self._parent is None:
                self.matrixWorld.copy( self.matrix )
            else:
                self.matrixWorld.multiplyMatrices( self._parent.matrixWorld, self.matrix )

            self.matrixWorldNeedsUpdate = False
            force = True

        # update children
        for child in self._children:
            child.updateMatrixWorld( force )

    def updateWorldMatrix( self, updateParents, updateChildren ):

        parent = self._parent

        if updateParents and parent:
            parent.updateWorldMatrix( True, False )

        if self.matrixAutoUpdate:
            self.updateMatrix()

        if self.parent is None:
            self.matrixWorld.copy( self._matrix )
        else:
            self.matrixWorld.multiplyMatrices( self.parent.matrixWorld, self._matrix )

        # update children

        if updateChildren:
            children = self.children
            for child in children:
                child.updateWorldMatrix( False, True )

    
    def copy( self, source:'Object3D', recursive = True ):

        self.name = source.name

        self.up.copy( source.up )

        self.position.copy( source.position )
        self.rotation.order = source.rotation.order
        self.quaternion.copy( source.quaternion )
        self.scale.copy( source.scale )

        self.matrix.copy( source.matrix )
        self.matrixWorld.copy( source.matrixWorld )

        self.matrixAutoUpdate = source.matrixAutoUpdate
        self.matrixWorldNeedsUpdate = source.matrixWorldNeedsUpdate

        self.layers.mask = source.layers.mask
        self.visible = source.visible

        self.castShadow = source.castShadow
        self.receiveShadow = source.receiveShadow

        self.frustumCulled = source.frustumCulled
        self.renderOrder = source.renderOrder

        self.userData = source.userData.copy()

        if recursive:
            for child in source.children:
                self.add( child.clone() )

        return self

    def clone( self, recursive ):
        self.__class__().copy( self, recursive )

