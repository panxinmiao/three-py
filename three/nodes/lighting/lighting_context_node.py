from ..core.context_node import ContextNode
from ..shader.shader_node_base_elements import float, vec3, add, temp

class LightingContextNode(ContextNode):

    def __init__(self, node, lightingModelNode = None ) -> None:
        super().__init__(node)
        self.lightingModelNode = lightingModelNode

    def getNodeType(self, *args ):
        return 'vec3'

    def generate( self, builder ):

        lightingModelNode = self.lightingModelNode
        context = self.context

        if context.reflectedLight is None:
            directDiffuse = temp(vec3())
            directSpecular = temp(vec3())
            indirectDiffuse = temp(vec3())
            indirectSpecular = temp(vec3())

            context.reflectedLight = {
                "directDiffuse": directDiffuse,
                "directSpecular": directSpecular,
                "indirectDiffuse": indirectDiffuse,
                "indirectSpecular": indirectSpecular,
                "total": add(directDiffuse, directSpecular,indirectDiffuse, indirectSpecular)
            }

            context.radiance = temp(vec3())
            context.irradiance = temp(vec3())
            context.iblIrradiance = temp(vec3())
            context.ambientOcclusion = temp(float(1))

        context.lightingModelNode = lightingModelNode or context.lightingModelNode


        type = self.getNodeType( builder )

        super().generate( builder, type )

        if lightingModelNode and lightingModelNode.indirectDiffuse:
            lightingModelNode.indirectDiffuse.call(context)
        
        if lightingModelNode and lightingModelNode.indirectSpecular:
            lightingModelNode.indirectSpecular.call(context)
        
        if lightingModelNode and lightingModelNode.ambientOcclusion:
            lightingModelNode.ambientOcclusion.call(context)

        return context.reflectedLight.total.build( builder, type )


