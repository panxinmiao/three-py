from inspect import isfunction
from ....materials import ShaderMaterial
from ..core.expression_node import ExpressionNode
from ..core.attribute_node import AttributeNode

from ..shader.shader_node_elements import (float, vec3, vec4,
	assign, label, mul, add, bypass,
	positionLocal, skinning, instance, modelViewProjection, context, lightContext, colorSpace,
	materialAlphaTest, materialColor, materialOpacity)

class NodeMaterial(ShaderMaterial):
    def __init__(self) -> None:
        super().__init__()
        self.lights = True

    def build( self, builder ):
        lightNode = self.lightNode
        diffuseColorNode = self.generateMain( builder )['diffuseColorNode']

        outgoingLightNode = self.generateLight( builder, { 'diffuseColorNode':diffuseColorNode, 'lightNode':lightNode } )

        self.generateOutput( builder, { 'diffuseColorNode':diffuseColorNode, 'outgoingLightNode': outgoingLightNode } )

    def generateMain( self, builder ):

        object = builder.object

        # < VERTEX STAGE >

        vertex = positionLocal

        if self.positionNode:
            vertex = bypass( vertex, assign( vertex, self.positionNode ) )

        if object.isInstancedMesh == True and builder.isAvailable( 'instance' ) == True:
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
        lightNode = parameters.get('lightNode', None)
        lightingModelNode = parameters.get('lightingModelNode', None)
        # < ANALYTIC LIGHTS >

        # OUTGOING LIGHT

        outgoingLightNode = diffuseColorNode.xyz
        if lightNode and lightNode.hasLight != False:
            outgoingLightNode = builder.addFlow( 'fragment', label( lightContext( lightNode, lightingModelNode ), 'Light' ) )

        # EMISSIVE

        if self.emissiveNode:
            outgoingLightNode = add( vec3( self.emissiveNode ), outgoingLightNode )

        return outgoingLightNode

    def generateOutput( self, builder, parameters ):

        diffuseColorNode = parameters['diffuseColorNode']
        outgoingLightNode = parameters['outgoingLightNode']

        renderer = builder.renderer

        # OUTPUT
        outputNode = vec4( outgoingLightNode, diffuseColorNode.a )

        # TONE MAPPING
        if renderer.toneMappingNode:
            outputNode = context( renderer.toneMappingNode, { 'color': outputNode } )

        # ENCODING
        outputNode = colorSpace( outputNode, renderer.outputEncoding )

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
