import math
from ..core.node import Node
from ..core.constants import NodeUpdateType

class ComputeNode(Node):

    def __init__(self, computeNode, count, workgroupSize=None) -> None:
        super().__init__('void')

        self.computeNode = computeNode

        self.count = count
        self.workgroupSize = workgroupSize or [64]
        self.dispatchCount = 0

        self.updateType = NodeUpdateType.Object

        self.updateDispatchCount()

    def updateDispatchCount(self):

        size = self.workgroupSize[0]

        for i in range (1, len(self.workgroupSize)):
            size *= self.workgroupSize[i]
        self.dispatchCount = math.ceil(self.count / size)

    def update(self, params):
        renderer = params['renderer']
        renderer.compute(self)


    def generate(self, builder):
        shaderStage = builder.shaderStage
        if shaderStage == 'compute':
            snippet = self.computeNode.build(builder, 'void')

            if snippet != '':
                builder.addFlowCode(snippet)

