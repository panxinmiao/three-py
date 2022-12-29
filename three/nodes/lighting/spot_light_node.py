import math
from .analytic_light_node import AnalyticLightNode
from .lights_node import LightsNode
from ..functions.light.getDistanceAttenuation import getDistanceAttenuation
from ..functions.light.getDirectionVector import getDirectionVector
from ..shadernode.shader_node_base_elements import uniform, smoothstep, positionView, objectViewPosition, normalize, dot, length, cond
from ...lights import SpotLight
from ...math import Vector3

getSpotAttenuation = lambda coneCosine, penumbraCosine, angleCosine: smoothstep(coneCosine, penumbraCosine, angleCosine)

class SpotLightNode(AnalyticLightNode):

    def __init__(self, light=None) -> None:
        super().__init__(light)

        self.directionNode = uniform( Vector3() )

        self.coneCosNode = uniform( 0 )
        self.penumbraCosNode = uniform( 0 )

        self.cutoffDistanceNode = uniform( 0 )
        self.decayExponentNode = uniform( 0 )

    
    def update(self, frame):
        super().update(frame)

        light = self.light

        getDirectionVector( light, frame.camera, self.directionNode.value )

        self.coneCosNode.value = math.cos( light.angle )
        self.penumbraCosNode.value = math.cos( light.angle * ( 1 - light.penumbra ) )

        self.cutoffDistanceNode.value = light.distance
        self.decayExponentNode.value = light.decay
    
    def construct(self, builder):
        
        colorNode = self.colorNode
        cutoffDistanceNode = self.cutoffDistanceNode
        decayExponentNode = self.decayExponentNode
        light = self.light

        lVector = objectViewPosition(light) - positionView
        lightDirection = normalize(lVector)
        angleCos = dot(lightDirection, self.directionNode)
        spotAttenuation = getSpotAttenuation( self.coneCosNode, self.penumbraCosNode, angleCos )

        lightDistance = length(lVector)

        lightAttenuation = getDistanceAttenuation.call( {
			'lightDistance': lightDistance,
			'cutoffDistance': cutoffDistanceNode,
			'decayExponent': decayExponentNode
		} )

        finalColor = colorNode * spotAttenuation * lightAttenuation

        lightColor = cond( spotAttenuation > 0, finalColor, 0 )

        lightingModelFunctionNode = builder.context.lightingModelNode
        reflectedLight = builder.context.reflectedLight

        if lightingModelFunctionNode and lightingModelFunctionNode.direct:
            lightingModelFunctionNode.direct.call({
                "lightDirection": lightDirection,
                "lightColor": lightColor,
                "reflectedLight": reflectedLight
            }, builder)

LightsNode.setReference( SpotLight, SpotLightNode )