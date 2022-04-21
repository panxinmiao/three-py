from .event import Event
from ..structure import Dict, NoneAttribute
import warnings

class EventDispatcher(NoneAttribute):

    def addEventListener(self, type, listener):

        if not callable(listener):
            warnings.warn('listener not callable')
            return 

        if not hasattr(self, '_listeners') or self._listeners is None:
            self._listeners = Dict()

        listeners = self._listeners

        if not listeners[ type ]:
            listeners[ type ] = []

        if not listener in listeners[ type ]:
            listeners[ type ].append( listener )


    def hasEventListener( self, type, listener ):

        if not hasattr(self, '_listeners') or self._listeners is None:
            return False

        listeners = self._listeners

        return listeners[ type ] and listener in listeners[ type ]



    def removeEventListener( self, type, listener ):

        if not hasattr(self, '_listeners') or self._listeners is None:
            return 
        
        listeners = self._listeners
        listenerArray:list = listeners[ type ]

        if listenerArray and listener in listenerArray:

            listenerArray.remove(listener)

            #index = listenerArray.index( listener )



    def dispatchEvent( self, event:Event ):

        if not hasattr(self, '_listeners') or self._listeners is None:
            return

        if type(event) == str:
            event = Event(event)

        listeners = self._listeners
        listenerArray:list = listeners[ event.type ]

        if listenerArray:
            event.target = self

            array = listenerArray.copy()

            for listener in array:
                listener( event )

            event.target = None

