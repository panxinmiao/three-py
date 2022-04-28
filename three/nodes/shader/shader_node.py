
from .shader_node_utils import shader_node_objects, shader_node_object
from three.structure import Dict

# def shader_node_object(obj):
#     if isinstance(obj, int) or isinstance(obj, float):
#         return shader_node_object( FloatNode( obj ).setConst( True ) )
#     elif isinstance(obj, object):
#         if isinstance(obj, Node) and not isinstance(obj, ProxyNode):

#             return ProxyNode(obj)


class ShaderNode:
    def __init__(self, func) -> None:
        if not callable(func):
            raise ValueError("ShaderNode func must be callable")
        self.func = func
        
    def __call__(self, *args, **kwds):
        if args:
            inputs = args[0]
            shader_node_objects(inputs)

            return shader_node_object(self.func(Dict(inputs), *args[1:], **kwds))
        else:
            return shader_node_object(self.func(*args, **kwds))


    