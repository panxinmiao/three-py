from weakref import WeakKeyDictionary
from ...structure import Dict
from functools import cmp_to_key


def painterSortStable( a, b ):
	if a.groupOrder != b.groupOrder:
		return a.groupOrder - b.groupOrder

	elif a.renderOrder != b.renderOrder:
		return a.renderOrder - b.renderOrder

	elif a.material.id != b.material.id:
		return a.material.id - b.material.id

	elif a.z != b.z :
		return a.z - b.z

	else:
		return a.id - b.id


def reversePainterSortStable( a, b ):
    if a.groupOrder != b.groupOrder:
        return a.groupOrder - b.groupOrder
    elif a.renderOrder != b.renderOrder:
        return a.renderOrder - b.renderOrder
    elif a.z != b.z:
        return b.z - a.z
    else:
        return a.id - b.id


class WgpuRenderList:

    def __init__(self) -> None:
        
        self.renderItems = []
        self.renderItemsIndex = 0
        self.opaque = []
        self.transparent = []

    def init(self):
        self.renderItemsIndex = 0

        self.opaque.clear()
        self.transparent.clear()

    def getNextRenderItem( self, object, geometry, material, groupOrder, z, group ):

        length = len(self.renderItems)
        if length <= self.renderItemsIndex:
            self.renderItems.extend([None] * (self.renderItemsIndex - length+1))

        renderItem = self.renderItems[ self.renderItemsIndex ]

        if renderItem is None:
            
            renderItem = Dict({
				'id': object.id,
				'object': object,
				'geometry': geometry,
				'material': material,
				'groupOrder': groupOrder,
				'renderOrder': object.renderOrder,
				'z': z,
				'group': group
			})
            
            self.renderItems[ self.renderItemsIndex ] = renderItem

        else:
            renderItem.id = object.id
            renderItem.object = object
            renderItem.geometry = geometry
            renderItem.material = material
            renderItem.groupOrder = groupOrder
            renderItem.renderOrder = object.renderOrder
            renderItem.z = z
            renderItem.group = group

        self.renderItemsIndex +=1

        return renderItem

    def push( self, object, geometry, material, groupOrder, z, group ):
        # print('push', object, geometry, material, groupOrder, z, group)
        renderItem = self.getNextRenderItem( object, geometry, material, groupOrder, z, group )
        if material.transparent:
            self.transparent.append( renderItem )
        else:
            self.opaque.append( renderItem )

    def unshift( self, object, geometry, material, groupOrder, z, group ):
        renderItem = self.getNextRenderItem( object, geometry, material, groupOrder, z, group )

        if material.transparent:
            self.transparent.remove( renderItem )
        else:
            self.opaque.remove( renderItem )

    def sort( self, customOpaqueSort = None, customTransparentSort = None ):
        
        if len(self.opaque) > 1:
            self.opaque.sort( key = cmp_to_key( customOpaqueSort or painterSortStable ) )

        if len(self.transparent) > 1:
            self.transparent.sort( key = cmp_to_key( customTransparentSort or reversePainterSortStable ) )


    def finish(self):
		# Clear references from inactive renderItems in the list

        i = self.renderItemsIndex
        il = len(self.renderItems)
        while i<il:
            renderItem = self.renderItems[ i ]
            if renderItem.id is None:
                break
            renderItem.id = None
            renderItem.object = None
            renderItem.geometry = None
            renderItem.material = None
            renderItem.program = None
            renderItem.group = None

            i+=1


class WgpuRenderLists:

    def __init__(self) -> None:
        self.lists = WeakKeyDictionary()


    def get( self, scene, camera ):
        lists = self.lists
        cameras = lists.get( scene )

        if cameras is None:
            list = WgpuRenderList()
            lists[scene] = WeakKeyDictionary()
            lists.get( scene )[camera] = list

        else:
            list = cameras.get( camera )
            if list is None:
                list = WgpuRenderList()
                cameras[camera] = list

        return list


    def dispose(self):

        self.lists = WeakKeyDictionary()
