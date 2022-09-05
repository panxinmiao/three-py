from .polyhedron_geometry import PolyhedronGeometry

class TetrahedronGeometry(PolyhedronGeometry):
    def __init__(self, radius = 1, detail = 0) -> None:

        vertices = [
            1, 1, 1, 	- 1, - 1, 1, 	- 1, 1, - 1, 	1, - 1, - 1
        ]

        indices = [
            2, 1, 0, 	0, 3, 2,	1, 3, 0,	2, 3, 1
        ]

        super().__init__( vertices, indices, radius, detail )

        self._type = 'TetrahedronGeometry'

        self.parameters = {
            'radius': radius,
            'detail': detail
        }