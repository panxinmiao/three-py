# accssors
from ..accessors.cube_texture_node import CubeTextureNode
from ..accessors.instance_node import InstanceNode
from ..accessors.reflect_vector_node import ReflectVectorNode
from ..accessors.refract_vector_node import RefractVectorNode
from ..accessors.skinning_node import SkinningNode
from ..accessors.extended_material_node import ExtendedMaterialNode

# display
from ..display.blend_mode_node import BlendModeNode
from ..display.color_adjustment_node import ColorAdjustmentNode
from ..display.color_space_node import ColorSpaceNode
from ..display.normal_map_node import NormalMapNode
from ..display.tone_mapping_node import ToneMappingNode
from ..display.viewport_node import ViewportNode

# lighting
from ..lighting.lights_node import LightsNode
from ..lighting.lighting_context_node import LightingContextNode

# utils
from ..utils.matcap_uv_node import MatcapUVNode
from ..utils.equirect_uv_node import EquirectUVNode
from ..utils.osc_node import OscNode
from ..utils.remap_node import RemapNode
from ..utils.rotate_uv_node import RotateUVNode
from ..utils.specular_mip_level_node import SpecularMipLevelNode
from ..utils.sprite_sheet_uv_node import SpriteSheetUVNode
from ..utils.timer_node import TimerNode
from ..utils.triplanar_textures_node import TriplanarTexturesNode
from ..utils.packing_node import PackingNode

# geometry
from ..geometry.range_node import RangeNode

# procedural
from ..procedural.checker_node import CheckerNode

# fog
from ..fog.fog_node import FogNode
from ..fog.fog_range_node import FogRangeNode
from ..fog.fog_exp2_node import FogExp2Node

from .shader_node import nodeObject, nodeProxy, nodeImmutable

from .shader_node_base_elements import *

# accessors

cubeTexture = nodeProxy(CubeTextureNode)
instance = nodeProxy(InstanceNode)
reflectVector = nodeImmutable(ReflectVectorNode)
refractVector = nodeImmutable(RefractVectorNode)
skinning = nodeProxy(SkinningNode)

# material

materialNormal = nodeImmutable(ExtendedMaterialNode, ExtendedMaterialNode.NORMAL)

# diaplay

burn = nodeProxy(BlendModeNode, BlendModeNode.BURN)
dodge = nodeProxy(BlendModeNode, BlendModeNode.DODGE)
overlay = nodeProxy(BlendModeNode, BlendModeNode.OVERLAY)
screen = nodeProxy(BlendModeNode, BlendModeNode.SCREEN)

saturation = nodeProxy(ColorAdjustmentNode, ColorAdjustmentNode.SATURATION)
vibrance = nodeProxy(ColorAdjustmentNode, ColorAdjustmentNode.VIBRANCE)
hue = nodeProxy(ColorAdjustmentNode, ColorAdjustmentNode.HUE)

colorSpace = lambda node, encoding : nodeObject( ColorSpaceNode( None, nodeObject( node ) ).fromEncoding( encoding ) )
normalMap = nodeProxy(NormalMapNode)
toneMapping =lambda mapping, exposure, color : nodeObject(ToneMappingNode(mapping, nodeObject(exposure), nodeObject(color)))

viewportCoordinate = nodeImmutable(ViewportNode, ViewportNode.COORDINATE)
viewportResolution = nodeImmutable(ViewportNode, ViewportNode.RESOLUTION)
viewportTopLeft = nodeImmutable(ViewportNode, ViewportNode.TOP_LEFT)
viewportBottomLeft = nodeImmutable(ViewportNode, ViewportNode.BOTTOM_LEFT)
viewportTopRight = nodeImmutable(ViewportNode, ViewportNode.TOP_RIGHT)
viewportBottomRight = nodeImmutable(ViewportNode, ViewportNode.BOTTOM_RIGHT)

# lighting

lights = lambda lights: nodeObject(LightsNode().fromLights(lights))
lightingContext = nodeProxy(LightingContextNode)

# utils

matcapUV = nodeImmutable(MatcapUVNode)
equirectUV = nodeProxy(EquirectUVNode)
specularMipLevel = nodeProxy(SpecularMipLevelNode)

oscSine = nodeProxy(OscNode, OscNode.SINE)
oscSquare = nodeProxy(OscNode, OscNode.SQUARE)
oscTriangle = nodeProxy(OscNode, OscNode.TRIANGLE)
oscSawtooth = nodeProxy(OscNode, OscNode.SAWTOOTH)

remap = nodeProxy(RemapNode, None, None, {'doClamp': False})
remapClamp = nodeProxy(RemapNode)

rotateUV = nodeProxy( RotateUVNode )

spritesheetUV = nodeProxy(SpriteSheetUVNode)

timerLocal = lambda timeScale, value=0 : nodeObject( TimerNode( TimerNode.LOCAL, timeScale, value ) )
timerGlobal = lambda timeScale, value=0 : nodeObject( TimerNode( TimerNode.GLOBAL, timeScale, value ) )
timerDelta = lambda timeScale, value=0 : nodeObject( TimerNode( TimerNode.DELTA, timeScale, value ) )
frameId = nodeImmutable( TimerNode, TimerNode.FRAME )

triplanarTextures = nodeProxy( TriplanarTexturesNode )
triplanarTexture = lambda texture, *args, **kwargs: triplanarTextures( texture, texture, texture, *args, **kwargs )

directionToColor = nodeProxy( PackingNode, PackingNode.DIRECTION_TO_COLOR )
colorToDirection = nodeProxy( PackingNode, PackingNode.COLOR_TO_DIRECTION )

# geometry

range = lambda min, max: nodeObject( RangeNode( min, max ) )

# procedural

checker = nodeProxy( CheckerNode )

# fog

fog = nodeProxy( FogNode )
rangeFog = nodeProxy( FogRangeNode )
densityFog = nodeProxy( FogExp2Node )