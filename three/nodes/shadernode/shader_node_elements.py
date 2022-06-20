# accssors
from ..accessors.cube_texture_node import CubeTextureNode
from ..accessors.instance_node import InstanceNode
from ..accessors.reflect_node import ReflectNode
from ..accessors.skinning_node import SkinningNode

# display
from ..display.color_adjustment_node import ColorAdjustmentNode
from ..display.color_space_node import ColorSpaceNode
from ..display.normal_map_node import NormalMapNode
from ..display.tone_mapping_node import ToneMappingNode

# lighting
from ..lighting.lights_node import LightsNode
from ..lighting.lighting_context_node import LightingContextNode

# utils
from ..utils.matcap_uv_node import MatcapUVNode
from ..utils.max_mip_level_node import MaxMipLevelNode
from ..utils.osc_node import OscNode
from ..utils.sprite_sheet_uv_node import SpriteSheetUVNode
from ..utils.timer_node import TimerNode

# geometry
from ..geometry.range_node import RangeNode

# procedural
from ..procedural.checker_node import CheckerNode

# fog
from ..fog.fog_node import FogNode
from ..fog.fog_range_node import FogRangeNode

from .shader_node import nodeObject, nodeProxy, nodeImmutable

from .shader_node_base_elements import *

# accessors

cubeTexture = nodeProxy( CubeTextureNode )
instance = nodeProxy(InstanceNode)
reflectVector = nodeImmutable(ReflectNode, ReflectNode.VECTOR)
reflectCube = nodeImmutable(ReflectNode, ReflectNode.CUBE)
skinning = nodeProxy(SkinningNode)

# diaplay

saturation = nodeProxy(ColorAdjustmentNode, ColorAdjustmentNode.SATURATION)
vibrance = nodeProxy(ColorAdjustmentNode, ColorAdjustmentNode.VIBRANCE)
hue = nodeProxy(ColorAdjustmentNode, ColorAdjustmentNode.HUE)

colorSpace = lambda node, encoding : nodeObject( ColorSpaceNode( None, nodeObject( node ) ).fromEncoding( encoding ) )
normalMap = nodeProxy(NormalMapNode)
toneMapping =lambda mapping, exposure, color : nodeObject(ToneMappingNode(mapping, nodeObject(exposure), nodeObject(color)))

# lighting

lights = lambda lights: nodeObject(LightsNode().fromLights(lights))
lightingContext = nodeProxy(LightingContextNode)

# utils

matcapUV = nodeImmutable(MatcapUVNode)
maxMipLevel = nodeProxy(MaxMipLevelNode)

oscSine = nodeProxy(OscNode, OscNode.SINE)
oscSquare = nodeProxy(OscNode, OscNode.SQUARE)
oscTriangle = nodeProxy(OscNode, OscNode.TRIANGLE)
oscSawtooth = nodeProxy(OscNode, OscNode.SAWTOOTH)

spritesheetUV = nodeProxy(SpriteSheetUVNode)

timerLocal = lambda timeScale : nodeObject( TimerNode( TimerNode.LOCAL, timeScale ) )
timerGlobal = lambda timeScale : nodeObject( TimerNode( TimerNode.GLOBAL, timeScale ) )
timerDelta = lambda timeScale : nodeObject( TimerNode( TimerNode.DELTA, timeScale ) )

# geometry

range = lambda min, max: nodeObject( RangeNode( min, max ) )

# procedural

checker = nodeProxy( CheckerNode )

# fog

fog = nodeProxy( FogNode )
rangeFog = nodeProxy( FogRangeNode )