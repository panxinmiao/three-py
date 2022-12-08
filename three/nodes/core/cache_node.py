from .node import Node
from .node_cache import NodeCache

class CacheNode(Node):
    isCacheNode = True

    def __init__(self, node, cache=None) -> None:
        super().__init__()

        self.node = node
        self.cache = cache or NodeCache()

    def getNodeType(self, builder):
        return self.node.getNodeType(builder)
    
    def build(self, builder, *args):
        previousCache = builder.getCache()

        builder.setCache(self.cache)
        data = self.node.build(builder, *args)
        builder.setCache(previousCache)

        return data