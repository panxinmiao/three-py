from ..core.node import Node
from ..core.uniform_node import UniformNode
from ..core.const_node import ConstNode
from ..core.const_node import ConstNode
from ..accessors.uv_node import UVNode
from ..math.operator_node import OperatorNode
from .material_reference_node import MaterialReferenceNode
from .texture_node import TextureNode
from ..utils.split_node import SplitNode
from ..utils.join_node import JoinNode

class MaterialNode(Node):
    ALPHA_TEST = 'alphaTest'
    COLOR = 'color'
    OPACITY = 'opacity'
    SHININESS = 'shininess'
    SPECULAR_COLOR = 'specularColor'
    REFLECTIVITY = 'reflectivity'
    ROUGHNESS = 'roughness'
    METALNESS = 'metalness'
    EMISSIVE = 'emissive'
    ROTATION = 'rotation'
    UV = 'uv'

    def __init__(self, scope) -> None:
        super().__init__()
        self.scope = scope

    def getNodeType( self, builder ):

        scope = self.scope
        material = builder.getContextValue( 'material' )

        if scope == MaterialNode.COLOR:
            return 'vec4' if material.map else 'vec3'

        elif scope == MaterialNode.ALPHA_TEST or scope == MaterialNode.OPACITY or scope == MaterialNode.ROTATION:
            return 'float'
        
        elif scope == MaterialNode.UV:
            return 'vec2'

        elif scope == MaterialNode.EMISSIVE:
            return 'vec3'

        elif scope == MaterialNode.ROUGHNESS or scope == MaterialNode.METALNESS or scope == MaterialNode.SPECULAR_COLOR or scope == MaterialNode.SHININESS:
            return 'float'

        # else:
        #     raise Exception( 'Unknown scope: ' + scope )

    def construct( self, builder ):
        material = builder.getContextValue( 'material' )
        scope = self.scope
        node = None
        if scope == MaterialNode.ALPHA_TEST:
            node = MaterialReferenceNode( 'alphaTest', 'float' )

        elif scope == MaterialNode.COLOR:
            colorNode = MaterialReferenceNode( 'color', 'color' )

            if material.map and material.map.isTexture:
                map = TextureNode(material.map, MaterialNode( MaterialNode.UV ))
                node = OperatorNode('*', colorNode, map)
            else:
                node = colorNode

        elif scope == MaterialNode.OPACITY:
            opacityNode = MaterialReferenceNode( 'opacity', 'float' )

            if material.alphaMap and material.alphaMap.isTexture:
                node = OperatorNode( '*', opacityNode, MaterialReferenceNode( 'alphaMap', 'texture' ) )
            else:
                node = opacityNode
        
        elif scope == MaterialNode.SHININESS:
            return MaterialReferenceNode( 'shininess', 'float' )

        elif scope == MaterialNode.SPECULAR_COLOR:
            return MaterialReferenceNode( 'specular', 'color' )
        
        elif scope == MaterialNode.REFLECTIVITY:
            reflectivityNode = MaterialReferenceNode( 'reflectivity', 'float' )

            if material.specularMap and material.specularMap.isTexture:
                node = OperatorNode( '*', reflectivityNode, SplitNode( TextureNode( material.specularMap ), 'r' ) )
            else:
                node = reflectivityNode

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
        elif scope == MaterialNode.ROTATION:
            node = MaterialReferenceNode( 'rotation', 'float' )
        
        elif scope == MaterialNode.UV:

            uvNode = None

            uvScaleMap = (material.map or
                material.specularMap or
                material.displacementMap or
                material.normalMap or
                material.bumpMap or
                material.roughnessMap or
                material.metalnessMap or
                material.alphaMap or
                material.emissiveMap or
                material.clearcoatMap or
                material.clearcoatNormalMap or
                material.clearcoatRoughnessMap or
                material.iridescenceMap or
                material.iridescenceThicknessMap or
                material.specularIntensityMap or
                material.specularColorMap or
                material.transmissionMap or
                material.thicknessMap or
                material.sheenColorMap or
                material.sheenRoughnessMap)
            
            if uvScaleMap:

                if uvScaleMap.isRenderTarget:
                    uvScaleMap = uvScaleMap.texture

                if uvScaleMap.matrixAutoUpdate is True:
                    uvScaleMap.updateMatrix()

                uvNode = OperatorNode( '*', UniformNode( uvScaleMap.matrix ), JoinNode( [ UVNode(), ConstNode( 1 ) ] ) )

                return uvNode or UVNode()

        else:
            outputType = self.getNodeType( builder )
            node = MaterialReferenceNode( scope, outputType )

        return node
