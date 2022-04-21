# Node, OperatorNode, MaterialReferenceNode

from ..core.node import Node
from ..math.operator_node import OperatorNode
from .material_reference_node import MaterialReferenceNode

class MaterialNode(Node):
    ALPHA_TEST = 'alphaTest'
    COLOR = 'color'
    OPACITY = 'opacity'
    SPECULAR = 'specular'
    ROUGHNESS = 'roughness'
    METALNESS = 'metalness'

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

        elif scope == MaterialNode.SPECULAR:
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
                node = OperatorNode( '*', colorNode, MaterialReferenceNode( 'map', 'texture' ) )
            else:
                node = colorNode

        elif scope == MaterialNode.OPACITY:
            opacityNode = MaterialReferenceNode( 'opacity', 'float' )

            if material.alphaMap and material.alphaMap.isTexture:
                node = OperatorNode( '*', opacityNode, MaterialReferenceNode( 'alphaMap', 'texture' ) )
            else:
                node = opacityNode

        elif scope == MaterialNode.SPECULAR:
            specularTintNode = MaterialReferenceNode( 'specularTint', 'color' )

            if material.specularTintMap and material.specularTintMap.isTexture:
                node = OperatorNode( '*', specularTintNode, MaterialReferenceNode( 'specularTintMap', 'texture' ) )
            else:
                node = specularTintNode

        else:
            outputType = self.getNodeType( builder )
            node = MaterialReferenceNode( scope, outputType )

        return node.build( builder, output )
