from .node_material import NodeMaterial
from three.materials import MeshNormalMaterial

from ..shadernode.shader_node_elements import vec4, diffuseColor, materialOpacity, transformedNormalView, directionToColor

defaultValues = MeshNormalMaterial()

class MeshNormalNodeMaterial(NodeMaterial):

    isMeshNormalNodeMaterial = True

    def __init__(self, parameters = None) -> None:
        super().__init__()

        self.opacityNode = None
        self.positionNode = None

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )
    
    def constructDiffuseColor(self, builder, stack):

        opacityNode = float( self.opacityNode ) if self.opacityNode else materialOpacity

        stack.assign( diffuseColor, vec4( directionToColor( transformedNormalView ), opacityNode ) )


    def copy( self, source ):
        self.opacityNode = source.opacityNode
        self.positionNode = source.positionNode
        return super().copy( source )
