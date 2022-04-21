from ..core.node import Node


class InstanceNode(Node):

    def __init__(self, instanceMesh ) -> None:
        from ..shader.shader_node_elements import vec3, mat3, mul, assign, buffer, element, dot, div, temp, instanceIndex, positionLocal, normalLocal
        super().__init__('void')
        self.instanceMesh = instanceMesh

        instanceBufferNode = buffer( instanceMesh.instanceMatrix.array, 'mat4', instanceMesh.count )
        self.instanceMatrixNode = temp( element( instanceBufferNode, instanceIndex ) )

    def generate(self, builder):
        from ..shader.shader_node_elements import vec3, mat3, mul, assign, buffer, element, dot, div, temp, instanceIndex, positionLocal, normalLocal
        instanceMatrixNode = self.instanceMatrixNode

        # POSITION

        instancePosition = mul( instanceMatrixNode, positionLocal ).xyz

		# NORMAL
        m = mat3( instanceMatrixNode[ 0 ].xyz, instanceMatrixNode[ 1 ].xyz, instanceMatrixNode[ 2 ].xyz )
        transformedNormal = div( normalLocal, vec3( dot( m[ 0 ], m[ 0 ] ), dot( m[ 1 ], m[ 1 ] ), dot( m[ 2 ], m[ 2 ] ) ) )
        instanceNormal = mul( m, transformedNormal ).xyz

        # ASSIGNS
        assign( positionLocal, instancePosition ).build( builder )
        assign( normalLocal, instanceNormal ).build( builder )