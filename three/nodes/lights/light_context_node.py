# from three.renderer.nodes import ContextNode, VarNode, Vector3Node, OperatorNode, PhysicalLightingModel

from ..core.context_node import ContextNode

class LightContextNode(ContextNode):

    def __init__(self, node, lightingModelNode = None ) -> None:
        super().__init__(node)
        self.lightingModelNode = lightingModelNode

    def getNodeType(self, *args ):
        return 'vec3'

    def generate( self, builder ):
        from ..shader.shader_node_elements import reflectedLight

        lightingModelNode = self.lightingModelNode

        self.context.reflectedLight = reflectedLight()

        if lightingModelNode is not None:
            self.context.lightingModelNode = lightingModelNode

        # directDiffuse = VarNode( UniformNode( Vector3() ), 'DirectDiffuse', 'vec3' )
        # directSpecular = VarNode( UniformNode( Vector3() ), 'DirectSpecular', 'vec3' )

        # self.context.directDiffuse = directDiffuse
        # self.context.directSpecular = directSpecular

        # if lightingModel:
        #     self.context.lightingModel = lightingModel


        type = self.getNodeType( builder )

        super().generate( builder, type )

        # totalLight = OperatorNode( '+', directDiffuse, directSpecular )

        # return totalLight.build( builder, type )
        return self.context.reflectedLight.build( builder, type )


