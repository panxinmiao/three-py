from ..core.node import Node
from warnings import warn

class LightingNode(Node):

    def __init__(self) -> None:
        super().__init__('vec3')

    def generate(self, *args):
        warn( 'Abstract function.' )