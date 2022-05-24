from ..core.node import Node
from ..math.operator_node import OperatorNode
from .material_reference_node import MaterialReferenceNode
from .texture_node import TextureNode
from ..utils.split_node import SplitNode

class MaterialNode(Node):
    ALPHA_TEST = 'alphaTest'
    COLOR = 'color'
    OPACITY = 'opacity'
    ROUGHNESS = 'roughness'
    METALNESS = 'metalness'
    EMISSIVE = 'emissive'

    def __init__(self, scope = COLOR) -> None:
        super().__init__()
        self.scope = scope

    def getNodeType( self, builder ):

        scope = self.scope
        material = builder.getContextValue( 'material' )

        if scope == MaterialNode.COLOR:
            return 'vec4' if material.map else 'vec3'

        elif scope == MaterialNode.OPACITY:
            return 'float'

        elif scope == MaterialNode.EMISSIVE:
            return 'vec3'

        elif scope == MaterialNode.ROUGHNESS or scope == MaterialNode.METALNESS:
            return 'float'

    def generate( self, builder, output ):
        material = builder.getContextValue( 'material' )
        scope = self.scope
        node = None
        if scope == MaterialNode.ALPHA_TEST:
            node = MaterialReferenceNode( 'alphaTest', 'float' )

        elif scope == MaterialNode.COLOR:
            colorNode = MaterialReferenceNode( 'color', 'color' )

            if material.map and material.map.isTexture:
                map = TextureNode(material.map)
                node = OperatorNode('*', colorNode, map)
            else:
                node = colorNode

        elif scope == MaterialNode.OPACITY:
            opacityNode = MaterialReferenceNode( 'opacity', 'float' )

            if material.alphaMap and material.alphaMap.isTexture:
                node = OperatorNode( '*', opacityNode, MaterialReferenceNode( 'alphaMap', 'texture' ) )
            else:
                node = opacityNode

        elif scope == MaterialNode.ROUGHNESS:
            roughnessNode = MaterialReferenceNode('roughness', 'float')
            if material.roughnessMap and material.roughnessMap.isTexture:
                node = OperatorNode('*', roughnessNode, SplitNode(TextureNode(material.roughnessMap), 'g'))
            else:
                node = roughnessNode

        elif scope == MaterialNode.METALNESS:
            metalnessNode = MaterialReferenceNode('metalness', 'float')
            if material.metalnessMap and material.metalnessMap.isTexture:
                node = OperatorNode('*', metalnessNode, SplitNode(TextureNode(material.metalnessMap), 'b'))
            else:
                node = metalnessNode
        elif scope == MaterialNode.EMISSIVE:
            emissiveNode = MaterialReferenceNode('emissive', 'color')
            if material.emissiveMap and material.emissiveMap.isTexture:
                node = OperatorNode('*', emissiveNode, TextureNode(material.emissiveMap) )
            else:
                node = emissiveNode
        else:
            outputType = self.getNodeType( builder )
            node = MaterialReferenceNode( scope, outputType )

        return node.build( builder, output )
