import three
from pathlib import Path

class Loader:
    # TODO cache
    def __init__(self, path=''):
        self.path = path

    def _parseMaterial(self, trimaterial):
        from trimesh.visual.material import PBRMaterial, SimpleMaterial

        if isinstance(trimaterial, SimpleMaterial):
            return self._parseBasicMaterial(trimaterial)
        elif isinstance(trimaterial, PBRMaterial):
            return self._parsePBRMaterial(trimaterial)
        else:
            raise NotImplementedError()
       
    
    def _parseBasicMaterial(self, basicMaterial):
        material = three.MeshBasicMaterial()
        material.color = three.Color(*basicMaterial.diffuse[:3]/255)
        material.map = self._parseTexture(
            basicMaterial.image, encoding=three.sRGBEncoding)

        material.toneMapped = True
        material.side = three.FrontSide

        material.needsUpdate = True
        return material

    def _parsePBRMaterial(self, pbrMaterial):
        material = three.MeshStandardMaterial()
        material.map = self._parseTexture(
            pbrMaterial.baseColorTexture, encoding=three.sRGBEncoding)

        material.emissive = three.Color(*pbrMaterial.emissiveFactor)
        material.emissiveMap = self._parseTexture(
            pbrMaterial.emissiveTexture, encoding=three.sRGBEncoding)

        metallicRoughnessMap = self._parseTexture(pbrMaterial.metallicRoughnessTexture)
        material.roughness = pbrMaterial.roughnessFactor or 1.0
        material.roughnessMap = metallicRoughnessMap

        material.metalness = pbrMaterial.metallicFactor or 1.0
        material.metalnessMap = metallicRoughnessMap

        material.normalMap = self._parseTexture(pbrMaterial.normalTexture)

        material.aoMap = self._parseTexture(pbrMaterial.occlusionTexture)
        material.aoMapIntensity = 1.0

        material.toneMapped = True
        material.side = three.FrontSide

        material.needsUpdate = True
        return material

    def _parseTexture(self, PILImage, encoding=three.LinearEncoding):
        if PILImage is None:
            return None
        from PIL.Image import Image  # noqa

        if not isinstance(PILImage, Image):
            raise NotImplementedError()

        PILImage = PILImage.convert(mode='RGBA')

        data = PILImage.tobytes()

        image = three.Image(memoryview(data), width=PILImage.size[0], height=PILImage.size[1])
        tex = three.Texture(image, format=three.RGBAFormat)
        tex.wrapS = three.RepeatWrapping
        tex.wrapT = three.RepeatWrapping
        tex.encoding = encoding
        tex.flipY = False
        tex.updateMatrix()
        tex.generateMipmaps = True
        tex.needsUpdate = True
        return tex

    def _parseMesh(self, mesh):
        import numpy as np

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
        material = self._parseMaterial(visual.material)
        return three.Mesh(geometry, material)

    def loadObj(self, name):
        import trimesh

        path = Path(self.path) / name
        mesh = trimesh.load(path)
        return self._parseMesh(mesh)

    def loadGLTF(self, name):
        import trimesh

        path = Path(self.path) / name
        scene = trimesh.load(path)
        for node_name in scene.graph.nodes_geometry:
            transform, geometry_name = scene.graph[node_name]
            current = scene.geometry[geometry_name]
            current.apply_transform(transform)

        meshes = list(scene.geometry.values())
        meshes = [self._parseMesh(m) for m in meshes]
        return meshes