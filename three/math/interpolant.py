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

                    i1 = pp.length
                    self._cachedIndex = i1
                    return self.afterEnd_( i1 - 1, t, t0 )

                if i1 == giveUpAt: break
        
        raise NotImplementedError


		# validate_interval: {
		# 	seek: {
		# 		let right;
		# 		linear_scan: {
		# 			# See http://jsperf.com/comparison-to-undefined/3
		# 			# slower code:
		# 			#
		# 			#- 				if ( t >= t1 || t1 === undefined ) {
		# 			forward_scan: if ( ! ( t < t1 ) ) {

		# 				for ( let giveUpAt = i1 + 2; ; ) {

		# 					if ( t1 === undefined ) {

		# 						if ( t < t0 ) break forward_scan;

		# 						# after end

		# 						i1 = pp.length;
		# 						this._cachedIndex = i1;
		# 						return this.afterEnd_( i1 - 1, t, t0 );

		# 					}

		# 					if ( i1 === giveUpAt ) break; # this loop

		# 					t0 = t1;
		# 					t1 = pp[ ++ i1 ];

		# 					if ( t < t1 ) {

		# 						// we have arrived at the sought interval
		# 						break seek;

		# 					}

		# 				}

		# 				// prepare binary search on the right side of the index
		# 				right = pp.length;
		# 				break linear_scan;

		# 			}

		# 			//- slower code:
		# 			//-					if ( t < t0 || t0 === undefined ) {
		# 			if ( ! ( t >= t0 ) ) {

		# 				// looping?

		# 				const t1global = pp[ 1 ];

		# 				if ( t < t1global ) {

		# 					i1 = 2; // + 1, using the scan for the details
		# 					t0 = t1global;

		# 				}

		# 				// linear reverse scan

		# 				for ( let giveUpAt = i1 - 2; ; ) {

		# 					if ( t0 === undefined ) {

		# 						// before start

		# 						this._cachedIndex = 0;
		# 						return this.beforeStart_( 0, t, t1 );

		# 					}

		# 					if ( i1 === giveUpAt ) break; // this loop

		# 					t1 = t0;
		# 					t0 = pp[ -- i1 - 1 ];

		# 					if ( t >= t0 ) {

		# 						// we have arrived at the sought interval
		# 						break seek;

		# 					}

		# 				}

		# 				// prepare binary search on the left side of the index
		# 				right = i1;
		# 				i1 = 0;
		# 				break linear_scan;

		# 			}

		# 			// the interval is valid

		# 			break validate_interval;

		# 		} // linear scan

		# 		// binary search

		# 		while ( i1 < right ) {

		# 			const mid = ( i1 + right ) >>> 1;

		# 			if ( t < pp[ mid ] ) {

		# 				right = mid;

		# 			} else {

		# 				i1 = mid + 1;

		# 			}

		# 		}

		# 		t1 = pp[ i1 ];
		# 		t0 = pp[ i1 - 1 ];

		# 		// check boundary cases, again

		# 		if ( t0 === undefined ) {

		# 			this._cachedIndex = 0;
		# 			return this.beforeStart_( 0, t, t1 );

		# 		}

		# 		if ( t1 === undefined ) {

		# 			i1 = pp.length;
		# 			this._cachedIndex = i1;
		# 			return this.afterEnd_( i1 - 1, t0, t );

		# 		}

		# 	} // seek

		# 	this._cachedIndex = i1;

		# 	this.intervalChanged_( i1, t0, t1 );

		# } // validate_interval

        return self.interpolate_( i1, t0, t, t1 )

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



