"""Normalized pointer control and simulator matching the firmware state machine."""
import math

def coordinate(position, extent):
    return round(max(0, min(100, position)) * max(0, extent - 1) / 100)

class TouchEngine:
    def __init__(self):
        self.x = self.y = self.tx = self.ty = 200.
        self.left = self.right = self.active = False
        self.mode = 'X'
        self.position = -1
        self.speed = 3.0  # maximum screen widths/heights per second
        self.smoothing = .045
        self.sensitivity = 1.0  # response curve, preserves both endpoints
        self.edge = 1.0  # percent endpoint snap zone
        self.deadband = .4  # percent jitter rejection
        self._size = None
        self._needs_anchor = False
        self._anchor = None
        self._pickup = False
        self._last_input = None

    def configure(self, *, speed=None, smoothing=None, sensitivity=None, edge=None):
        for key, value, low, high in [('speed',speed,.25,8.), ('smoothing',smoothing,0.,.25),
                                      ('sensitivity',sensitivity,.3,3.), ('edge',edge,0.,5.)]:
            if value is not None:
                value = float(value)
                if not math.isfinite(value): raise ValueError('Non-finite pointer setting')
                setattr(self,key,max(low,min(high,value)))

    def resize(self, width, height):
        size = (max(1,width),max(1,height))
        if self._size is not None and size != self._size:
            old_w,old_h = self._size
            self.x *= (size[0]-1)/max(1,old_w-1)
            self.tx *= (size[0]-1)/max(1,old_w-1)
            self.y *= (size[1]-1)/max(1,old_h-1)
            self.ty *= (size[1]-1)/max(1,old_h-1)
        self._size = size
        self.x = max(0.,min(size[0]-1.,self.x))
        self.y = max(0.,min(size[1]-1.,self.y))

    def _mode(self, mode):
        if self.mode != mode:
            self.mode = mode
            self.tx,self.ty = self.x,self.y
            self._needs_anchor = True
            self._anchor = None
            self._pickup = False
            self._last_input = None

    def _curve(self, pos):
        if pos <= self.edge: return 0.
        if pos >= 100-self.edge: return 1.
        n = pos/100
        return .5+math.copysign(.5*(2*abs(n-.5))**(1/self.sensitivity),n-.5)

    @property
    def pickup(self):
        return self._pickup

    def apply(self, e, width, height):
        self.resize(width,height)
        kind = e['type']
        if kind == 'MOVE':
            self._mode(e['mode'])
            self.active = True
            self.position = e['position']
            p = self._curve(self.position)
            extent = max(1,(width if self.mode=='X' else height)-1)
            current = (self.x if self.mode=='X' else self.y)/extent
            if self._needs_anchor:
                self._needs_anchor = False
                self._anchor = (p,current)
                self._pickup = p in (0.,1.) and abs(p-current)>.02
                self._last_input = self.position
                return None  # First position on the new axis is a reference, never a jump.
            if self._last_input is not None and abs(self.position-self._last_input)<self.deadband:
                return None
            self._last_input = self.position
            if self._anchor is not None:
                origin,reference = self._anchor
                if self._pickup:
                    # An endpoint anchor has no range on one side; wait for pickup.
                    if (origin<reference and p<reference) or (origin>reference and p>reference): return None
                    self._pickup = False
                    self._anchor = None
                elif 0<origin<1:
                    p = p/origin*reference if p<=origin else reference+(p-origin)/(1-origin)*(1-reference)
            if self.mode=='X': self.tx = p*max(0,width-1)
            else: self.ty = p*max(0,height-1)
        elif kind=='MODE':
            self._mode(e['mode'])
        elif kind=='RELEASE':
            self.active = False
            self.position = -1
            self._last_input = None
            self.tx,self.ty = self.x,self.y
        elif kind in ('LEFT_CLICK','RIGHT_CLICK'):
            key = 'left' if kind=='LEFT_CLICK' else 'right'
            state = bool(e['state'])
            if getattr(self,key)!=state:
                setattr(self,key,state)
                return key,state
        elif kind=='STATUS':
            self._mode(e['mode'])
            if e.get('position')==-1:
                self.active = False
                self.position = -1
                self._last_input = None
                self.tx,self.ty = self.x,self.y
            # Recover a lost UP without inventing a DOWN on reconnect.
            if self.left and not e['b2']:
                self.left = False
                return 'left',False
        return None

    def step(self, dt, width, height):
        self.resize(width,height)
        dt = max(0,dt)
        alpha = 1 if self.smoothing==0 else 1-math.exp(-dt/self.smoothing)
        self.tx = max(0.,min(width-1.,self.tx))
        self.ty = max(0.,min(height-1.,self.ty))
        for value,target,extent in [('x','tx',width),('y','ty',height)]:
            old = getattr(self,value)
            delta = (getattr(self,target)-old)*alpha
            limit = self.speed*max(0,extent-1)*dt
            setattr(self,value,old+max(-limit,min(limit,delta)))
        return self.x,self.y

    def reset(self):
        self.left = self.right = self.active = False
        self.tx,self.ty = self.x,self.y
        self.mode = 'X'
        self.position = -1
        self._needs_anchor = True
        self._anchor = None
        self._pickup = False
        self._last_input = None

class GestureSimulator:
    """Same debounce, edge priorities and timing as firmware/gesture.c."""
    def __init__(self):
        self.candidate = [False,False]
        self.stable = [False,False]
        self.since = [0,0]
        self.vertical = self.slider = False
        self.position = 0
        self.last_mode = 'X'
        self.last_move = 0
        self.seq = 0

    def sample(self, ms, b1, b2, position):
        ms &= 0xffffffff
        out = []
        def emit(kind, **fields):
            out.append(dict(v=1,seq=self.seq,type=kind,**fields))
            self.seq = (self.seq+1)&0xffffffff
        edges = [False,False]
        for i,raw in enumerate((b1,b2)):
            if raw!=self.candidate[i]: self.candidate[i],self.since[i] = raw,ms
            if self.stable[i]!=raw and ((ms-self.since[i])&0xffffffff)>=30:
                self.stable[i],edges[i] = raw,True
        if edges[0] and self.stable[0]:
            self.vertical = not self.vertical
            emit('MODE',mode='Y' if self.vertical else 'X')
        mode = 'Y' if self.vertical else 'X'
        for i,edge in enumerate(edges):
            if edge: emit('BUTTON',button=i+1,state=int(self.stable[i]))
        if edges[1]: emit('LEFT_CLICK',state=int(self.stable[1]))
        if 0<=position<=100:
            if (not self.slider or position!=self.position or mode!=self.last_mode) and (
                    not self.slider or mode!=self.last_mode or ((ms-self.last_move)&0xffffffff)>=20):
                emit('MOVE',position=position,mode=mode)
                self.position,self.last_move,self.last_mode = position,ms,mode
            self.slider = True
        elif self.slider:
            self.slider = False
            emit('RELEASE')
        return out
