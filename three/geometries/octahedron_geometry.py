from .polyhedron_geometry import PolyhedronGeometry

class OctahedronGeometry(PolyhedronGeometry):
    def __init__(self, radius = 1, detail = 0) -> None:

        vertices = [
            1, 0, 0, 	- 1, 0, 0,	0, 1, 0,
			0, - 1, 0, 	0, 0, 1,	0, 0, - 1
        ]

        indices = [
            0, 2, 4,	0, 4, 3,	0, 3, 5,
			0, 5, 2,	1, 2, 5,	1, 5, 3,
			1, 3, 4,	1, 4, 2
        ]

        super().__init__( vertices, indices, radius, detail )

        self._type = 'OctahedronGeometry'

        self.parameters = {
            'radius': radius,
            'detail': detail
        }