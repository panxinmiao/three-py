import math
from ..core import Object3D, BufferGeometry, Float32BufferAttribute
from ..materials import LineBasicMaterial
from ..objects import LineSegments
from ..math import Vector3

_vector = Vector3()

class SpotLightHelper(Object3D):

    def __init__(self, light, color=None):
        super().__init__()

        self.light = light

        self.matrix = light.matrixWorld
        self.matrixAutoUpdate = False

        self.color = color

        self._type = 'SpotLightHelper'

        geometry = BufferGeometry()

        positions = [
			0, 0, 0, 	0, 0, 1,
			0, 0, 0, 	1, 0, 1,
			0, 0, 0,	- 1, 0, 1,
			0, 0, 0, 	0, 1, 1,
			0, 0, 0, 	0, - 1, 1
		]

        for i in range(32):
            p1 = i / 32 * math.pi * 2
            p2 = (i + 1) / 32 * math.pi * 2

            positions.extend([math.cos(p1), math.sin(p1), 1])
            positions.extend([math.cos(p2), math.sin(p2), 1])

        geometry.setAttribute('position', Float32BufferAttribute(positions, 3))

        material = LineBasicMaterial( { "fog": False, "toneMapped": False } )

        self.cone = LineSegments(geometry, material)
        self.add(self.cone)

        self.update()

    def dispose(self):
        self.cone.geometry.dispose()
        self.cone.material.dispose()

    def updateMatrixWorld(self, *args, **kwargs):
        self.update()
        super().updateMatrixWorld(*args, **kwargs)

    def update(self):
        self.light.updateWorldMatrix( True, False )
        self.light.target.updateWorldMatrix( True, False )

        coneLength = self.light.distance or 1000
        coneWidth = coneLength * math.tan( self.light.angle )
        self.cone.scale.set( coneWidth, coneWidth, coneLength )

        _vector.setFromMatrixPosition( self.light.target.matrixWorld )
        self.cone.lookAt( _vector )

        if self.color is not None:
            self.cone.material.color.set(self.color)
        else:
            self.cone.material.color.copy(self.light.color)
