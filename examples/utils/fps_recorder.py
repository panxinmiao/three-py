import time

class FPSRecorder:
    def __init__(self):
        now = time.time()
        self.fps = now, now, 1

    def update(self):
        now = time.time()
        if now > self.fps[0] + 1:
            print(f"FPS: {self.fps[2]/(now - self.fps[0]):0.1f}")
            self.fps = now, now, 1
        else:
            self.fps = self.fps[0], now, self.fps[2] + 1
