
from .base import Camera
from ..structure import Dict
from ..math import math_utils as MathUtils
import math

class OrthographicCamera(Camera):

    def __init__(self, left=- 1, right=1, top=1, bottom=- 1, near=0.1, far=2000):
        super().__init__()

        self.zoom = 1
        self.view = None

        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

        self.near = near
        self.far = far

        self.updateProjectionMatrix()

    def copy(self):
        pass

    def setViewOffset(self, fullWidth, fullHeight, x, y, width, height):

        if self.view is None:
            self.view = Dict({
                'enabled': True,
                'fullWidth': 1,
                'fullHeight': 1,
                'offsetX': 0,
                'offsetY': 0,
                'width': 1,
                'height': 1
            })

        self.view.enabled = True
        self.view.fullWidth = fullWidth
        self.view.fullHeight = fullHeight
        self.view.offsetX = x
        self.view.offsetY = y
        self.view.width = width
        self.view.height = height

        self.updateProjectionMatrix()


    def clearViewOffset(self):
        if self.view is not None:
            self.view.enabled = False
            self.updateProjectionMatrix()

    def updateProjectionMatrix(self):

        dx = (self.right - self.left) / (2 * self.zoom)
        dy = (self.top - self.bottom) / (2 * self.zoom)
        cx = (self.right + self.left) / 2
        cy = (self.top + self.bottom) / 2

        left = cx - dx
        right = cx + dx
        top = cy + dy
        bottom = cy - dy

        if self.view and  self.view.enabled:
            scaleW = (self.right - self.left) / self.view.fullWidth / self.zoom
            scaleH = (self.top - self.bottom) / self.view.fullHeight / self.zoom

            left += scaleW * self.view.offsetX
            right = left + scaleW * self.view.width
            top -= scaleH * self.view.offsetY
            bottom = top - scaleH * self.view.height
   
        self.projectionMatrix.makeOrthographic(left, right, top, bottom, self.near, self.far)
        self.projectionMatrixInverse.copy(self.projectionMatrix).invert()
