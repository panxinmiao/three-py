import wgpu
import wgpu.backends.rs

#from wgpu import GPUAdapter, GPUDevice, GPUCanvasContext, GPUShaderModule

from wgpu.gui.auto import WgpuCanvas, run

import numpy as np

from three import Matrix4

triangle_vertex = np.array( [

    0.0,  1.0,  0.0,
   -1.0, -1.0,  0.0,
    1.0, -1.0,  0.0

])

triangle_index = np.array( [ 0, 1, 2 ] )

triangle_mVMatrix = Matrix4().makeTranslation( -1.5, 0.0, -7.0 )

square_vertex = np.array( [

     1.0,  1.0,  0.0,
    -1.0,  1.0,  0.0,
     1.0, -1.0,  0.0,
    -1.0, -1.0,  0.0

])

square_index = np.array( [ 0, 1, 2, 1, 2, 3 ] )

square_mVMatrix = Matrix4().makeTranslation( 1.5, 0.0, -7.0 )


shader_source = """
struct VertexInput {
    [[builtin(vertex_index)]] vertex_index : u32;
};
struct VertexOutput {
    [[location(0)]] color : vec4<f32>;
    [[builtin(position)]] pos: vec4<f32>;
};
[[stage(vertex)]]
fn vs_main(in: VertexInput) -> VertexOutput {
    var positions = array<vec2<f32>, 3>(vec2<f32>(0.0, -0.5), vec2<f32>(0.5, 0.5), vec2<f32>(-0.5, 0.7));
    let index = i32(in.vertex_index);
    let p: vec2<f32> = positions[index];
    var out: VertexOutput;
    out.pos = vec4<f32>(p, 0.0, 1.0);
    out.color = vec4<f32>(p, 0.5, 1.0);
    return out;
}
[[stage(fragment)]]
fn fs_main(in: VertexOutput) -> [[location(0)]] vec4<f32> {
    return in.color;
}
"""

# shader_source = """
# struct Uniforms {
#     [[size(64)]]uPMatrix: mat4x4<f32>;
#     [[size(64)]]uMVMatrix: mat4x4<f32>;
# };

# [[group(0), binding(0)]]
# var<uniform> uniforms: Uniforms;

# [[stage(vertex)]]
# fn vs_main ([[location(0)]] aVertexPosition : vec3<f32>) -> [[builtin(position)]] vec4<f32> {
#     return uniforms.uPMatrix * uniforms.uMVMatrix * vec4<f32>(aVertexPosition, 1.0);
# }

# [[stage(fragment)]]
# fn fs_main() -> [[location(0)]] vec4<f32> {
#     return vec4<f32>(1.0, 1.0, 1.0, 1.0);
# }
# """

canvas = WgpuCanvas(size=(640, 480), title="wgpu triangle")
adapter:wgpu.GPUAdapter = wgpu.request_adapter(canvas = canvas)

device:wgpu.GPUDevice = adapter.request_device()

context:wgpu.GPUCanvasContext = canvas.get_context()
render_texture_format:wgpu.TextureFormat = context.get_preferred_format(device.adapter)
context.configure(device=device, format=render_texture_format)

shader:wgpu.GPUShaderModule = device.create_shader_module(code=shader_source)

render_pipeline = device.create_render_pipeline(
    layout= device.create_pipeline_layout(bind_group_layouts=[]),
    vertex={
        "module": shader,
        "entry_point": "vs_main",
        "buffers": [],
    },
    primitive={
        "topology": wgpu.PrimitiveTopology.triangle_list,
        "front_face": wgpu.FrontFace.ccw,
        "cull_mode": wgpu.CullMode.none,
    },
    depth_stencil=None,
    multisample=None,
    fragment={
        "module": shader,
        "entry_point": "fs_main",
        "targets": [
            {
                "format": render_texture_format,
                "blend": {
                    "color": (
                        wgpu.BlendFactor.one,
                        wgpu.BlendFactor.zero,
                        wgpu.BlendOperation.add,
                    ),
                    "alpha": (
                        wgpu.BlendFactor.one,
                        wgpu.BlendFactor.zero,
                        wgpu.BlendOperation.add,
                    ),
                },
            },
        ],
    },
)

def draw_frame():
    current_texture_view = context.get_current_texture()
    command_encoder:wgpu.GPUCommandEncoder = device.create_command_encoder()

    render_pass:wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
        color_attachments=[
            {
                "view": current_texture_view,
                "resolve_target": None,
                "load_value": (0, 0, 0, 1),  # LoadOp.load or color
                "store_op": wgpu.StoreOp.store,
            }
        ],
    )

    render_pass.set_pipeline(render_pipeline)
    # render_pass.set_bind_group(0, no_bind_group, [], 0, 1)
    render_pass.draw(3, 1, 0, 0)
    render_pass.end_pass()
    device.queue.submit([command_encoder.finish()])

canvas.request_draw(draw_frame)

run()