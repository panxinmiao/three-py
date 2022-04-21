from ..wgpu_uniform import FloatUniform, Vector2Uniform, Vector3Uniform, Vector4Uniform, ColorUniform, Matrix3Uniform, Matrix4Uniform

class FloatNodeUniform(FloatUniform):

    def __init__(self, nodeUniform ) -> None:
        super().__init__( nodeUniform.name, nodeUniform.value )
        self.nodeUniform = nodeUniform

    def getValue(self):
        return self.nodeUniform.value


class Vector2NodeUniform(Vector2Uniform):

    def __init__(self, nodeUniform ) -> None:
        super().__init__( nodeUniform.name, nodeUniform.value )
        self.nodeUniform = nodeUniform

    def getValue(self):
        return self.nodeUniform.value

class Vector3NodeUniform(Vector3Uniform):

    def __init__(self, nodeUniform ) -> None:
        super().__init__( nodeUniform.name, nodeUniform.value )
        self.nodeUniform = nodeUniform

    def getValue(self):
        return self.nodeUniform.value

class Vector4NodeUniform(Vector4Uniform):

    def __init__(self, nodeUniform ) -> None:
        super().__init__( nodeUniform.name, nodeUniform.value )
        self.nodeUniform = nodeUniform

    def getValue(self):
        return self.nodeUniform.value

class ColorNodeUniform(ColorUniform):

    def __init__(self, nodeUniform ) -> None:
        super().__init__( nodeUniform.name, nodeUniform.value )
        self.nodeUniform = nodeUniform

    def getValue(self):
        return self.nodeUniform.value

class Matrix3NodeUniform(Matrix3Uniform):

    def __init__(self, nodeUniform ) -> None:
        super().__init__( nodeUniform.name, nodeUniform.value )
        self.nodeUniform = nodeUniform

    def getValue(self):
        return self.nodeUniform.value

class Matrix4NodeUniform(Matrix4Uniform):

    def __init__(self, nodeUniform ) -> None:
        super().__init__( nodeUniform.name, nodeUniform.value )
        self.nodeUniform = nodeUniform

    def getValue(self):
        return self.nodeUniform.value
