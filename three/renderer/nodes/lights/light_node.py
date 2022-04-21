# from three.renderer.nodes import Node, NodeUpdateType, ColorNode, FloatNode, Object3DNode, PositionNode, OperatorNode, MathNode, getDistanceAttenuation
from ..core.node import Node
from ..core.constants import NodeUpdateType
from ..core.uniform_node import UniformNode
from ..accessors.object3d_node import Object3DNode
from ..accessors.position_node import PositionNode
from ..math.math_node import MathNode
from ..math.operator_node import OperatorNode
from ..functions import getDistanceAttenuation

from ....math import Color

class LightNode(Node):

    def __init__(self, light=None ) -> None:
        super().__init__('vec3')

        self.updateType = NodeUpdateType.Object

        self.light = light

        self._colorNode = UniformNode( Color() )

        self._lightCutoffDistanceNode = UniformNode( 0 )
        self._lightDecayExponentNode = UniformNode( 0 )

    def getHash(self, *args):
        return self.light.uuid

    def update( self, *args):
        self._colorNode.value.copy( self.light.color ).multiplyScalar( self.light.intensity )
        self._lightCutoffDistanceNode.value = self.light.distance or 0
        self._lightDecayExponentNode.value = self.light.decay or 0


    def generate( self, builder):

        lightPositionView = Object3DNode( Object3DNode.VIEW_POSITION )
        positionView = PositionNode( PositionNode.VIEW )

        lVector = OperatorNode( '-', lightPositionView, positionView )

        lightDirection = MathNode( MathNode.NORMALIZE, lVector )

        lightDistance = MathNode( MathNode.LENGTH, lVector )

        lightAttenuation = getDistanceAttenuation( {
			'lightDistance': lightDistance, 
			'cutoffDistance': self._lightCutoffDistanceNode,
			'decayExponent': self._lightDecayExponentNode
		} )

        lightColor = OperatorNode( '*', self._colorNode, lightAttenuation )

        lightPositionView.object3d = self.light

        lightingModelFunctionNode = builder.context.lightingModelNode

        if lightingModelFunctionNode:
            # directDiffuse = builder.context.directDiffuse
            # directSpecular = builder.context.directSpecular
            reflectedLight = builder.context.reflectedLight
            lightingModelFunctionNode( {
				'lightDirection': lightDirection,
				'lightColor': lightColor,
				# 'directDiffuse': directDiffuse,
				# 'directSpecular': directSpecular
                'reflectedLight': reflectedLight
			}, builder )

