from inspect import isfunction
from three.materials import ShaderMaterial
from ..core.expression_node import ExpressionNode
from ..core.attribute_node import AttributeNode

from ..shadernode.shader_node_elements import (
    float, vec4,
   	assign, label, mul, bypass,
   	positionLocal, skinning, instance, modelViewProjection, lightingContext, colorSpace,
   	materialAlphaTest, materialColor, materialOpacity)

class NodeMaterial(ShaderMaterial):
    def __init__(self) -> None:
        super().__init__()
        self.lights = True

    def build( self, builder ):
        lightsNode = self.lightsNode
        diffuseColorNode = self.generateMain( builder )['diffuseColorNode']

        outgoingLightNode = self.generateLight( builder, { 'diffuseColorNode':diffuseColorNode, 'lightsNode':lightsNode } )

        self.generateOutput( builder, { 'diffuseColorNode':diffuseColorNode, 'outgoingLightNode': outgoingLightNode } )

    def customProgramCacheKey(self):
        return self.uuid + '-' + str(self.version)


    def generateMain( self, builder ):

        object = builder.object

        # < VERTEX STAGE >

        vertex = positionLocal

        if self.positionNode:
            vertex = bypass(vertex, assign(positionLocal, self.positionNode))

        if object.instanceMatrix and object.instanceMatrix.isInstancedBufferAttribute and builder.isAvailable('instance') == True:
            vertex = bypass( vertex, instance( object ) )


        if object.isSkinnedMesh == True:
            vertex = bypass( vertex, skinning( object ) )


        builder.context.vertex = vertex

        builder.addFlow( 'vertex', modelViewProjection() )

        # < FRAGMENT STAGE >
        if not self.colorNode and self.vertexColors == True:
            self.colorNode = AttributeNode('color', 'vec3')

        colorNode = vec4( self.colorNode or materialColor )

        # TODO - add support for flatShading?
        # if self.flatShading:
        #     colorNode = add(mul(normalize(cross(dFdx(positionWorld), dFdy(positionWorld))), 0.5), 0.5)

        opacityNode = float( self.opacityNode ) if self.opacityNode else materialOpacity

        # COLOR
        colorNode = builder.addFlow( 'fragment', label( colorNode, 'Color' ) )
        diffuseColorNode = builder.addFlow( 'fragment', label( colorNode, 'DiffuseColor' ) )

        # OPACITY
        opacityNode = builder.addFlow( 'fragment', label( opacityNode, 'OPACITY' ) )
        builder.addFlow( 'fragment', assign( diffuseColorNode.a, mul( diffuseColorNode.a, opacityNode ) ) )

        # ALPHA TEST
        if self.alphaTestNode or self.alphaTest > 0:

            alphaTestNode = float( self.alphaTestNode ) if self.alphaTestNode else materialAlphaTest

            builder.addFlow( 'fragment', label( alphaTestNode, 'AlphaTest' ) )

            # @TODO: remove ExpressionNode here and then possibly remove it completely
            builder.addFlow( 'fragment', ExpressionNode( 'if ( DiffuseColor.a <= AlphaTest ) { discard; }' ) )

        return { 'colorNode': colorNode, 'diffuseColorNode': diffuseColorNode }


    def generateLight( self, builder, parameters:dict ):
        diffuseColorNode = parameters.get('diffuseColorNode')
        lightingModelNode = parameters.get('lightingModelNode', None)
        lightsNode = parameters.get('lightsNode', builder.lightsNode)

        # < ANALYTIC LIGHTS >

        # OUTGOING LIGHT

        outgoingLightNode = diffuseColorNode.xyz
        if lightsNode: # and lightsNode.hasLight != False:  # TODO if show basic color when no lights?
            outgoingLightNode = builder.addFlow( 'fragment', label( lightingContext( lightsNode, lightingModelNode ), 'Light' ) )

        return outgoingLightNode

    def generateOutput( self, builder, parameters ):

        diffuseColorNode = parameters['diffuseColorNode']
        outgoingLightNode = parameters['outgoingLightNode']

        # OUTPUT
        outputNode = vec4( outgoingLightNode, diffuseColorNode.a )

        # ENCODING
        outputNode = colorSpace( outputNode, builder.renderer.outputEncoding )

        # FOG
        if builder.fogNode:
            outputNode = builder.fogNode.mix( outputNode )

        # RESULT
        builder.addFlow( 'fragment', label( outputNode, 'Output' ) )

        return outputNode


    def setDefaultValues( self, values ):

		# This approach is to reuse the native refreshUniforms*
		# and turn available the use of features like transmission and environment in core

        for property in values.__dict__:
            value = values.__dict__[ property ]

            if getattr(self, property, None) is None:
                if value and hasattr(value, 'clone') and isfunction(value.clone):
                    setattr(self, property, value.clone())
                else:
                    setattr(self, property, value)

        if self.defines and values.defines:
            self.defines.update(values.defines)
