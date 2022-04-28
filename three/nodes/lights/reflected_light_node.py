from ..core.temp_node import TempNode
from ..core.var_node import VarNode
from ..core.const_node import ConstNode
from ..math.operator_node import OperatorNode
from three import Vector3

class ReflectedLightNode(TempNode):

    def __init__(self) -> None:
        super().__init__('vec3')

        self.directDiffuse = VarNode( ConstNode( Vector3() ), 'DirectDiffuse' )
        self.directSpecular = VarNode( ConstNode( Vector3() ), 'DirectSpecular' )
        self.indirectDiffuse = VarNode( ConstNode( Vector3() ), 'IndirectDiffuse' )
        self.indirectSpecular = VarNode( ConstNode( Vector3() ), 'IndirectSpecular' )

    def generate(self, builder):
        totalLight = OperatorNode( '+', self.directDiffuse, self.directSpecular, self.indirectDiffuse, self.indirectSpecular )

        return totalLight.build( builder )