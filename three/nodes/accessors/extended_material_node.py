from .material_node import MaterialNode
from ..display.normal_map_node import NormalMapNode
from ..shadernode.shader_node_base_elements import materialReference, normalView

class ExtendedMaterialNode(MaterialNode):

    NORMAL= 'normal'

    def __init__(self, scope) -> None:
        super().__init__(scope)

    def getNodeType(self, builder):
        scope = self.scope
        type = None
        if scope == ExtendedMaterialNode.NORMAL:
            type = 'vec3'

        return type or super().getNodeType(builder)

    def construct(self, builder):
        material = builder.material
        scope = self.scope

        node = None
        if scope == ExtendedMaterialNode.NORMAL:
            if material.normalMap is not None:
                node = NormalMapNode(self.getTexture( 'normalMap' ), materialReference( 'normalScale', 'vec2' ))
            else:
                node = normalView

        return node or super().construct(builder)