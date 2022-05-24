#from three.renderer.nodes import Node, NodeUpdateType, AttributeNode, ShaderNode, assign, element, add, mul, transformDirection, Matrix4Node, BufferNode, PositionNode, NormalNode

from ..core.node import Node
from ..core.constants import NodeUpdateType
from ..shadernode.shader_node import ShaderNode
from ..shadernode.shader_node_base_elements import attribute, buffer, mat4, uniform, positionLocal, normalLocal, assign, element, add,  mul, transformDirection


class SkinningNode(Node):

    def __skinning_func( inputs, builder):
        # { position, normal, index, weight, bindMatrix, bindMatrixInverse, boneMatrices } = inputs

        index = inputs['index']
        weight = inputs['weight']
        bindMatrix = inputs['bindMatrix']
        bindMatrixInverse = inputs['bindMatrixInverse']
        boneMatrices = inputs['boneMatrices']


        boneMatX = element( boneMatrices, index.x )
        boneMatY = element( boneMatrices, index.y )
        boneMatZ = element( boneMatrices, index.z )
        boneMatW = element( boneMatrices, index.w )

        # POSITION

        skinVertex = mul( bindMatrix, positionLocal )

        skinned = add(
            mul( mul( boneMatX, skinVertex ), weight.x ),
            mul( mul( boneMatY, skinVertex ), weight.y ),
            mul( mul( boneMatZ, skinVertex ), weight.z ),
            mul( mul( boneMatW, skinVertex ), weight.w )
        )

        skinPosition = mul( bindMatrixInverse, skinned ).xyz

        # NORMAL

        skinMatrix = add(
            mul( weight.x, boneMatX ),
            mul( weight.y, boneMatY ),
            mul( weight.z, boneMatZ ),
            mul( weight.w, boneMatW )
        )

        skinMatrix = mul( mul( bindMatrixInverse, skinMatrix ), bindMatrix )

        skinNormal = transformDirection( skinMatrix, normalLocal ).xyz

        # ASSIGNS

        assign( positionLocal, skinPosition ).build( builder )
        assign( normalLocal, skinNormal ).build( builder )

    __Skinning = ShaderNode(__skinning_func)

    def __init__(self, skinnedMesh ) -> None:
        super().__init__('void')
        
        self.skinnedMesh = skinnedMesh

        self.updateType = NodeUpdateType.Object

		#

        self.skinIndexNode =  attribute( 'skinIndex', 'uvec4' )
        self.skinWeightNode = attribute( 'skinWeight', 'vec4' )

        self.bindMatrixNode = uniform( mat4(skinnedMesh.bindMatrix) )
        self.bindMatrixInverseNode = uniform( mat4( skinnedMesh.bindMatrixInverse ) )
        self.boneMatricesNode = buffer( skinnedMesh.skeleton.boneMatrices, 'mat4', len(skinnedMesh.skeleton.bones) )

    
    def generate( self, builder ):

        SkinningNode.__Skinning( {
			'index': self.skinIndexNode,
			'weight': self.skinWeightNode,
			'bindMatrix': self.bindMatrixNode,
			'bindMatrixInverse': self.bindMatrixInverseNode,
			'boneMatrices': self.boneMatricesNode
		}, builder )


    def update(self, *args):
        self.skinnedMesh.skeleton.update()
