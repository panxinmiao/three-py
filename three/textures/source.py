from ..structure import NoneAttribute
import uuid, warnings

class Source(NoneAttribute):

    def __init__(self, data = None ) -> None:
        super().__init__()
        self.uuid = uuid.uuid1()
        self.data = data
        self.version = 0

        self._needsUpdate = False

    @property
    def needsUpdate(self):
        return self._needsUpdate

    @needsUpdate.setter
    def needsUpdate(self, value):
        self._needsUpdate = value
        if value:
            self.version += 1


def serializeImage( image ):
    if image is None:
        return None

    if image.data:
            # images of DataTexture
            return {
                'data': image.data.copy(),
                'width': image.width,
                'height': image.height,
                'type': image.data.__class__.__name__
            }

    else:
        warnings.warn( 'THREE.Texture: Unable to serialize Texture.' )
        return {}
