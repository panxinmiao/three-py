from ..core import Object3D, BufferGeometry, Float32BufferAttribute
from ..materials import LineBasicMaterial
from ..math import Sphere, Ray, Matrix4, Vector3
from warnings import warn


_start = Vector3()
_end = Vector3()
# _inverseMatrix = Matrix4()
# _ray = Ray()
# _sphere = Sphere()


class Line(Object3D):

    isLine = True

    def __init__(self, geometry = None, material = None):

        super().__init__()

        self.geometry = geometry or BufferGeometry()
        self.material = material or LineBasicMaterial()

        self.updateMorphTargets()

    def copy(self, source):

        super().copy(source)

        self.material = source.material
        self.geometry = source.geometry

        return self

    def computeLineDistances(self):
        geometry = self.geometry

        # we assume non-indexed geometry
        if geometry.index is None:

            positionAttribute = geometry.attributes.position
            lineDistances = [ 0 ]

            for i in range(1, positionAttribute.count):

                _start.fromBufferAttribute( positionAttribute, i - 1 )
                _end.fromBufferAttribute( positionAttribute, i )

                # lineDistances[ i ] = lineDistances[ i - 1 ]
                lineDistances.append(lineDistances[ i - 1 ])
                lineDistances[ i ] += _start.distanceTo( _end )

            geometry.setAttribute( 'lineDistance', Float32BufferAttribute( lineDistances, 1 ) )

        else:
            warn( 'THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.' )


        return self

    # def raycast(self, raycaster, intersects):
    #     pass

    def updateMorphTargets(self):
        geometry = self.geometry
        morphAttributes = geometry.morphAttributes
        keys = morphAttributes.keys()

        if len(keys) > 0:
            morphAttribute = morphAttributes[ keys[ 0 ] ]

            if morphAttribute is not None:

                self.morphTargetInfluences = []
                self.morphTargetDictionary = {}

                for morph in morphAttribute:
                    name = morph.name or str( morph )

                    self.morphTargetInfluences.append( 0 )
                    self.morphTargetDictionary[ name ] = morph
