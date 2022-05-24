from .node_material import NodeMaterial
from three.materials import MeshNormalMaterial
from ..shader.shader_node_base_elements import NormalNode, mul, add

defaultValues = MeshNormalMaterial()

class MeshNormalNodeMaterial(NodeMaterial):
    def __init__(self, parameters = None) -> None:
        super().__init__()
        #colorNode = NormalNode( NormalNode.VIEW )
        #colorNode = mul(colorNode, 0.5)
        self.colorNode = add(mul(NormalNode( NormalNode.VIEW ), 0.5), 0.5)
        #self.colorNode = None
        self.opacityNode = None
        self.alphaTestNode = None
        self.lightsNode = None
        self.positionNode = None

        self.fog = False

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def copy( self, source ):
        self.colorNode = source.colorNode
        self.opacityNode = source.opacityNode
        self.alphaTestNode = source.alphaTestNode
        self.positionNode = source.positionNode
        return super().copy( source )

    
    # def build( self, builder ):
    #     lightNode = self.lightNode
    #     diffuseColorNode = self.generateMain( builder )['diffuseColorNode']

    #     outgoingLightNode = self.generateLight( builder, { diffuseColorNode, lightNode } )

    #     self.generateOutput( builder, { diffuseColorNode, outgoingLightNode } )