import time
import math
import random

from wgpu.gui.auto import WgpuCanvas, run
import three


def update_value(target, dist):
    for k, v in dist.items():
        if isinstance(v, dict):
            update_value(getattr(target, k), v)
        else:
            setattr(target, k, v)

    return dist


def get_value(target, template):
    vals = {}
    for k, v in template.items():
        if isinstance(v, dict):
            vals[k] = get_value(getattr(target, k), v)
        else:
            vals[k] = getattr(target, k)

    return vals


def lerp(start_vals, to_vals, t):
    current_vals = {}
    for key, start_value in start_vals.items():
        if isinstance(start_value, (int, float)):
            to_value = to_vals[key]
            value = start_value + (to_value - start_value) * t
            current_vals[key] = value

        elif isinstance(start_value, dict):
            current_vals[key] = lerp(start_value, to_vals[key], t)

    return current_vals


class Tween:
    def __init__(self, target):
        self.target = target
        self.starttime = 0
        self._lerp_func = None

    def to(self, to: dict, duration):
        self.to_val = to
        self.duration = duration
        self.starttime = time.time()
        self.start_val = get_value(self.target, to)
        return self

    def lerp_func(self, func):
        self._lerp_func = func
        return self

    def update(self):
        t = (time.time() - self.starttime) / self.duration
        if t < 1:
            if self._lerp_func:
                t = self._lerp_func(t)
            current_val = lerp(self.start_val, self.to_val, t)
            update_value(self.target, current_val)

    @property
    def since_last_start(self):
        return time.time() - self.starttime


def init_scene():
    canvas = WgpuCanvas(size=(640, 480), max_fps=60)
    renderer = three.WgpuRenderer(canvas, antialias=True)
    renderer.init()

    renderer.outputEncoding = three.sRGBEncoding

    scene = three.Scene()
    camera = three.PerspectiveCamera(35, 16 / 9, 1, 2000)
    camera.position.set(46, 22, -21)

    controller = three.OrbitControls(camera, canvas)
    # controller.add_default_event_handlers(renderer, camera)

    controller.target.set(0, 7, 0)
    controller.maxPolarAngle = math.pi / 2
    controller.update()

    floor = three.Mesh(
        three.PlaneGeometry(2000, 2000),
        three.MeshPhongMaterial(color=0x808080, side=three.FrontSide),
    )

    floor.rotation.x = -math.pi / 2
    floor.position.set(0, -0.05, 0)

    ambient = three.AmbientLight(0x111111)

    def create_spot_light(color) -> three.SpotLight:
        return three.SpotLight(color, 2000, angle=0.3, penumbra=0.2, decay=2)

    spot_light1 = create_spot_light(0xff7f00)
    spot_light2 = create_spot_light(0x00ff7f)
    spot_light3 = create_spot_light(0x7f00ff)

    spot_light1.position.set(15, 40, 45)
    spot_light2.position.set(0, 40, 35)
    spot_light3.position.set(-15, 40, 45)

    scene.add(floor)
    scene.add(ambient)
    scene.add(spot_light1, spot_light2, spot_light3)
    
    # lightHelper1 = three.SpotLightHelper(spot_light1)
    scene.add(three.SpotLightHelper(spot_light1))
    # lightHelper2 = three.SpotLightHelper(spot_light2)
    scene.add(three.SpotLightHelper(spot_light2))
    # lightHelper3 = three.SpotLightHelper(spot_light3)
    scene.add(three.SpotLightHelper(spot_light3))

    tweens = [Tween(spot_light1), Tween(spot_light2), Tween(spot_light3)]

    def animate():
        for tween in tweens:
            if tween.since_last_start > 5:
                tween.to(
                    {
                        "angle": random.random() * 0.7 + 0.1,
                        "penumbra": random.random() + 1,
                        "position": {
                            "x": random.random() * 30 - 15,
                            "y": random.random() * 10 + 15,
                            "z": random.random() * 30 - 15,
                        },
                    },
                    random.random() * 3 + 2,
                ).lerp_func(lambda t: t * (2 - t))

            tween.update()

        renderer.render(scene, camera)

    renderer.setAnimationLoop(animate)


if __name__ == "__main__":
    init_scene()
    run()
