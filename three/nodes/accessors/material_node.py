from ..core.node import Node
from ..core.uniform_node import UniformNode
from ..core.const_node import ConstNode
from ..core.const_node import ConstNode
from ..accessors.uv_node import UVNode
from ..math.operator_node import OperatorNode
from .material_reference_node import MaterialReferenceNode
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

    def getFloat( self, property):
        return MaterialReferenceNode( property, 'float' )
    
    def getColor( self, property):
        return MaterialReferenceNode( property, 'color' )
    
    def getTexture( self, property):
        textureRefNode = MaterialReferenceNode( property, 'texture' )
        textureRefNode.node.uvNode = MaterialNode( MaterialNode.UV )
        return textureRefNode

    def construct( self, builder ):
        material = builder.getContextValue( 'material' )
        scope = self.scope
        node = None
        if scope == MaterialNode.ALPHA_TEST:
            node = self.getFloat( 'alphaTest' )

        elif scope == MaterialNode.COLOR:
            colorNode = self.getColor( 'color' )

            if material.map and material.map.isTexture:
                node = OperatorNode( '*', colorNode, self.getTexture( 'map' ) )
            else:
                node = colorNode

        elif scope == MaterialNode.OPACITY:
            opacityNode = self.getFloat( 'opacity' )

            if material.alphaMap and material.alphaMap.isTexture:
                node = OperatorNode( '*', opacityNode, self.getTexture( 'alphaMap' ) )
            else:
                node = opacityNode
        
        elif scope == MaterialNode.SHININESS:
            return self.getFloat( 'shininess' )

        elif scope == MaterialNode.SPECULAR_COLOR:
            return self.getColor( 'specular' )
        
        elif scope == MaterialNode.REFLECTIVITY:
            reflectivityNode = self.getFloat( 'reflectivity' )

            if material.specularMap and material.specularMap.isTexture:
                node = OperatorNode( '*', reflectivityNode, SplitNode( self.getTexture( 'specularMap' ), 'r' ) )
            else:
                node = reflectivityNode

        elif scope == MaterialNode.ROUGHNESS:
            roughnessNode = self.getFloat( 'roughness' )
            if material.roughnessMap and material.roughnessMap.isTexture:
                node = OperatorNode( '*', roughnessNode, SplitNode( self.getTexture( 'roughnessMap' ), 'g' ) )
            else:
                node = roughnessNode

        elif scope == MaterialNode.METALNESS:
            metalnessNode = self.getFloat( 'metalness' )
            if material.metalnessMap and material.metalnessMap.isTexture:
                node = OperatorNode( '*', metalnessNode, SplitNode( self.getTexture( 'metalnessMap' ), 'b' ) )
            else:
                node = metalnessNode
        elif scope == MaterialNode.EMISSIVE:
            emissiveNode = self.getColor( 'emissive' )
            if material.emissiveMap and material.emissiveMap.isTexture:
                node = OperatorNode( '*', emissiveNode, self.getTexture( 'emissiveMap' ) )
            else:
                node = emissiveNode
        elif scope == MaterialNode.ROTATION:
            node = self.getFloat( 'rotation' )
        
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
