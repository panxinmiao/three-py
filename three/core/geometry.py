import uuid
import three, math
from warnings import warn
from .event_dispatcher import EventDispatcher
from ..math import Matrix4, Quaternion, Vector3, Matrix3, Box3, Sphere, Vector2
from .object3d import Object3D
from ..structure import Dict, Float32Array
from .buffer_attribute import BufferAttribute, Uint32BufferAttribute, Uint16BufferAttribute, Float32BufferAttribute

def arrayNeedsUint32( array ):

	# assumes larger values usually on last
    
    i = len(array)-1

    while i >=0:
        if array[i] > 65535:
            return True
        
        i=i-1

    return False


_m1 = Matrix4()
_obj = Object3D()
_offset = Vector3()
_box = Box3()
_boxMorphTargets = Box3()
_vector = Vector3()

class Geometry(EventDispatcher):
    def __init__(self) -> None:
        self.uuid = uuid.uuid1()

        self.name = ''
        self._type = 'Geometry'

        self.index = None
        self.attributes = Dict({})

        self.morphAttributes = Dict({})
        self.morphTargetsRelative = False

        self.groups = []

        self.boundingBox = None
        self.boundingSphere = None

        self.drawRange = Dict({ 'start': 0, 'count': float('inf') })

        self.userData = Dict({})

    @property
    def isBufferGeometry(self):
        return True

    def getIndex(self):
        return self.index

    def setIndex( self, index ) -> 'Geometry':

        if type(index) == list:
            self.index = (Uint32BufferAttribute if arrayNeedsUint32( index ) else Uint16BufferAttribute)(index, 1)
        else:
            self.index = index
        return self

    def getAttribute( self, name ):
        return self.attributes[name]
    
    def setAttribute( self, name, attribute ) -> 'Geometry':
        self.attributes[ name ] = attribute
        return self

    def deleteAttribute(self, name ) -> 'Geometry':
        del self.attributes[ name ]
        return self

    def hasAttribute( self, name ):
        return name in self.attributes

    def addGroup( self, start, count, material_index = 0):
        self.groups.append(Dict({
            'start': start,
            'count': count,
            'materialIndex': material_index
        }))
    
    def clearGroups( self ):
        self.groups.clear()

    def setDrawRange( self, start, count ):
        self.drawRange['start'] = start
        self.drawRange['count'] = count

    
    # @TODO Geometry工具方法

    def applyMatrix4(self, matrix: Matrix4) -> 'Geometry':
        position = self.attributes.position

        if position is None:
            position.applyMatrix4( matrix )
            position.needsUpdate = True

        normal = self.attributes.normal

        if normal is not None:
            normalMatrix = Matrix3().getNormalMatrix( matrix )

            normal.applyNormalMatrix( normalMatrix )

            normal.needsUpdate = True

        tangent = self.attributes.tangent

        if tangent is not None:
            tangent.transformDirection( matrix )
            tangent.needsUpdate = True

        if self.boundingBox is not None:
            self.computeBoundingBox()

        if self.boundingSphere is not None:
            self.computeBoundingSphere()

        return self

    def applyQuaternion(self, q: Quaternion) -> 'Geometry':
        _m1.makeRotationFromQuaternion( q )
        self.applyMatrix4( _m1 )
        return self

    def rotateX(self, angle) -> 'Geometry':
        _m1.makeRotationX( angle )
        self.applyMatrix4( _m1 )
        return self

    def rotateY(self, angle) -> 'Geometry':
        _m1.makeRotationY( angle )
        self.applyMatrix4( _m1 )
        return self

    def rotateZ(self, angle) -> 'Geometry':
        _m1.makeRotationZ( angle )
        self.applyMatrix4( _m1 )
        return self

    def translate( self, x, y, z ) -> 'Geometry':
        _m1.makeTranslation( x, y, z )
        self.applyMatrix4( _m1 )
        return self

    def scale( self, x, y, z ) -> 'Geometry':
        _m1.makeScale( x, y, z )
        self.applyMatrix4( _m1 )
        return self

    def lookAt( self, vector: Vector3) -> 'Geometry':
        _obj.lookAt( vector )
        _obj.updateMatrix()
        self.applyMatrix4( _obj.matrix )
        return self

    def center( self ) -> 'Geometry':
        self.computeBoundingBox()
        self.boundingBox.getCenter( _offset ).negate()
        self.translate( _offset.x, _offset.y, _offset.z )
        return self

    def setFromPoints( self, points:'list[three.Vector2|Vector3]' ) -> 'Geometry':
        position = []

        for point in points:
            position.extend( [point.x, point.y, point.z or 0] )

        self.setAttribute( 'position', Float32BufferAttribute( position, 3 ) )
        return self

    def computeBoundingBox( self ):
        if self.boundingBox is None:
            self.boundingBox = Box3()

        position = self.attributes.position
        morphAttributesPosition = self.morphAttributes.position

        if position and position.isGLBufferAttribute:
            warn( f'THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box. Alternatively set "mesh.frustumCulled" to "false". {self}' )
            self.boundingBox.set(
                Vector3( float('-inf'),float('-inf'), float('-inf') ),
                Vector3( float('+inf'), float('+inf'), float('+inf') )
            )

            return

        if position is not None:
            self.boundingBox.setFromBufferAttribute( position )

            # process morph attributes if present

            if morphAttributesPosition:
                for i in range(len(morphAttributesPosition)):
                    morphAttribute = morphAttributesPosition[ i ]
                    _box.setFromBufferAttribute( morphAttribute )

                    if self.morphTargetsRelative:

                        _vector.addVectors( self.boundingBox.min, _box.min )
                        self.boundingBox.expandByPoint( _vector )

                        _vector.addVectors( self.boundingBox.max, _box.max )
                        self.boundingBox.expandByPoint( _vector )

                    else:

                        self.boundingBox.expandByPoint( _box.min )
                        self.boundingBox.expandByPoint( _box.max )

        else:
            self.boundingBox.makeEmpty()


        if math.isnan( self.boundingBox.min.x ) or math.isnan( self.boundingBox.min.y) or math.isnan( self.boundingBox.min.z ):
            warn( f'THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values. {self}')



    def computeBoundingSphere( self ):
        if self.boundingSphere is None:
            self.boundingSphere = Sphere()

        position = self.attributes.position
        morphAttributesPosition = self.morphAttributes.position

        if position and position.isGLBufferAttribute:
            warn( 'THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere. Alternatively set "mesh.frustumCulled" to "false".', self )
            self.boundingSphere.set(Vector3(), float('inf') )
            return

        if position:

            # first, find the center of the bounding sphere

            center = self.boundingSphere.center

            _box.setFromBufferAttribute( position )

            # process morph attributes if present

            if morphAttributesPosition:
                for i in range(len(morphAttributesPosition)):
                    morphAttribute = morphAttributesPosition[ i ]
                    _boxMorphTargets.setFromBufferAttribute( morphAttribute )

                    if self.morphTargetsRelative:
                        _vector.addVectors( _box.min, _boxMorphTargets.min )
                        _box.expandByPoint( _vector )

                        _vector.addVectors( _box.max, _boxMorphTargets.max )
                        _box.expandByPoint( _vector )

                    else:

                        _box.expandByPoint( _boxMorphTargets.min )
                        _box.expandByPoint( _boxMorphTargets.max )

            _box.getCenter( center )

            # second, try to find a boundingSphere with a radius smaller than the
            # boundingSphere of the boundingBox: sqrt(3) smaller in the best case

            maxRadiusSq = 0
            for i in range(position.count):
                _vector.fromBufferAttribute( position, i )
                maxRadiusSq = max( maxRadiusSq, center.distanceToSquared( _vector ) )

			# process morph attributes if present

            if morphAttributesPosition:
                for i in range(len(morphAttributesPosition)):

                    morphAttribute = morphAttributesPosition[ i ]
                    morphTargetsRelative = self.morphTargetsRelative
                    for j in range(morphAttribute.count):
                        _vector.fromBufferAttribute( morphAttribute, j )

                        if morphTargetsRelative:

                            _offset.fromBufferAttribute( position, j )
                            _vector.add( _offset )

                        maxRadiusSq = max( maxRadiusSq, center.distanceToSquared( _vector ) )

            self.boundingSphere.radius = math.sqrt( maxRadiusSq )

            if math.isnan( self.boundingSphere.radius ):
                warn( f'THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values. {self}' )


    def computeTangents(self):
        index = self.index
        attributes = self.attributes

        # based on http:#www.terathon.com/code/tangent.html
        # (per vertex tangents)

        if ( index is None or
                attributes.position is None or
                attributes.normal is None or
                attributes.uv is None ):

            warn( 'THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)' )
            return

        indices = index.array
        positions = attributes.position.array
        normals = attributes.normal.array
        uvs = attributes.uv.array

        nVertices = positions.length / 3

        if self.hasAttribute( 'tangent' ) == False:
            self.setAttribute( 'tangent', BufferAttribute( Float32Array( 4 * nVertices ), 4 ) )

        tangents = self.getAttribute( 'tangent' ).array

        tan1:'list[Vector3]' = []
        tan2:'list[Vector3]' = []

        for i in range(nVertices):
            tan1[ i ] = Vector3()
            tan2[ i ] = Vector3()


        vA = Vector3()
        vB = Vector3()
        vC = Vector3()

        uvA = Vector2()
        uvB = Vector2()
        uvC = Vector2()

        sdir = Vector3()
        tdir = Vector3()

        def handleTriangle( a, b, c ):

            vA.fromArray( positions, a * 3 )
            vB.fromArray( positions, b * 3 )
            vC.fromArray( positions, c * 3 )

            uvA.fromArray( uvs, a * 2 )
            uvB.fromArray( uvs, b * 2 )
            uvC.fromArray( uvs, c * 2 )

            vB.sub( vA )
            vC.sub( vA )

            uvB.sub( uvA )
            uvC.sub( uvA )

            r = 1.0 / ( uvB.x * uvC.y - uvC.x * uvB.y )

            # silently ignore degenerate uv triangles having coincident or colinear vertices
            
            if not math.isfinite( r ) :
                return

            sdir.copy( vB ).multiplyScalar( uvC.y ).addScaledVector( vC, - uvB.y ).multiplyScalar( r )
            tdir.copy( vC ).multiplyScalar( uvB.x ).addScaledVector( vB, - uvC.x ).multiplyScalar( r )

            tan1[ a ].add( sdir )
            tan1[ b ].add( sdir )
            tan1[ c ].add( sdir )

            tan2[ a ].add( tdir )
            tan2[ b ].add( tdir )
            tan2[ c ].add( tdir )

        groups = self.groups

        if len(groups) == 0:
            groups = [ {
                'start': 0,
                'count': indices.length
            } ]

        for i in range(len(groups)):
            group = groups[ i ]
            start = group.start
            count = group.count

            for j in range(start, start+count, 3):
                handleTriangle(
                    indices[ j + 0 ],
                    indices[ j + 1 ],
                    indices[ j + 2 ]
                )

        tmp = Vector3()
        tmp2 = Vector3()
        n = Vector3()
        n2 = Vector3()

        def handleVertex( v ):

            n.fromArray( normals, v * 3 )
            n2.copy( n )

            t = tan1[ v ]

            # Gram-Schmidt orthogonalize

            tmp.copy( t )
            tmp.sub( n.multiplyScalar( n.dot( t ) ) ).normalize()

            # Calculate handedness

            tmp2.crossVectors( n2, t )
            test = tmp2.dot( tan2[ v ] )
            w = - 1.0 if  test < 0.0 else 1.0

            tangents[ v * 4 ] = tmp.x
            tangents[ v * 4 + 1 ] = tmp.y
            tangents[ v * 4 + 2 ] = tmp.z
            tangents[ v * 4 + 3 ] = w

        for i in range(len(groups)):
            group = groups[ i ]
            start = group.start
            count = group.count
            for j in range(start, start+count, 3):
                handleVertex( indices[ j + 0 ] )
                handleVertex( indices[ j + 1 ] )
                handleVertex( indices[ j + 2 ] )



    def computeVertexNormals(self):
        index = self.index
        positionAttribute:'BufferAttribute' = self.getAttribute( 'position' )

        if positionAttribute is not None:
            normalAttribute:'BufferAttribute' = self.getAttribute( 'normal' )
            if normalAttribute is None:
                normalAttribute = BufferAttribute( Float32Array.allocate(positionAttribute.count * 3), 3 )
                self.setAttribute( 'normal', normalAttribute )
            else:
                # reset existing normals to zero
                for i in range(normalAttribute.count):
                    normalAttribute.setXYZ( i, 0, 0, 0 )

            pA = Vector3()
            pB = Vector3()
            pC = Vector3()
            nA = Vector3()
            nB = Vector3()
            nC = Vector3()
            cb = Vector3()
            ab = Vector3()

            # indexed elements
            if index:
                for i in range(0, index.count, 3):
                    vA = index.getX( i + 0 )
                    vB = index.getX( i + 1 )
                    vC = index.getX( i + 2 )

                    pA.fromBufferAttribute( positionAttribute, vA )
                    pB.fromBufferAttribute( positionAttribute, vB )
                    pC.fromBufferAttribute( positionAttribute, vC )

                    cb.subVectors( pC, pB )
                    ab.subVectors( pA, pB )
                    cb.cross( ab )

                    nA.fromBufferAttribute( normalAttribute, vA )
                    nB.fromBufferAttribute( normalAttribute, vB )
                    nC.fromBufferAttribute( normalAttribute, vC )

                    nA.add( cb )
                    nB.add( cb )
                    nC.add( cb )

                    normalAttribute.setXYZ( vA, nA.x, nA.y, nA.z )
                    normalAttribute.setXYZ( vB, nB.x, nB.y, nB.z )
                    normalAttribute.setXYZ( vC, nC.x, nC.y, nC.z )
            else:
                # non-indexed elements (unconnected triangle soup)
                for i in range(0, positionAttribute.count, 3):
                    pA.fromBufferAttribute( positionAttribute, i + 0 )
                    pB.fromBufferAttribute( positionAttribute, i + 1 )
                    pC.fromBufferAttribute( positionAttribute, i + 2 )

                    cb.subVectors( pC, pB )
                    ab.subVectors( pA, pB )
                    cb.cross( ab )

                    normalAttribute.setXYZ( i + 0, cb.x, cb.y, cb.z )
                    normalAttribute.setXYZ( i + 1, cb.x, cb.y, cb.z )
                    normalAttribute.setXYZ( i + 2, cb.x, cb.y, cb.z )

            self.normalizeNormals()
            normalAttribute.needsUpdate = True


    def merge( self, geometry:'Geometry', offset ):
        if not ( geometry and geometry.isBufferGeometry ):
            warn( f'THREE.BufferGeometry.merge(): geometry not an instance of THREE.BufferGeometry. ,{geometry}' )
            return

        if offset is None:
            offset = 0
            warn(
                'THREE.BufferGeometry.merge(): Overwriting original geometry, starting at offset=0. '
                + 'Use BufferGeometryUtils.mergeBufferGeometries() for lossless merge.'
            )

        attributes = self.attributes

        for key in attributes:
            if geometry.attributes[ key ] is None:
                continue

            attribute1 = attributes[ key ]
            attributeArray1 = attribute1.array

            attribute2 = geometry.attributes[ key ]
            attributeArray2 = attribute2.array

            attributeOffset = attribute2.itemSize * offset
            length = min( attributeArray2.length, attributeArray1.length - attributeOffset )

            i = 0
            j = attributeOffset

            while i < length:
                attributeArray1[ j ] = attributeArray2[ i ]
                i += 1
                j += 1

        return self

    def normalizeNormals(self):
        normals:'BufferAttribute' = self.attributes.normal
        for i in range(normals.count):
            _vector.fromBufferAttribute( normals, i )
            _vector.normalize()
            normals.setXYZ( i, _vector.x, _vector.y, _vector.z )


    def toIndexed(self):
        def convertBufferAttribute( attribute:'BufferAttribute', indices ):
            array = attribute.array
            itemSize = attribute.itemSize
            normalized = attribute.normalized

            array2 = array.__class__.allocate(len(indices) * itemSize)

            index = 0
            index2 = 0
            for i in range(len(indices)):
                if attribute.isInterleavedBufferAttribute:
                    index = indices[ i ] * attribute.data.stride + attribute.offset
                else:
                    index = indices[ i ] * itemSize

                for j in range(itemSize):
                    array2[ index2  ] = array[ index ]
                    index2 += 1
                    index += 1


            return BufferAttribute( array2, itemSize, normalized )
        #
        if self.index is None:
            warn( 'THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed.' )
            return self

        geometry2 = Geometry()

        indices = self.index.array
        attributes = self.attributes

        # attributes

        for name in attributes:
            attribute = attributes[ name ]
            newAttribute = convertBufferAttribute( attribute, indices )
            geometry2.setAttribute( name, newAttribute )


        # morph attributes

        morphAttributes = self.morphAttributes

        for name in morphAttributes:
            morphArray = []
            morphAttribute = morphAttributes[ name ] # morphAttribute: array of Float32BufferAttributes

            for i in range(len(morphAttribute)):
                attribute = morphAttribute[ i ]
                newAttribute = convertBufferAttribute( attribute, indices )
                morphArray.append( newAttribute )

            geometry2.morphAttributes[ name ] = morphArray

        geometry2.morphTargetsRelative = self.morphTargetsRelative

        # groups

        groups = self.groups

        for i in range(len(groups)):
            group = groups[ i ]
            geometry2.addGroup( group.start, group.count, group.materialIndex )
            
        return geometry2