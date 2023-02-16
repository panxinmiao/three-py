from warnings import warn
from inspect import isfunction
from three.materials import ShaderMaterial
from three.constants import NoToneMapping
from ..core.stack_node import StackNode
from ..display.tone_mapping_node import ToneMappingNode
from ..core.node_utils import getCacheKey

from ..shadernode.shader_node_elements import (
    float, vec3, vec4,
    assign, mul, bypass, attribute, context, discard,
	positionLocal, diffuseColor, skinning, instance, modelViewProjection, lightingContext, colorSpace,
    normalize, cross, dFdx, dFdy, positionView,
	materialAlphaTest, materialColor, materialOpacity, materialEmissive, materialNormal, transformedNormalView,
	reference, rangeFog, densityFog)

class NodeMaterial(ShaderMaterial):

    isNodeMaterial = True

    def __init__(self, parameters = {}, **kwargs) -> None:
        super().__init__(parameters, **kwargs)
        self._type = self.__class__.__name__

        self.lights = True
        self.normals = True

        self.lightsNode = None

    def customProgramCacheKey(self):
        return getCacheKey( self )

    def build( self, builder ):
        self.construct( builder )

    def construct(self, builder):

        # < STACKS >
        vertexStack = StackNode()
        fragmentStack = StackNode()

        # < VERTEX STAGE >

        vertexStack.outputNode = self.constructPosition( builder, vertexStack )

        # < FRAGMENT STAGE >

        if self.normals is True:
            self.constructNormal( builder, fragmentStack )

        self.constructDiffuseColor( builder, fragmentStack )
        self.constructVariants( builder, fragmentStack )

        outgoingLightNode = self.constructLighting( builder, fragmentStack )
        fragmentStack.outputNode = self.constructOutput( builder, fragmentStack, outgoingLightNode, diffuseColor.a )

        # < FLOW >

        builder.addFlow( 'vertex', vertexStack )
        builder.addFlow( 'fragment', fragmentStack )

    def constructPosition(self, builder, stack):
        object = builder.object

        vertex = positionLocal

        if self.positionNode:
            vertex = bypass(vertex, assign(positionLocal, self.positionNode))

        if object.instanceMatrix and object.instanceMatrix.isInstancedBufferAttribute and builder.isAvailable('instance') == True:
            vertex = bypass( vertex, instance( object ) )

        if object.isSkinnedMesh == True:
            vertex = bypass( vertex, skinning( object ) )

        builder.context.vertex = vertex

        return modelViewProjection()

    def constructDiffuseColor(self, builder, stack):

        colorNode = vec4( self.colorNode or materialColor )
        opacityNode = float( self.opacityNode ) if self.opacityNode else materialOpacity

        # VERTEX COLORS
        if self.vertexColors is True and builder.geometry.hasAttribute( 'color' ):
            colorNode = vec4( mul( colorNode.xyz, attribute( 'color' ) ), colorNode.a )

        # COLOR
        stack.assign( diffuseColor, colorNode )

        # OPACITY
        stack.assign( diffuseColor.a, diffuseColor.a * opacityNode )

        # ALPHA TEST
        # if self.alphaTestNode or self.alphaTest > 0:
        #     alphaTestNode = float( self.alphaTestNode ) if self.alphaTestNode else materialAlphaTest
        #     stack.add( discard( diffuseColor.a <= alphaTestNode ) )

    
    def constructVariants(self, builder, stack):
        # Interface function
        pass
    
    def constructNormal(self, builder, stack):
        # NORMAL VIEW
        if self.flatShading:
            normalNode = normalize(cross(dFdx(positionView), dFdy(positionView)))
        else:
            normalNode =  vec3( self.normalNode ) if self.normalNode else materialNormal
        stack.assign( transformedNormalView, normalNode )
        return normalNode
    
    def constructLights(self, builder):
        return self.lightsNode or builder.lightsNode

        # envNode = self.envNode or builder.scene.environmentNode
        # materialLightsNode = []
        # envNode = self.envNode or builder.material.envMap or builder.scene.environmentNode or builder.scene.environment
        # if envNode:
        #     if envNode.isTexture:
        #         envNode = cubeTexture(envNode)
        #     materialLightsNode.append( EnvironmentNode( envNode ) )
        
        # if builder.material.aoMap:
        #     materialLightsNode.append( AONode( texture( builder.material.aoMap ) ) )

        # if len( materialLightsNode ) > 0:
        #     lightsNode = LightsNode( materialLightsNode + lightsNode.lightNodes )
        
        # return lightsNode
    
    def constructLightingModel( *args ):
        # Interface function.
        pass

    def constructLighting(self, builder, stack):
        material = builder.material

        # OUTGOING LIGHT

        lights = self.lights is True or self.lightsNode is not None

        lightsNode = self.constructLights( builder ) if lights else None
        lightingModelNode = self.constructLightingModel( builder ) if lightsNode else None

        outgoingLightNode = diffuseColor.xyz

        if lightingModelNode and lightsNode and lightsNode.hasLight is not False:
            outgoingLightNode = lightingContext( lightsNode, lightingModelNode )

        # EMISSIVE
        if (self.emissiveNode and self.emissiveNode.isNode) or (material.emissive and material.emissive.isColor):
            outgoingLightNode = outgoingLightNode + vec3( self.emissiveNode or materialEmissive )
        
        return outgoingLightNode

    def constructOutput( self, builder, stack, outgoingLight, opacity ):
        renderer = builder.renderer

        # TONE MAPPING
        toneMappingNode = renderer.toneMappingNode

        if not toneMappingNode and renderer.toneMapping != NoToneMapping:
            toneMappingNode = ToneMappingNode( renderer.toneMapping, reference( 'toneMappingExposure', 'float', renderer ), outgoingLight )

        if renderer.toneMappingNode and renderer.toneMappingNode.isNode:
            outgoingLight = context(toneMappingNode, {'color': outgoingLight})

        outputNode = vec4( outgoingLight, opacity )

        # ALPHA TEST 
        # TODO: move to constructDiffuseColor when uniformity analysis updated in naga
        # See: https://github.com/gfx-rs/naga/issues/1744
        if self.alphaTestNode or self.alphaTest > 0:
            alphaTestNode = float( self.alphaTestNode ) if self.alphaTestNode else materialAlphaTest
            stack.add( discard( outputNode.a <= alphaTestNode ) )

        # ENCODING
        outputNode = colorSpace( outputNode, renderer.outputEncoding )

        # FOG

        fogNode = builder.fogNode

        if (fogNode is None or fogNode.isNode != True) and builder.scene.fog:
            fog = builder.scene.fog
            if fog.isFogExp2:
                fogNode = densityFog( reference( 'color', 'color', fog ), reference( 'density', 'float', fog ) )
            elif fog.isFog:
                fogNode = rangeFog( reference( 'color', 'color', fog ), reference( 'near', 'float', fog ), reference( 'far', 'float', fog ) )
            else:
                warn(f'THREE.NodeMaterial: Unsupported fog configuration. {fog}')

        if fogNode:
            outputNode = vec4( vec3( fogNode.mix( outputNode ) ), outputNode.w )
        
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
