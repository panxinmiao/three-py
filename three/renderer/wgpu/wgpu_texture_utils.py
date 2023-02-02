from .constants import GPUTextureViewDimension, GPUIndexFormat, GPUFilterMode, GPUPrimitiveTopology, GPULoadOp, GPUStoreOp
import wgpu


class WgpuTextureUtils:

    def __init__(self, device: 'wgpu.GPUDevice') -> None:
        
        self.device = device

        mipmapVertexSource = '''
struct VarysStruct {
    @builtin( position ) Position: vec4<f32>,
    @location( 0 ) vTex : vec2<f32>
};
@vertex
fn main( @builtin( vertex_index ) vertexIndex : u32 ) -> VarysStruct {
    var Varys : VarysStruct;
    var pos = array< vec2<f32>, 4 >(
        vec2<f32>( -1.0,  1.0 ),
        vec2<f32>(  1.0,  1.0 ),
        vec2<f32>( -1.0, -1.0 ),
        vec2<f32>(  1.0, -1.0 )
    );
    var tex = array< vec2<f32>, 4 >(
        vec2<f32>( 0.0, 0.0 ),
        vec2<f32>( 1.0, 0.0 ),
        vec2<f32>( 0.0, 1.0 ),
        vec2<f32>( 1.0, 1.0 )
    );
    Varys.vTex = tex[ vertexIndex ];
    Varys.Position = vec4<f32>( pos[ vertexIndex ], 0.0, 1.0 );
    return Varys;
}
'''

        mipmapFragmentSource = '''
@group( 0 ) @binding( 0 )
var imgSampler : sampler;

@group( 0 ) @binding( 1 )
var img : texture_2d<f32>;

@fragment
fn main( @location( 0 ) vTex : vec2<f32> ) -> @location( 0 ) vec4<f32> {
    return textureSample( img, imgSampler, vTex );
}
'''

        self.sampler = device.create_sampler(min_filter = GPUFilterMode.Linear)

        # We'll need a new pipeline for every texture format used.
        self.pipelines = {}

        self.mipmapVertexShaderModule = device.create_shader_module(code = mipmapVertexSource)

        self.mipmapFragmentShaderModule = device.create_shader_module(code = mipmapFragmentSource)

    
    def getMipmapPipeline( self, format ) -> 'wgpu.GPURenderPipeline':

        pipeline = self.pipelines.get(format, None)

        if pipeline is None:

            pipeline = self.device.create_render_pipeline(
                layout=self._create_pipeline_layout(),
                vertex= {
                    'module': self.mipmapVertexShaderModule,
                    'entry_point': 'main',
                    'buffers': []
                },
                fragment={
                    'module': self.mipmapFragmentShaderModule,
                    'entry_point': 'main',
                    'targets': [ { 'format':  format} ]
                },
                primitive={
                    'topology': GPUPrimitiveTopology.TriangleStrip,
                    'strip_index_format': GPUIndexFormat.Uint32
                }
            )

            self.pipelines[ format ] = pipeline


        return pipeline

    
    def _create_pipeline_layout(self):
        bind_group_layouts = []

        entries = []
        entries.append({
            'binding': 0,
            'visibility': wgpu.ShaderStage.FRAGMENT,
            "sampler": {
                "type": "filtering"
            }
        })

        entries.append({
            'binding': 1,
            'visibility': wgpu.ShaderStage.FRAGMENT,
            "texture": {
                "multisampled": False
            }
        })

        bind_group_layout = self.device.create_bind_group_layout(
            entries=entries)
        bind_group_layouts.append(bind_group_layout)
        pipeline_layout = self.device.create_pipeline_layout(
            bind_group_layouts=bind_group_layouts)
        return pipeline_layout

    
    def generateMipmaps( self, textureGPU:'wgpu.GPUTexture', textureGPUDescriptor, baseArrayLayer = 0 ):
        
        pipeline = self.getMipmapPipeline( textureGPUDescriptor.format )

        commandEncoder:'wgpu.GPUCommandEncoder' = self.device.create_command_encoder()
        # bindGroupLayout = pipeline.getBindGroupLayout( 0 ); # @TODO: Consider making this static.
        bindGroupLayout = pipeline.get_bind_group_layout(0)

        srcView = textureGPU.create_view(
            base_mip_level=0,
            mip_level_count=1,
            dimension = GPUTextureViewDimension.TwoD,
            base_array_layer=baseArrayLayer
        )


        for i in range(1, textureGPUDescriptor.mip_level_count):

            dstView = textureGPU.create_view(
                base_mip_level= i,
                mip_level_count= 1,
                dimension=GPUTextureViewDimension.TwoD,
                base_array_layer = baseArrayLayer)

            passEncoder:'wgpu.GPURenderPassEncoder' = commandEncoder.begin_render_pass(color_attachments=[{
                'view': dstView,
                'load_op': GPULoadOp.Clear,
                'store_op': GPUStoreOp.Store,
                'clear_value': [ 0, 0, 0, 0 ]
            }])

            bindGroup = self.device.create_bind_group(
                layout=bindGroupLayout,
                entries=[{
                    'binding': 0,
                    'resource': self.sampler
                },{
                    'binding': 1,
                    'resource': srcView
                }]

            )

            passEncoder.set_pipeline( pipeline )
            passEncoder.set_bind_group( 0, bindGroup, [], 0, 99 )
            passEncoder.draw( 4, 1, 0, 0 )
            passEncoder.end()
            
            srcView = dstView

        self.device.queue.submit( [ commandEncoder.finish() ] )


