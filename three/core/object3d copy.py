from . import EventDispatcher
from ..structure import Dict
from ..math import Vector3, Matrix4, Quaternion, Matrix3
from .id_provider import IdProvider
from .layers import Layers
from typing import List

id_provider = IdProvider()

#_m1 = Matrix4()
# TODO 重写

class Object3D(EventDispatcher):
    _v = Vector3()
    _m = Matrix4()
    _q = Quaternion()

    def __init__(
        self,
        name = ''
    ):
        self.visible = True
        self._name = name
        self._type = "Object3D"
        
        # Init parent and children
        self._parent: Object3D = None
        self._children: List[Object3D] = []

        self.position = Vector3()
        self.rotation = Quaternion()
        self.scale = Vector3(1, 1, 1)
        self._transform_hash = ()

        self.up = Vector3(0, 1, 0)


        self.model_view_matrix = Matrix4()
        self.normal_matrix = Matrix3()

        self._matrix = Matrix4()
        self._matrix_world = Matrix4()
        self._matrix_auto_update = True
        self._matrix_world_dirty = False

        self.cast_shadow = False
        self.receive_shadow = False

        self.frustum_culled = True
        self.render_order = 0

        self.animations = []

        self.userData = Dict({})

        self._id = id_provider.claim_id(self)

        self.layers = Layers()


    def __del__(self):
        id_provider.release_id(self, self.id)

    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def parent(self):
        """Object's parent in the scene graph (read-only).
        An object can have at most one parent.
        """
        return self._parent

    @property
    def children(self):
        """The child objects of this wold object (read-only tuple).
        Use ``.add()`` and ``.remove()`` to change this list.
        """
        return tuple(self._children)

    def add(self, *objects):
        """Adds object as child of this object. Any number of
        objects may be added. Any other current parent on an object passed
        in here will be removed, since an object can have at most one
        parent.
        """
        for obj in objects:
            if obj._parent is not None:
                obj._parent.remove(obj)

            obj._parent = self
            self._children.append(obj)
            # flag world matrix as dirty
            obj._matrix_world_dirty = True
        return self

    def remove(self, *objects):
        """Removes object as child of this object. Any number of objects may be removed.
        If a given object is not a child, it is ignored.
        """
        for obj in objects:

            try:
                self._children.remove(obj)
                obj._parent = None
            except ValueError:
                pass
        return self

    def traverse(self, callback, skip_invisible=False):
        """Executes the callback on this object and all descendants.
        """
        if skip_invisible and not self.visible:
            return
        callback(self)
        for child in self._children:
            child.traverse(callback, skip_invisible)

    def update_matrix(self):
        p, r, s = self.position, self.rotation, self.scale
        hash = p.x, p.y, p.z, r.x, r.y, r.z, r.w, s.x, s.y, s.z
        if hash != self._transform_hash:
            self._transform_hash = hash
            self._matrix.compose(self.position, self.rotation, self.scale)
            self._matrix_world_dirty = True

    @property
    def matrix(self):
        """The (settable) transformation matrix."""
        return self._matrix

    @matrix.setter
    def matrix(self, matrix):
        self._matrix.copy(matrix)
        self._matrix.decompose(self.position, self.rotation, self.scale)
        self._matrix_world_dirty = True

    @property
    def matrix_world(self):
        """The world matrix (local matrix composed with any parent matrices)."""
        return self._matrix_world

    @property
    def matrix_auto_update(self):
        """Whether or not the matrix auto-updates."""
        return self._matrix_auto_update

    @matrix_auto_update.setter
    def matrix_auto_update(self, value):
        self._matrix_auto_update = bool(value)

    @property
    def matrix_world_dirty(self):
        """Whether or not the matrix needs updating (readonly)."""
        return self._matrix_world_dirty

    def apply_matrix(self, matrix):
        if self._matrix_auto_update:
            self.update_matrix()
        self._matrix.premultiply(matrix)
        self._matrix.decompose(self.position, self.rotation, self.scale)
        self._matrix_world_dirty = True

    def update_matrix_world(
        self, force=False, update_children=True, update_parents=False
    ):
        if update_parents and self.parent:
            self.parent.update_matrix_world(
                force=force, update_children=False, update_parents=True
            )
        if self._matrix_auto_update:
            self.update_matrix()
        if self._matrix_world_dirty or force:
            if self.parent is None:
                self._matrix_world.copy(self._matrix)
            else:
                self._matrix_world.multiply_matrices(
                    self.parent._matrix_world, self._matrix
                )

            self._matrix_world_dirty = False
            for child in self._children:
                child._matrix_world_dirty = True
        if update_children:
            for child in self._children:
                child.update_matrix_world()

    def look_at(self, target: Vector3):
        self.update_matrix_world(update_parents=True, update_children=False)
        self._v.set_from_matrix_position(self._matrix_world)
        self._m.look_at(self._v, target, self.up)
        self.rotation.set_from_rotation_matrix(self._m)
        if self.parent:
            self._m.extract_rotation(self.parent._matrix_world)
            self._q.set_from_rotation_matrix(self._m)
            self.rotation.premultiply(self._q.inverse())


    def local_to_world(self, vector: Vector3):
        return vector.apply_matrix4( self._matrix_world )
	

    def world_to_local(self, vector: Vector3):
        return vector.apply_matrix4(self._m.get_inverse(self._matrix_world))


    updateMatrix = update_matrix
    applyMatrix = apply_matrix
    updateMatrixWorld = update_matrix_world
    lookAt = look_at
    localToWorld = local_to_world
    worldToLocal = world_to_local