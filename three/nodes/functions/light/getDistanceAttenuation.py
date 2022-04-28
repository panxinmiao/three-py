from ...shader.shader_node import ShaderNode
from ...shader.shader_node_elements import div, max, sub, mul, saturate, pow, pow2, pow4, cond, greaterThan

def __getDistanceAttenuation( inputs ):
    lightDistance = inputs['lightDistance']
    cutoffDistance = inputs['cutoffDistance']
    decayExponent = inputs['decayExponent']

    # based upon Frostbite 3 Moving to Physically-based Rendering
    # page 32, equation 26: E[window1]
    # https://seblagarde.files.wordpress.com/2015/07/course_notes_moving_frostbite_to_pbr_v32.pdf
    distanceFalloff = div( 1.0, max( pow( lightDistance, decayExponent ), 0.01 ) )

    return cond(
      greaterThan( cutoffDistance, 0 ),
      mul( distanceFalloff, pow2( saturate( sub( 1.0, pow4( div( lightDistance, cutoffDistance ) ) ) ) ) ),
      distanceFalloff
    )

getDistanceAttenuation = ShaderNode( __getDistanceAttenuation ); # validated