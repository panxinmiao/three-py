from ..core.context_node import ContextNode
from ..shadernode.shader_node_base_elements import float, vec3, add, temp
from three.structure import Dict

class LightingContextNode(ContextNode):

    def __init__(self, node, lightingModelNode = None ) -> None:
        super().__init__(node)
        self.lightingModelNode = lightingModelNode

    def getNodeType(self, *args ):
        return 'vec3'

    def construct( self, builder ):
        lightingModelNode = self.lightingModelNode
        self.context = Dict()  # reset context
        context = self.context
        properties = builder.getNodeProperties( self )

        directDiffuse = temp(vec3())
        directSpecular = temp(vec3())
        indirectDiffuse = temp(vec3())
        indirectSpecular = temp(vec3())
        total = add( directDiffuse, directSpecular, indirectDiffuse, indirectSpecular )

        reflectedLight = {
            "directDiffuse": directDiffuse,
            "directSpecular": directSpecular,
            "indirectDiffuse": indirectDiffuse,
            "indirectSpecular": indirectSpecular,
            "total": total
        }

        lighting = {
            "radiance": temp(vec3()),
            "irradiance": temp(vec3()),
            "iblIrradiance": temp(vec3()),
            "ambientOcclusion": temp(float(1))
        }

        properties.update( reflectedLight )
        properties.update( lighting )
        context.update( lighting )

        context.reflectedLight = reflectedLight
        context.lightingModelNode = lightingModelNode or context.lightingModelNode

        if lightingModelNode and lightingModelNode.indirectDiffuse:
            lightingModelNode.indirectDiffuse.call(context)
        
        if lightingModelNode and lightingModelNode.indirectSpecular:
            lightingModelNode.indirectSpecular.call(context)
        
        if lightingModelNode and lightingModelNode.ambientOcclusion:
            lightingModelNode.ambientOcclusion.call(context)

        return super().construct(builder)

    def generate( self, builder ):
        context = self.context
        type = self.getNodeType( builder )

        super().generate( builder, type )
        return context.reflectedLight.total.build( builder, type )


