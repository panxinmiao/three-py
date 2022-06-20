# three-py

A Python render engine like threejs(via wgpu).

## Introduction

This is a Python render engine build on top of WGPU.

## Current status

Under development, many things can change.

## Installation

```
pip install three-py
```
Or, to get the latest from GitHub:
```
pip install -U https://github.com/panxinmiao/three-py/archive/main.zip
```

## Requirements

[wgpu-py](https://github.com/pygfx/wgpu-py)

To run the [examples](./examples/), You probably also want to install `glwf` (or other gui backends).

Please check the installation instructions of [wgpu-py](https://github.com/pygfx/wgpu-py) for details.

## Usage

This code creates a scene, a camera, and a geometric cube, and animates the cube within the scene for the camera.

Also see the [examples](./examples/).

```Python
import three
from wgpu.gui.auto import WgpuCanvas, run

canvas = WgpuCanvas(size=(640, 480), title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias = True)
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100)
camera.position.z = 1

scene = three.Scene()

geometry = three.BoxGeometry(0.2, 0.2, 0.2)
material = three.MeshNormalMaterial()

mesh = three.Mesh(geometry, material)
scene.add(mesh)

def loop():
    mesh.rotation.x += 0.01
    mesh.rotation.y += 0.02
    render.render(scene, camera)

render.setAnimationLoop(loop)

run()
```

