from .constants import GPUChunkSize


def getFloatLength( floatLength ):
	# ensure chunk size alignment (STD140 layout)
	return floatLength + ( ( GPUChunkSize - ( floatLength % GPUChunkSize ) ) % GPUChunkSize )


def getVectorLength( count, vectorLength = 4 ):
    strideLength = getStrideLength( vectorLength )

    floatLength = strideLength * count

    return getFloatLength( floatLength )


def getStrideLength( vectorLength ):

    strideLength = 4

    return vectorLength + ( ( strideLength - ( vectorLength % strideLength ) ) % strideLength )
