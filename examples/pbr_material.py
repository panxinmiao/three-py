import imageio
import numpy as np
import three
import three.nodes
import trimesh
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run


def load_rgbm16_cube_texture(path, urls):
    def rgbm_to_rgba(data: np.ndarray):
        data = data.astype(np.float32)/255
        data = data * data[:, :, 3:4]*16
        data[:, :, 3] = 1
        return data


    images = []
    for url in urls:
        data = imageio.imread(path / url, format='png')
        data = rgbm_to_rgba(data)
        image = three.Image(memoryview(
            data), width=data.shape[1], height=data.shape[0])
        images.append(image)


    cubeTexture = three.CubeTexture(images)
    cubeTexture.type = three.FloatType
    cubeTexture.generateMipmaps = True
    cubeTexture.minFilter = three.LinearMipmapLinearFilter
    cubeTexture.format = three.RGBAFormat
    cubeTexture.needsUpdate = True

    return cubeTexture


def load_gltf(path):

    def __parse_texture(pil_image, encoding=three.LinearEncoding):
        if pil_image is None:
            return None
        pil_image = pil_image.convert(mode='RGBA')
        data = pil_image.tobytes()
        image = three.Image(memoryview(data), width=pil_image.size[0], height=pil_image.size[1])
        tex = three.Texture(image, format=three.RGBAFormat)
        tex.wrapS = three.RepeatWrapping
        tex.wrapT = three.RepeatWrapping
        tex.encoding = encoding
        tex.flipY = False
        tex.updateMatrix()
        tex.generateMipmaps = True
        tex.needsUpdate = True
        return tex


    def __parse_material(pbrmaterial):
        material = three.MeshStandardMaterial()
        material.map = __parse_texture(
            pbrmaterial.baseColorTexture, encoding=three.sRGBEncoding)

        material.emissive = three.Color(*pbrmaterial.emissiveFactor)
        material.emissiveMap = __parse_texture(
            pbrmaterial.emissiveTexture, encoding=three.sRGBEncoding)

        metallicRoughnessMap = __parse_texture(pbrmaterial.metallicRoughnessTexture)
        if pbrmaterial.roughnessFactor:
            material.roughness = pbrmaterial.roughnessFactor
        else:
            material.roughness = 1.0
        material.roughnessMap = metallicRoughnessMap

        if pbrmaterial.metallicFactor:
            material.metalness = pbrmaterial.metallicFactor
        else:
            material.metalness = 1.0
        material.metalnessMap = metallicRoughnessMap

        material.normalMap = __parse_texture(pbrmaterial.normalTexture)
        material.normalScale = three.Vector2(1, -1)

        material.aoMap = __parse_texture(pbrmaterial.occlusionTexture)
        material.aoMapIntensity = 1.0

        material.toneMapped = True
        material.side = three.FrontSide

        material.needsUpdate = True
        return material


    def parse_mesh(mesh):
        geometry = three.BufferGeometry()

        vertices = mesh.vertices.flatten()
        geometry.setAttribute(
            'position', three.Float32BufferAttribute(vertices, 3))

        normals = mesh.vertex_normals.flatten()
        geometry.setAttribute('normal', three.Float32BufferAttribute(normals, 3))

        geometry.setIndex(mesh.faces.flatten().tolist())

        visual = mesh.visual
        uv = visual.uv
        uv = uv * np.array([1, -1]) + np.array([0, 1])   # uv.y = 1 - uv.y
        geometry.setAttribute('uv', three.Float32BufferAttribute(uv.flatten(), 2))
        material = __parse_material(visual.material)
        return three.Mesh(geometry, material)


    helmet = trimesh.load(path)
    for node_name in helmet.graph.nodes_geometry:
        transform, geometry_name = helmet.graph[node_name]
        current = helmet.geometry[geometry_name]
        current.apply_transform(transform)

    meshes = list(helmet.geometry.values())
    meshes = [parse_mesh(m) for m in meshes]
    return meshes


def init_scene():

    canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

    render = three.WgpuRenderer(canvas, parameters={'antialias': True})
    render.init()

    camera = three.PerspectiveCamera(45, 640 / 480, 0.25, 20)
    camera.position.set(- 1.8, 0.6, 2.7)

    scene = three.Scene()

    env_text_path = Path(__file__).parent / "textures" / "cube" / "pisaRGBM16"
    env_text_urls = ['px.png', 'nx.png','py.png', 'ny.png', 'pz.png', 'nz.png']

    env_texture = load_rgbm16_cube_texture(env_text_path, env_text_urls)

    scene.environmentNode = three.nodes.CubeTextureNode(env_texture)

    # scene.background = env_texture

    gltf_path = Path(__file__).parent / "models" / "DamagedHelmet" / "glTF" / "DamagedHelmet.gltf"
    meshes = load_gltf(gltf_path)
    scene.add(*meshes)

    render.toneMappingNode = three.nodes.ToneMappingNode(three.LinearToneMapping, 1)
    render.outputEncoding = three.sRGBEncoding

    three.OrbitControls(camera, canvas)

    def on_resize(event):
        camera.aspect = event['width'] / event['height']
        camera.updateProjectionMatrix()

    canvas.add_event_handler(on_resize, 'resize')

    def loop():
        render.render(scene, camera)

    render.setAnimationLoop(loop)


if __name__ == "__main__":
    init_scene()
    run()
