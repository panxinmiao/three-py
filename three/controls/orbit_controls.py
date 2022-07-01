from ..core import EventDispatcher
import three, math, wgpu
from three import Vector2, Vector3, Spherical, Quaternion, MOUSE, TOUCH, Dict, Event
from warnings import warn
from .ui_event import UIEvent

class STATE:
    NONE = - 1
    ROTATE = 0
    DOLLY = 1
    PAN = 2
    TOUCH_ROTATE = 3
    TOUCH_PAN = 4
    TOUCH_DOLLY_PAN = 5
    TOUCH_DOLLY_ROTATE = 6


# _changeEvent = Dict({ type: 'change' })
# _startEvent = Dict({ type: 'start' })
# _endEvent = Dict({ type: 'end' })

_changeEvent = Event('change')
_startEvent = Event('start')
_endEvent = Event('end')

EPS = 0.000001

class OrbitControls(EventDispatcher):

    def __init__(self, obj:'three.Camera', canvas:'three.WgpuRenderer') -> None:
        super().__init__()

        self.object = obj
        
        if not isinstance(canvas, wgpu.gui.WgpuAutoGui):
            # warn(f'canvas [{canvas.__class__}] not support controls yet, use glfw.WgpuCanvas instead')
            raise NotImplementedError(f'canvas [{canvas.__class__}] not support controls yet, use glfw.WgpuCanvas instead')

        self.canvas = canvas

        # Set to false to disable self control
        self.enabled = True

        # "target" sets the location of focus, where the object orbits around
        self.target = Vector3()

        # How far you can dolly in and out ( PerspectiveCamera only )
        self.minDistance = 0
        self.maxDistance = math.inf

        # How far you can zoom in and out ( OrthographicCamera only )
        self.minZoom = 0
        self.maxZoom = math.inf

        # How far you can orbit vertically, upper and lower limits.
        # Range is 0 to Math.PI radians.
        self.minPolarAngle = 0 # radians
        self.maxPolarAngle = math.pi # radians

        # How far you can orbit horizontally, upper and lower limits.
        # If set, the interval [ min, max ] must be a sub-interval of [ - 2 PI, 2 PI ], with ( max - min < 2 PI )
        self.minAzimuthAngle = - math.inf # radians
        self.maxAzimuthAngle = math.inf # radians

        # Set to true to enable damping (inertia)
        # If damping is enabled, you must call controls.update() in your animation loop
        self.enableDamping = False
        self.dampingFactor = 0.05

        # This option actually enables dollying in and out left as "zoom" for backwards compatibility.
        # Set to false to disable zooming
        self.enableZoom = True
        self.zoomSpeed = 1.0

        # Set to false to disable rotating
        self.enableRotate = True
        self.rotateSpeed = 1.0

        # Set to false to disable panning
        self.enablePan = True
        self.panSpeed = 1.0
        self.screenSpacePanning = True # if false, pan orthogonal to world-space direction camera.up
        self.keyPanSpeed = 7.0  # pixels moved per arrow key push

        # Set to true to automatically rotate around the target
        # If auto-rotate is enabled, you must call controls.update() in your animation loop
        self.autoRotate = False
        self.autoRotateSpeed = 2.0 # 30 seconds per orbit when fps is 60

        # The four arrow keys
        self.keys = Dict({ 'LEFT': 'ArrowLeft', 'UP': 'ArrowUp', 'RIGHT': 'ArrowRight', 'BOTTOM': 'ArrowDown' })

        # Mouse buttons
        self.mouseButtons = Dict({ 'LEFT': MOUSE.ROTATE, 'MIDDLE': MOUSE.DOLLY, 'RIGHT': MOUSE.PAN })

        # Touch fingers
        self.touches = Dict({ 'ONE': TOUCH.ROTATE, 'TWO': TOUCH.DOLLY_PAN })

        # for reset
        self.target0 = self.target.clone()
        self.position0 = self.object.position.clone()
        self.zoom0 = self.object.zoom

        # the target DOM element for key events
        # self._domElementKeyEvents = null

        # self.__STATE = {
        #     'NONE': - 1,
        #     'ROTATE': 0,
        #     'DOLLY': 1,
        #     'PAN': 2,
        #     'TOUCH_ROTATE': 3,
        #     'TOUCH_PAN': 4,
        #     'TOUCH_DOLLY_PAN': 5,
        #     'TOUCH_DOLLY_ROTATE': 6
        # }

        self.__state = STATE.NONE

        # current position in spherical coordinates
        self.__spherical = Spherical()
        self.__sphericalDelta = Spherical()

        self.__scale = 1
        self.__panOffset = Vector3()
        self.__zoomChanged = False

        self.__rotateStart = Vector2()
        self.__rotateEnd = Vector2()
        self.__rotateDelta = Vector2()

        self.__panStart = Vector2()
        self.__panEnd = Vector2()
        self.__panDelta = Vector2()

        self.__dollyStart = Vector2()
        self.__dollyEnd = Vector2()
        self.__dollyDelta = Vector2()

        self.__pointers = []
        self.__pointerPositions = {}

        self.__handler_cache = {}

        def __update():
            offset = Vector3()

            # so camera.up is the orbit axis
            quat = Quaternion().setFromUnitVectors( self.object.up, Vector3( 0, 1, 0 ) )
            quatInverse = quat.clone().invert()
            
            lastPosition = Vector3()
            lastQuaternion = Quaternion()
            twoPI = 2 * math.pi

            def update():
                position = self.object.position

                offset.copy( position ).sub( self.target )

                # rotate offset to "y-axis-is-up" space
                offset.applyQuaternion( quat )

                # angle from z-axis around y-axis
                self.__spherical.setFromVector3( offset )

                if self.autoRotate and self.__state == STATE.NONE:
                    self.__rotateLeft( self.__getAutoRotationAngle() )

                if self.enableDamping:
                    self.__spherical.theta += self.__sphericalDelta.theta * self.dampingFactor
                    self.__spherical.phi += self.__sphericalDelta.phi * self.dampingFactor

                else:
                    self.__spherical.theta += self.__sphericalDelta.theta
                    self.__spherical.phi += self.__sphericalDelta.phi

                # restrict theta to be between desired limits

                _min = self.minAzimuthAngle
                _max = self.maxAzimuthAngle

                if math.isfinite( _min ) and math.isfinite( _max ):

                    if _min < - math.pi:
                        _min += twoPI
                    elif _min > math.pi:
                        _min -= twoPI

                    if _max < - math.pi:
                        _max += twoPI
                    elif _max > math.pi:
                        _max -= twoPI

                    if _min <= _max:
                        self.__spherical.theta = max( _min, min( _max, self.__spherical.theta ) )

                    else:
                        self.__spherical.theta = max( _min, self.__spherical.theta ) if self.__spherical.theta > ( _min + _max ) / 2  else min( _max, self.__spherical.theta )



                # restrict phi to be between desired limits
                self.__spherical.phi = max( self.minPolarAngle, min( self.maxPolarAngle, self.__spherical.phi ) )

                self.__spherical.makeSafe()


                self.__spherical.radius *= self.__scale

                # restrict radius to be between desired limits
                self.__spherical.radius = max( self.minDistance, min( self.maxDistance, self.__spherical.radius ) )

                # move target to panned location

                if self.enableDamping == True:
                    self.target.addScaledVector( self.__panOffset, self.dampingFactor )

                else:
                    self.target.add( self.__panOffset )


                offset.setFromSpherical( self.__spherical )

                # rotate offset back to "camera-up-vector-is-up" space
                offset.applyQuaternion( quatInverse )

                position.copy( self.target ).add( offset )

                self.object.lookAt( self.target )

                if self.enableDamping == True:
                    self.__sphericalDelta.theta *= ( 1 - self.dampingFactor )
                    self.__sphericalDelta.phi *= ( 1 - self.dampingFactor )

                    self.__panOffset.multiplyScalar( 1 - self.dampingFactor )

                else:

                    self.__sphericalDelta.set( 0, 0, 0 )

                    self.__panOffset.set( 0, 0, 0 )

                self.__scale = 1

                # update condition is:
                # min(camera displacement, camera rotation in radians)^2 > EPS
                # using small-angle approximation cos(x/2) = 1 - x^2 / 8

                if ( self.__zoomChanged or
                    lastPosition.distanceToSquared( self.object.position ) > EPS or
                    8 * ( 1 - lastQuaternion.dot( self.object.quaternion ) ) > EPS ):

                    self.dispatchEvent( _changeEvent )

                    lastPosition.copy( self.object.position )
                    lastQuaternion.copy( self.object.quaternion )
                    self.__zoomChanged = False

                    return True

                return False

            return update

        self.__update = __update()
        self.__panLeft_ = self.__panLeft_()
        self.__panUp_ = self.__panUp_()
        self.__pan_ = self.__pan_()

        
        # scope.domElement.addEventListener( 'contextmenu', onContextMenu );

        # scope.domElement.addEventListener( 'pointerdown', onPointerDown );
        # scope.domElement.addEventListener( 'pointercancel', onPointerCancel );
        # scope.domElement.addEventListener( 'wheel', onMouseWheel, { passive: false } );

        self.bindEvent( self.__onPointerDown, 'pointer_down' )
        self.bindEvent( self.__onPointerCancel, 'pointer_cancel' )
        self.bindEvent( self.__onMouseWheel,'wheel')

        # force an update at start

        self.update()



    def bindEvent(self, handler, eventType):
        def handler_wrapper(event):
            event = UIEvent(event)
            handler(event)

        self.__handler_cache[handler] = handler_wrapper
        self.canvas.add_event_handler( handler_wrapper, eventType )


    def removeEvent(self, handler, eventType):
        self.canvas.remove_event_handler( self.__handler_cache.pop( handler ), eventType )

    # public methods
    def getPolarAngle(self):
        return self.__spherical.phi

    def getAzimuthalAngle(self):
        return self.__spherical.theta

    def getDistance(self):
        return self.object.position.distanceTo( self.target )

    # def listenToKeyEvents( self, domElement ):
    #     domElement.addEventListener( 'keydown', onKeyDown )
    #     this._domElementKeyEvents = domElement
    # }
    
    def saveState(self):
        self.target0.copy( self.target )
        self.position0.copy( self.object.position )
        self.zoom0 = self.object.zoom


    def reset(self):
        self.target.copy( self.target0 )
        self.object.position.copy( self.position0 )
        self.object.zoom = self.zoom0

        self.object.updateProjectionMatrix()
        self.dispatchEvent( _changeEvent )

        self.update()

        self.__state = STATE.NONE

    def update(self):
        self.__update()


    def dispose(self):
        self.removeEvent( self.__onPointerDown, 'pointer_down' )
        self.removeEvent( self.__onPointerCancel, 'pointer_cancel' )
        self.removeEvent( self.__onMouseWheel, 'wheel')

        self.removeEvent( self.__onPointerMove, 'pointer_move' )
        self.removeEvent( self.__onPointerUp, 'pointer_up' )


    def __getAutoRotationAngle(self):
        return 2 * math.pi / 60 / 60 * self.autoRotateSpeed

    def __getZoomScale(self):
        return math.pow( 0.95, self.zoomSpeed )

    def __rotateLeft( self, angle ):
        self.__sphericalDelta.theta -= angle

    def __rotateUp( self, angle ):
        self.__sphericalDelta.phi -= angle

    
    def __panLeft_(self):
        v = Vector3()
        def panLeft(distance, objectMatrix ):
            v.setFromMatrixColumn( objectMatrix, 0 )   # get X column of objectMatrix
            v.multiplyScalar( - distance )
            self.__panOffset.add( v )
        
        return panLeft

    def __panLeft(self, distance, objectMatrix ):
        self.__panLeft_(distance, objectMatrix)


    def __panUp_(self):
        v = Vector3()
        def panUp( distance, objectMatrix ):
            if self.screenSpacePanning:
                v.setFromMatrixColumn( objectMatrix, 1 )
            else:
                v.setFromMatrixColumn( objectMatrix, 0 )
                v.crossVectors( self.object.up, v )

            v.multiplyScalar( distance )
            self.__panOffset.add( v )

        return panUp


    def __panUp(self, distance, objectMatrix):
        self.__panUp_(distance, objectMatrix)

    # deltaX and deltaY are in pixels; right and down are positive
    def __pan_(self):
        offset = Vector3()
        def pan( deltaX, deltaY ):
            element = self.canvas
            cw, ch = element.get_physical_size()
            if self.object.isPerspectiveCamera:
                # perspective
                position = self.object.position
                offset.copy( position ).sub( self.target )
                targetDistance = offset.length()

                # half of the fov is center to top of screen
                targetDistance *= math.tan( ( self.object.fov / 2 ) * math.pi / 180.0 )

                # we use only clientHeight here so aspect ratio does not distort speed
                self.__panLeft( 2 * deltaX * targetDistance / cw, self.object.matrix )
                self.__panUp( 2 * deltaY * targetDistance / ch, self.object.matrix )

            elif self.object.isOrthographicCamera:
                # orthographic
                self.__panLeft( deltaX * ( self.object.right - self.object.left ) / self.object.zoom / cw, self.object.matrix )
                self.__panUp( deltaY * ( self.object.top - self.object.bottom ) / self.object.zoom / ch, self.object.matrix )

            else:
                # camera neither orthographic nor perspective
                warn( 'WARNING: OrbitControls encountered an unknown camera type - pan disabled.' )
                self.enablePan = False

        return pan

    def __pan(self, deltaX, deltaY):
        self.__pan_(deltaX, deltaY)

    def __dollyOut( self, dollyScale ):

        if self.object.isPerspectiveCamera:
            self.__scale /= dollyScale

        elif self.object.isOrthographicCamera:
            self.object.zoom = max( self.minZoom, min( self.maxZoom, self.object.zoom * dollyScale ) )
            self.object.updateProjectionMatrix()
            self.__zoomChanged = True

        else:
            warn( 'WARNING: OrbitControls encountered an unknown camera type - dolly/zoom disabled.' )
            self.enableZoom = False

    def __dollyIn( self, dollyScale ):
        if self.object.isPerspectiveCamera:
            self.__scale *= dollyScale

        elif self.object.isOrthographicCamera:
            self.object.zoom = max( self.minZoom, min( self.maxZoom, self.object.zoom / dollyScale ) )
            self.object.updateProjectionMatrix()
            self.__zoomChanged = True

        else:
            warn( 'WARNING: OrbitControls encountered an unknown camera type - dolly/zoom disabled.' )
            self.enableZoom = False

    #
    # event callbacks - update the object state
    #

    def __handleMouseDownRotate( self, event ):
        self.__rotateStart.set( event.x, event.y )


    def __handleMouseDownDolly( self, event ):
        self.__dollyStart.set( event.x, event.y )


    def __handleMouseDownPan( self, event ):
        self.__panStart.set( event.x, event.y )

    def __handleMouseMoveRotate( self, event ):

        self.__rotateEnd.set( event.x, event.y )

        self.__rotateDelta.subVectors( self.__rotateEnd, self.__rotateStart ).multiplyScalar( self.rotateSpeed )

        element = self.canvas
        cw, ch = element.get_physical_size()

        self.__rotateLeft( 2 * math.pi * self.__rotateDelta.x / ch ); # yes, height

        self.__rotateUp( 2 * math.pi * self.__rotateDelta.y / ch )

        self.__rotateStart.copy( self.__rotateEnd )

        self.update()


    def __handleMouseMoveDolly( self, event ):
        self.__dollyEnd.set( event.x, event.y )

        self.__dollyDelta.subVectors( self.__dollyEnd, self.__dollyStart )

        if self.__dollyDelta.y > 0:

            self.__dollyOut( self.__getZoomScale() )

        elif self.__dollyDelta.y < 0:
            self.__dollyIn( self.__getZoomScale() )

        self.__dollyStart.copy( self.__dollyEnd )

        self.update()


    def __handleMouseMovePan( self, event ):

        self.__panEnd.set( event.x, event.y )

        self.__panDelta.subVectors( self.__panEnd, self.__panStart ).multiplyScalar( self.panSpeed )

        self.__pan( self.__panDelta.x, self.__panDelta.y )

        self.__panStart.copy( self.__panEnd )

        self.update()

    def __handleMouseWheel( self, event ):

        if event.dy < 0:
            self.__dollyIn( self.__getZoomScale() )

        elif event.dy > 0:
            self.__dollyOut( self.__getZoomScale() )

        self.update()

    def __handleKeyDown( self, event ):
        needsUpdate =  False
        if event.code == self.keys.UP:
            self.__pan( 0, self.keyPanSpeed )
            needsUpdate = True
        elif event.code == self.keys.BOTTOM:
            self.__pan( 0, - self.keyPanSpeed )
            needsUpdate = True
        elif event.code == self.keys.LEFT:
            self.__pan( self.keyPanSpeed, 0 )
            needsUpdate = True
        elif event.code == self.keys.RIGHT:
            self.__pan( - self.keyPanSpeed, 0 )
            needsUpdate = True
        
        if needsUpdate:
            self.update()

    def __handleTouchStartRotate(self):
        pass
        # if len(self.__pointers) == 1:
        #     self.__rotateStart.set( self.__pointers[0].clientX, self.__pointers[0].clientY )
        # else:
        #     x = 0.5 * ( self.__pointers[0].x + self.__pointers[1].x )
        #     y = 0.5 * ( self.__pointers[0].y + self.__pointers[1].y )

        #     self.__rotateStart.set( x, y )

    def __handleTouchStartPan(self):
        pass
        # if len(self.__pointers) == 1:
        #     self.__panStart.set( self.__pointers[0].x, self.__pointers[0].y )
        # else:
        #     x = 0.5 * ( self.__pointers[0].x + self.__pointers[1].x )
        #     y = 0.5 * ( self.__pointers[0].y + self.__pointers[1].y )

        #     self.__panStart.set( x, y )

    def __handleTouchStartDolly(self):
        pass
        # dx = self.__pointers[0].x - self.__pointers[1].x
        # dy = self.__pointers[0].y - self.__pointers[1].y

        # distance = math.sqrt( dx * dx + dy * dy )
        # self.__dollyStart.set( 0, distance )

    def __handleTouchStartDollyPan(self):
        pass
        # if self.enableZoom:
        #     self.__handleTouchStartDolly()
        # if self.enablePan:
        #     self.__handleTouchStartPan()

    def __handleTouchStartDollyRotate(self):
        pass
        # if self.enableZoom:
        #     self.__handleTouchStartDolly()
        # if self.enableRotate:
        #     self.__handleTouchStartRotate()

    def __handleTouchMoveRotate(self, event):
        pass
        # if len(self.__pointers) == 1:
        #     self.__rotateEnd.set( event.x, event.y )
        # else:
        #     position = self.__getSecondPointerPosition( event )
        #     x = 0.5 * ( event.x + position.x )
        #     y = 0.5 * ( event.y + position.y )

        #     self.__rotateEnd.set( x, y )

        # self.__rotateDelta.subVectors( self.__rotateEnd, self.__rotateStart ).multiplyScalar( self.rotateSpeed )
        
        # element = self.canvas
        # cw, ch = element.get_physical_size()

        # self.__rotateLeft( 2 * math.pi * self.__rotateDelta.x / ch ) # yes, height
        # self.__rotateUp( 2 * math.pi * self.__rotateDelta.y / ch )
        # self.__rotateStart.copy( self.__rotateEnd )

    def __handleTouchMovePan( self, event ):
        pass
        # if len(self.__pointers) == 1:
        #     self.__panEnd.set( event.x, event.y )
        # else:
        #     position = self.__getSecondPointerPosition( event )
        #     x = 0.5 * ( event.x + position.x )
        #     y = 0.5 * ( event.y + position.y )

        #     self.__panEnd.set( x, y )

        # self.__panDelta.subVectors( self.__panEnd, self.__panStart ).multiplyScalar( self.panSpeed )

        # self.__pan( self.__panDelta.x, self.__panDelta.y )
        # self.__panStart.copy( self.__panEnd )

    def __handleTouchMoveDolly( self, event ):
        pass
        # position = self.__getSecondPointerPosition( event )
        # dx = event.x - position.x
        # dy = event.y - position.y

        # distance = math.sqrt( dx * dx + dy * dy )

        # self.__dollyEnd.set( 0, distance )
        # self.__dollyDelta.set( 0, (self.__dollyEnd.y/self.__dollyStart.y)**self.zoomSpeed )
        # self.__dollyOut( self.__dollyDelta.y )
        # self.__dollyStart.copy( self.__dollyEnd )

    def __handleTouchMoveDollyPan( self, event ):
        pass
        # if self.enableZoom:
        #     self.__handleTouchMoveDolly( event )
        # if self.enablePan:
        #     self.__handleTouchMovePan( event )

    def __handleTouchMoveDollyRotate( self, event ):
        pass
        # if self.enableZoom:
        #     self.__handleTouchMoveDolly( event )
        # if self.enableRotate:
        #     self.__handleTouchMoveRotate( event )



    # event handlers
    def __onPointerDown( self, event ):
        if self.enabled == False:
            return
        
        if len(self.__pointers) == 0:
            self.bindEvent(self.__onPointerMove, "pointer_move")
            self.bindEvent(self.__onPointerUp, "pointer_up")


        self.__addPointer( event )

        if event.pointerType == 'touch':
            self.__onTouchStart(event)

        else:
            self.__onMouseDown(event)


    def __onPointerMove( self, event ):
        if self.enabled == False:
            return
        
        # if event.pointerType == 'touch':
        #     self.__onTouchMove(event)
        # else:
        self.__onMouseMove(event)


    def __onPointerUp( self, event ):
        self.__removePointer( event )

        if len(self.__pointers) == 0:
            self.removeEvent(self.__onPointerMove, "pointer_move")
            self.removeEvent(self.__onPointerUp, "pointer_up" )

        self.dispatchEvent(_endEvent)
        self.__state = STATE.NONE

    
    def __onPointerCancel( self, event ):
        self.__removePointer( event )

    def __onMouseDown( self, event ):
        mouseAction = - 1

        if event.button == 1:
            mouseAction = self.mouseButtons.LEFT
        elif event.button == 3:
            mouseAction = self.mouseButtons.MIDDLE
        elif event.button == 2:
            mouseAction = self.mouseButtons.RIGHT

        if mouseAction == MOUSE.DOLLY:
            if self.enableZoom:
                self.__handleMouseDownDolly( event )
                self.__state = STATE.DOLLY
        elif mouseAction == MOUSE.ROTATE:
            if event.ctrlKey or event.metaKey or event.shiftKey:
                if self.enablePan:
                    self.__handleMouseDownPan( event )
                    self.__state = STATE.PAN
            else:
                if self.enableRotate:
                    self.__handleMouseDownRotate( event )
                    self.__state = STATE.ROTATE
        elif mouseAction == MOUSE.PAN:
            if event.ctrlKey or event.metaKey or event.shiftKey:
                if self.enableRotate:
                    self.__handleMouseDownRotate( event )
                    self.__state = STATE.ROTATE
            else:
                if self.enablePan:
                    self.__handleMouseDownPan( event )
                    self.__state = STATE.PAN
        else:
            self.__state = STATE.NONE

        if self.__state != STATE.NONE:
            self.dispatchEvent(_startEvent)


    def __onMouseMove( self, event ):
        if self.enabled == False:
            return
        
        if self.__state == STATE.ROTATE:
            if self.enableRotate:
                self.__handleMouseMoveRotate( event )
        elif self.__state == STATE.DOLLY:
            if self.enableZoom:
                self.__handleMouseMoveDolly( event )
        elif self.__state == STATE.PAN:
            if self.enablePan:
                self.__handleMouseMovePan( event )

    def __onMouseWheel( self, event ):
        if self.enabled == False or self.enableZoom == False or self.__state != STATE.NONE:
            return
        
        self.dispatchEvent(_startEvent)
        self.__handleMouseWheel( event )
        self.dispatchEvent(_endEvent)

    def __onKeyDown( self, event ):
        if self.enabled == False or self.enablePan == False:
            return
        self.__handleKeyDown( event )


    def __onTouchStart(self, event):
        pass

    def __onTouchMove(self, event):
        pass

    def __onContextMenu(self, event):
        pass

    def __addPointer(self, event):
        self.__pointers.append(event)

    def __removePointer(self, event):
        #del self.__pointerPositions[ event.pointerId ]

        for p in self.__pointers:
            if p.pointerId == event.pointerId:
                self.__pointers.remove(p)
                break

    def __trackerPointer(self, event):
        pass

    def __getSecondPointerPosition( self, event ):
        pointer = self.__pointers[ 1 ] if event.pointerId == self.__pointers[ 0 ].pointerId else self.__pointers[ 0 ]
        return self.__pointerPositions[ pointer.pointerId ]

        # const pointer = ( event.pointerId === pointers[ 0 ].pointerId ) ? pointers[ 1 ] : pointers[ 0 ];

        # return pointerPositions[ pointer.pointerId ];

