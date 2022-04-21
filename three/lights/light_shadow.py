
from ..math import Vector2, Vector3, Vector4, Matrix4, Frustum
import three

_projScreenMatrix = Matrix4()
_lightPositionWorld = Vector3()
_lookTarget = Vector3()

class LightShadow:

    def __init__(self, camera:'three.Camera') -> None:
        self.camera = camera

        self.bias = 0
        self.normalBias = 0
        self.radius = 1
        self.blurSamples = 8

        self.mapSize = Vector2( 512, 512 )

        self.map = None
        self.mapPass = None
        self.matrix = Matrix4()

        self.autoUpdate = True
        self.needsUpdate = False

        self._frustum = Frustum()
        self._frameExtents = Vector2( 1, 1 )

        self._viewportCount = 1

        self._viewports = [Vector4( 0, 0, 1, 1 )]

    def getViewportCount(self):
        return self._viewportCount

    def getFrustum(self):
        return self._frustum

    def updateMatrices( self, light:'three.Light' ):
        shadowCamera = self.camera
        shadowMatrix = self.matrix

        _lightPositionWorld.setFromMatrixPosition( light.matrixWorld )
        shadowCamera.position.copy( _lightPositionWorld )

        _lookTarget.setFromMatrixPosition( light.target.matrixWorld )
        shadowCamera.lookAt( _lookTarget )
        shadowCamera.updateMatrixWorld()

        _projScreenMatrix.multiplyMatrices( shadowCamera.projectionMatrix, shadowCamera.matrixWorldInverse )
        self._frustum.setFromProjectionMatrix( _projScreenMatrix )

        shadowMatrix.set(
            0.5, 0.0, 0.0, 0.5,
            0.0, 0.5, 0.0, 0.5,
            0.0, 0.0, 0.5, 0.5,
            0.0, 0.0, 0.0, 1.0
        )

        shadowMatrix.multiply( shadowCamera.projectionMatrix )
        shadowMatrix.multiply( shadowCamera.matrixWorldInverse )


    def getViewport( self, viewportIndex ):
        return self._viewports[ viewportIndex ]


    def getFrameExtents(self):
        return self._frameExtents

    def dispose(self):
        if self.map:
            self.map.dispose()

        if self.mapPass:
            self.mapPass.dispose()


    def copy( self, source:'LightShadow' ):
        self.camera = source.camera.clone()
        self.bias = source.bias
        self.radius = source.radius
        self.mapSize.copy( source.mapSize )
        return self

    def clone(self):
        return self.__class__().copy( self )
