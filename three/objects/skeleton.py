from typing import List
from warnings import warn
import math, uuid
from .bone import Bone
from ..math import Matrix4
from ..structure import NoneAttribute, Float32Array

_offsetMatrix = Matrix4()
_identityMatrix = Matrix4()

class Skeleton(NoneAttribute):
    def __init__(self, bones:List[Bone] = None, boneInverses = None ):
        self.uuid = uuid.uuid1()
        if bones is None:
            bones = []
        self.bones = bones.copy()
        self.boneInverses = boneInverses or []

        self.boneMatrices = None

        self.boneTexture = None
        self.boneTextureSize = 0

        self.frame = - 1

        self.init()

    def init(self):
        bones = self.bones
        boneInverses = self.boneInverses

        self.boneMatrices = Float32Array.allocate( len(bones) * 16 )

        # calculate inverse bone matrices if necessary

        if len(boneInverses) == 0:
            self.calculateInverses()

        else:
            # handle special case
            if len(bones) != len(boneInverses):
                warn( 'THREE.Skeleton: Number of inverse bone matrices does not match amount of bones.' )
                self.boneInverses = []
                for _ in range( len(self.bones)):
                    self.boneInverses.append( Matrix4() )


    def calculateInverses(self):
        self.boneInverses.clear()
        for bone in self.bones:
            inverse = Matrix4()

            inverse.getInverse(bone.matrixWorld)

            self.boneInverses.append(inverse)


    def pose(self):
        # recover the bind-time world matrices
        for i, bone in enumerate(self.bones):
            bone.matrixWorld.copy(self.boneInverses[i]).invert()

        # compute the local matrices, positions, rotations and scales
        for bone in self.bones:
            if bone:
                if bone.parent and bone.parent.isBone:
                    bone.matrix.getInverse(bone.parent.matrixWorld)
                    bone.matrix.multiply(bone.matrixWorld)
                else:
                    bone.matrix.copy(bone.matrixWorld)

                bone.matrix.decompose(bone.position, bone.quaternion, bone.scale)

    def update(self):
        bones = self.bones
        boneInverses = self.boneInverses
        boneMatrices = self.boneMatrices
        boneTexture = self.boneTexture

        # flatten bone matrices to array
        for i, bone in enumerate(bones):

            matrix = bone.matrixWorld if bone else _identityMatrix

            _offsetMatrix.multiplyMatrices( matrix, boneInverses[ i ] )
            _offsetMatrix.toArray( boneMatrices, i * 16 )

        if boneTexture is not None:
            boneTexture.needsUpdate = True

    def computeBoneTexture(self):
        pass
        # TODO
        # layout (1 matrix = 4 pixels)
        #      RGBA RGBA RGBA RGBA (=> column1, column2, column3, column4)
        #  with  8x8  pixel texture max   16 bones * 4 pixels =  (8 * 8)
        #       16x16 pixel texture max   64 bones * 4 pixels = (16 * 16)
        #       32x32 pixel texture max  256 bones * 4 pixels = (32 * 32)
        #       64x64 pixel texture max 1024 bones * 4 pixels = (64 * 64)

        # size = math.sqrt( len(self.bones) * 4 )  # 4 pixels needed for 1 matrix
        # size = MathUtils.ceilPowerOfTwo( size )
        # size = max( size, 4 )

        # boneMatrices = Float32Array( size * size * 4 ) # 4 floats per RGBA pixel
        # boneMatrices.set( self.boneMatrices ) # copy current values

        # boneTexture = DataTexture( boneMatrices, size, size, RGBAFormat, FloatType )
        # boneTexture.needsUpdate = True

        # self.boneMatrices = boneMatrices
        # self.boneTexture = boneTexture
        # self.boneTextureSize = size

        # return self

    def clone(self):
        return Skeleton( self.bones, self.boneInverses )

    def getBoneByName(self, name) :
        for bone in self.bones:
            if bone.name == name:
                return bone
        return None

    def dispose( self ):
        if self.boneTexture is not None:
            self.boneTexture.dispose()
            self.boneTexture = None


    def __repr__(self) -> str:
        def print_tree(bone:Bone, level = 0):
            if level == 0:
                name = bone.name
            else:
                name = '---- ' * level + bone.name
            
            s = f'{name.ljust(40, " ")} \t{str(bone.position).ljust(35, " ")} \t{bone.rotation} \t{bone.matrix}\n'
            for child in bone.children:
                s += print_tree(child, level+1)
            return s
        
        s=f'Skeleton[{len(self.bones)}]: \n'
        for bone in self.bones:
            if bone.parent is None:
                s += print_tree(bone)
        
        return s

