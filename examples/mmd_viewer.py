import three
from PyQt5 import QtWidgets, QtCore
from wgpu.gui.qt import WgpuWidget
from pymeshio.pmx import reader
from three.controls import OrbitControls

class MMDViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('mmd_viewer')
        self.resize(800, 600)
        self.wgpu_widget = WgpuWidget()
        
        open_btn = QtWidgets.QPushButton('open')
        open_btn.clicked.connect(self.open_file)

        self.checkbox = QtWidgets.QCheckBox('roatate')

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.wgpu_widget)
        layout.addWidget(open_btn)
        layout.addWidget(self.checkbox)
        self.setLayout(layout)

        self.setAcceptDrops(True)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            url = event.mimeData().urls()[0].toLocalFile()
            if (url.endswith('.pmx')):
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        event.accept()
        url = event.mimeData().urls()[0].toLocalFile()
        if url:
            self.load_mesh(url)

    def init_scene(self):
        self.scene = three.Scene()
        w, h = self.wgpu_widget.get_physical_size()
        self.camera = three.PerspectiveCamera(70, w/h, 0.01, 1000)
        self.camera.position.z = -20
        self.camera.position.y = 10

        self.mesh = None
        
        self.controls = OrbitControls(self.camera, self.wgpu_widget)
        self.controls.target.set(0, 10, 0)
        self.controls.update()

        renderer = three.WgpuRenderer(self.wgpu_widget, parameters={'antialias': True})
        renderer.init()

        def on_resize(event):
            w, h = self.wgpu_widget.get_physical_size()
            self.camera.aspect = w/h
            self.camera.updateProjectionMatrix()

        self.wgpu_widget.add_event_handler(on_resize, 'resize')
        
        def loop():
            if self.checkbox.isChecked():
                self.mesh.rotation.y += 0.02
            renderer.render(self.scene, self.camera)
        
        renderer.setAnimationLoop(loop)

    def open_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'open file', '.', '*.pmx')
        if file_path:
            self.load_mesh(file_path)


    def load_mesh(self, path):
        pmx_file = reader.read_from_file(path)
        positions = []
        normals = []
        uvs = []
        for v in pmx_file.vertices:
            p = v.position
            positions.append(p.x)
            positions.append(p.y)
            positions.append(p.z)

            n = v.normal
            normals.append(n.x)
            normals.append(n.y)
            normals.append(n.z)

            uv = v.uv
            uvs.append(uv.x)
            uvs.append(uv.y)
        
        geometry = three.BufferGeometry()
        geometry.setAttribute('position', three.Float32BufferAttribute(positions, 3))
        geometry.setAttribute('normal', three.Float32BufferAttribute(normals, 3))
        geometry.setAttribute('uv', three.Float32BufferAttribute(uvs, 2))

        geometry.setIndex( pmx_file.indices )


        material = three.MeshNormalMaterial()
        material.side = three.DoubleSide

        mesh = three.Mesh(geometry, material)
        
        if self.mesh:
            self.scene.remove(self.mesh)
        self.scene.add(mesh)

        geometry.computeBoundingBox()
        box = geometry.boundingBox
        box.getCenter(self.controls.target)

        self.camera.position.z = box.max.z + 1.5*(box.max.z - box.min.z)
        self.controls.saveState()
        self.controls.update()

        self.mesh = mesh


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MMDViewer()
    window.init_scene()
    window.show()
    app.exec_()

            

        

            