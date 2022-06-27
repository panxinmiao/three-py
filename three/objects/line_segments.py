from .line import Line
from ..math import Vector3
from ..core import Float32BufferAttribute
from warnings import warn

_start = Vector3()
_end = Vector3()

class LineSegments(Line):

    isLineSegments = True

    def __init__(self, geometry=None, material=None):
        super().__init__(geometry, material)


    def computeLineDistances(self):
        geometry = self.geometry

        # we assume non-indexed geometry

        if geometry.index is None:
            positionAttribute = geometry.attributes.position
            lineDistances = []

            for i in range(0, positionAttribute.count, 2):
                _start.fromBufferAttribute( positionAttribute, i )
                _end.fromBufferAttribute( positionAttribute, i + 1 )

                lineDistances.append( 0 if i==0 else lineDistances[i - 1] )
                lineDistances.append( lineDistances[ i ] +_start.distanceTo(_end) )


            geometry.setAttribute( 'lineDistance', Float32BufferAttribute( lineDistances, 1 ) )

        else:
            warn( 'THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.' )

        return self
