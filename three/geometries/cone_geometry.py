import math
from .cylinder_geometry import CylinderGeometry

class ConeGeometry(CylinderGeometry):

    def __init__(self, radius = 1, height = 1, radialSegments = 8, heightSegments = 1, openEnded = False, thetaStart = 0, thetaLength = math.pi * 2 ) -> None:
        super().__init__(0, radius, height, radialSegments, heightSegments, openEnded, thetaStart, thetaLength)

        self._type = 'ConeGeometry'

        self.parameters = {
            'radius': radius,
            'height': height,
            'radialSegments': radialSegments,
            'heightSegments': heightSegments,
            'openEnded': openEnded,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }