from .node_material import NodeMaterial
from .line_basic_node_material import LineBasicNodeMaterial
from .mesh_basic_node_material import MeshBasicNodeMaterial
from .mesh_standard_node_material import MeshStandardNodeMaterial
from .mesh_normal_node_material import MeshNormalNodeMaterial
from .points_node_material import PointsNodeMaterial

# __all__ = [ 
#     'MeshBasicNodeMaterial', 'MeshStandardNodeMaterial', 'PointsNodeMaterial', 'LineBasicNodeMaterial'
# ]

materialLib = {
    'NodeMaterial': NodeMaterial,
    'LineBasicNodeMaterial': LineBasicNodeMaterial,
    'MeshBasicNodeMaterial': MeshBasicNodeMaterial,
    'MeshStandardNodeMaterial': MeshStandardNodeMaterial,
    'PointsNodeMaterial': PointsNodeMaterial,
    'MeshNormalNodeMaterial': MeshNormalNodeMaterial

}

def fromType( type ):
    if type in materialLib:
        return materialLib[type]()

def fromMaterial( material ):
    type = material.type.replace( 'Material', 'NodeMaterial' )
    if not type in materialLib:
        return material # is already a node material or cannot be converted


    nodeMaterial = materialLib[ type ]( material )

    for key in material.__dict__:
        #if not key in nodeMaterial.__dict__:
        if not hasattr( nodeMaterial, key ):
            setattr(nodeMaterial, key, getattr(material, key))
            # nodeMaterial.__dict__[ key ] = material.__dict__[ key ]  # currently this is needed only for material.alphaTest

    return nodeMaterial