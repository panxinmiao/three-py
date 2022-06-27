from .light_shadow import LightShadow
from ..camera.perspective_camera import PerspectiveCamera
from ..math import Matrix4, Vector2, Vector3, Vector4

_projScreenMatrix = Matrix4()
_lightPositionWorld = Vector3()
_lookTarget = Vector3()

class PointLightShadow(LightShadow):

    isPointLightShadow = True

    def __init__(self) -> None:

        super().__init__(PerspectiveCamera( 90, 1, 0.5, 500 ))

        self._frameExtents = Vector2( 4, 2 )

        self._viewportCount = 6

        self._viewports = [
            # These viewports map a cube-map onto a 2D texture with the
            # following orientation:
            #
            #  xzXZ
            #   y Y
            #
            # X - Positive x direction
            # x - Negative x direction
            # Y - Positive y direction
            # y - Negative y direction
            # Z - Positive z direction
            # z - Negative z direction

            # positive X
            Vector4( 2, 1, 1, 1 ),
            # negative X
            Vector4( 0, 1, 1, 1 ),
            # positive Z
            Vector4( 3, 1, 1, 1 ),
            # negative Z
            Vector4( 1, 1, 1, 1 ),
            # positive Y
            Vector4( 3, 0, 1, 1 ),
            # negative Y
            Vector4( 1, 0, 1, 1 )
        ]

        self._cubeDirections = [
            Vector3( 1, 0, 0 ), Vector3( - 1, 0, 0 ), Vector3( 0, 0, 1 ),
            Vector3( 0, 0, - 1 ), Vector3( 0, 1, 0 ), Vector3( 0, - 1, 0 )
        ]

        self._cubeUps = [
            Vector3( 0, 1, 0 ), Vector3( 0, 1, 0 ), Vector3( 0, 1, 0 ),
            Vector3( 0, 1, 0 ), Vector3( 0, 0, 1 ), Vector3( 0, 0, - 1 )
        ]

    def updateMatrices( self, light, viewportIndex = 0 ):
        camera:'PerspectiveCamera' = self.camera
        shadowMatrix = self.matrix

        far = light.distance or camera.far

        if far != camera.far:
            camera.far = far
            camera.updateProjectionMatrix()

        _lightPositionWorld.setFromMatrixPosition( light.matrixWorld )
        camera.position.copy( _lightPositionWorld )

        _lookTarget.copy( camera.position )
        _lookTarget.add( self._cubeDirections[ viewportIndex ] )
        camera.up.copy( self._cubeUps[ viewportIndex ] )
        camera.lookAt( _lookTarget )
        camera.updateMatrixWorld()

        shadowMatrix.makeTranslation( - _lightPositionWorld.x, - _lightPositionWorld.y, - _lightPositionWorld.z )

        _projScreenMatrix.multiplyMatrices( camera.projectionMatrix, camera.matrixWorldInverse )
        self._frustum.setFromProjectionMatrix( _projScreenMatrix )
