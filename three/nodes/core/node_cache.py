from weakref import WeakKeyDictionary

_id = 0

class NodeCache:

    def __init__(self) -> None:
        global _id
        self.id = _id
        _id += 1
        self.nodesData = WeakKeyDictionary()
    
    def getNodeData(self, node):
        return self.nodesData.get(node, None)
    
    def setNodeData(self, node, data):
        self.nodesData[node] = data