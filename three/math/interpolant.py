from ..structure import NoneAttribute

class Interpolant(NoneAttribute):
    
    def __init__(self, parameterPositions, sampleValues, sampleSize, resultBuffer ) -> None:
        
        self.parameterPositions = parameterPositions
        self._cachedIndex = 0

        
        self.resultBuffer = resultBuffer if resultBuffer else sampleValues.__class__(sampleSize)
        self.sampleValues = sampleValues
        self.valueSize = sampleSize

        self.settings = None
        self.DefaultSettings_ = {}

    def evaluate( self, t ):
        pp = self.parameterPositions
        i1 = self._cachedIndex
        t1 = pp[ i1 ]
        t0 = pp[ i1 - 1 ]

        if t1 is None or t>= t1:
            giveUpAt = i1 + 2
            while True:
                if t1 is None:
                    if t<0: break

                    i1 = len(pp)
                    self._cachedIndex = i1
                    return self.afterEnd_( i1 - 1, t, t0 )

                if i1 == giveUpAt: break
        
        raise NotImplementedError


    def getSettings_(self):
        return self.settings or self.DefaultSettings_

    def copySampleValue_( self, index ):
        # copies a sample value to the result buffer
        result = self.resultBuffer
        values = self.sampleValues
        stride = self.valueSize
        offset = index * stride
        
        for i in range(stride):
            result[ i ] = values[ offset + i ]
        return result

    # Template methods for derived classes:

    def interpolate_( self, *args, **kargs ):
        raise NotImplementedError

    def intervalChanged_(self, *args, **kargs ):
        pass



