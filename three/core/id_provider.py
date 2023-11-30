import random
import weakref
import threading

class IdProvider:
    """Object for internal use to manage world object id's."""

    def __init__(self):
        self._ids_in_use = set([0])
        self._map = weakref.WeakValueDictionary()
        self._lock = threading.RLock()

    def claim_id(self, wobject):
        # We don't simply count up, but keep a pool of ids. This is
        # because an application *could* create and discard objects at
        # a high rate, so we want to be able to re-use these ids.
        #
        # Some numbers:
        # * 4_294_967_296 (2**32) max number for u32
        # * 2_147_483_647 (2**31 -1) max number for i32.
        # *    16_777_216 max integer that can be stored exactly in f32
        # *     4_000_000 max integer that survives being passed as a varying (in my tests)
        # *     1_048_575 is ~1M is 2**20 seems like a good max scene objects.
        # *    67_108_864 is ~50M is 2**26 seems like a good max vertex count.
        #                 which leaves 64-20-26=18 bits for any other picking info.

        # Max allowed id, inclusive
        id_max = 1_048_575  # 2*20-1

        # The max number of ids. This is a bit less to avoid choking
        # when there are few free id's left.
        max_items = 1_000_000

        with self._lock:
            if len(self._ids_in_use) >= max_items:
                raise RuntimeError("Max number of objects reached.")
            id = 0
            while id in self._ids_in_use:
                id = random.randint(1, id_max)
            self._ids_in_use.add(id)
            self._map[id] = wobject

        return id

    def release_id(self, wobject, id):
        """Release an id associated with a wobject."""
        with self._lock:
            self._ids_in_use.discard(id)
            self._map.pop(id, None)

    def get_object_from_id(self, id):
        """Return the wobject associated with an id, or None."""
        return self._map.get(id)