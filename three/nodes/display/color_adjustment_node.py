from ..core.temp_node import TempNode
from ..shadernode.shader_node import ShaderNode
from ..shadernode.shader_node_base_elements import (
    vec3, mat3, add, sub, mul, max, div, dot, float, mix, cos, sin, atan2, sqrt
)


def __luminance( inputs , *args):
    color = inputs['color']
    LUMA = vec3(0.2125, 0.7154, 0.0721)
    return dot(color, LUMA)

luminanceNode = ShaderNode(__luminance)


def __saturation( inputs , *args):
    color = inputs['color']
    adjustment = inputs['adjustment']
    intensityNode = luminanceNode.call({color})
    return mix(intensityNode, color, adjustment)

saturationNode = ShaderNode(__saturation)


def __vibrance( inputs , *args):
    color = inputs['color']
    adjustment = inputs['adjustment']

    average = div(add(color.r, color.g, color.b), 3.0)

    mx = max(color.r, max(color.g, color.b))
    amt = mul(sub(mx, average), mul(-3.0, adjustment))

    return mix(color.rgb, vec3(mx), amt)

vibranceNode = ShaderNode(__vibrance)


def __hue( inputs , *args):
    color = inputs['color']
    adjustment = inputs['adjustment']

    RGBtoYIQ = mat3(0.299, 0.587, 0.114, 0.595716, -0.274453, -0.321263, 0.211456, -0.522591, 0.311135)

    YIQtoRGB = mat3(1.0, 0.9563, 0.6210, 1.0, -0.2721, -0.6474, 1.0, -1.107, 1.7046)

    yiq = mul(RGBtoYIQ, color)

    hue = add(atan2(yiq.z, yiq.y), adjustment)
    chroma = sqrt(add(mul(yiq.z, yiq.z), mul(yiq.y, yiq.y)))

    return mul(YIQtoRGB, vec3(yiq.x, mul(chroma, cos(hue)), mul(chroma, sin(hue))))

hueNode = ShaderNode(__hue)


class ColorAdjustmentNode(TempNode):

    SATURATION = 'saturation'
    VIBRANCE = 'vibrance'
    HUE = 'hue'

    def __init__(self, method, colorNode, adjustmentNode=float(1)):
        super().__init__('vec3')
        
        self.method = method

        self.colorNode = colorNode
        self.adjustmentNode = adjustmentNode

    def construct(self):
        method = self.method
        colorNode = self.colorNode
        adjustmentNode = self.adjustmentNode

        callParams = {"color": colorNode, "adjustment": adjustmentNode}

        outputNode = None

        if method == ColorAdjustmentNode.SATURATION:
            outputNode = saturationNode.call(callParams)
        elif method == ColorAdjustmentNode.VIBRANCE:
            outputNode = vibranceNode.call(callParams)
        elif method == ColorAdjustmentNode.HUE:
            outputNode = hueNode.call(callParams)
        else:
            raise (f'{self.type}: Method "{ self.method }" not supported!')

        return outputNode
