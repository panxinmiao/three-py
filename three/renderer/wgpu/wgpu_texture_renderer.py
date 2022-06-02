
from ..render_target import RenderTarget

class WgpuTextureRenderer:

    def __init__(self, renderer, options = {}) -> None:
        self.renderer = renderer

        self.renderTarget = RenderTarget( options )

    
    def getTexture(self):
        return self.renderTarget.texture

    def setSize(self, width, height ):
        self.renderTarget.setSize( width, height )

    def render(self, scene, camera):
        renderer = self.renderer
        renderTarget = self.renderTarget

        renderer.setRenderTarget( renderTarget )
        renderer.render( scene, camera )
        renderer.setRenderTarget( None )
