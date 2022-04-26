import re
from three.nodes import NodeFunctionInput, NodeFunction

__pragmaMain = '#pragma main'

__declarationRegexp = re.compile(r'^\s*(highp|mediump|lowp)?\s*([a-z_0-9]+)\s*([a-z_0-9]+)?\s*\((.*?)\)', flags=re.I)

__propertiesRegexp = re.compile(r'[a-z_0-9]+' , flags=re.I)

def __is_num(s:str):
    try:
        float(s)
        return True
    except:
        return False

def __parse(source:str):
    ''' glsl souce code parser

    Parameters:
        source: glsl source code

    Returns:
        ( type, inputs, name, presicion, inputsCode, blockCode, headerCode )
    '''
    
    source = source.strip()

    has_pragma_main = __pragmaMain in source

    pragmaMainIndex = source.index( __pragmaMain) if has_pragma_main else -1

    mainCode = source[source.index( __pragmaMain)+len(__pragmaMain):] if has_pragma_main else source

    declaration = __declarationRegexp.findall(mainCode)

    match = __declarationRegexp.match(mainCode)

    if match and len(match.groups()) == 4:
        # tokenizer
        inputsCode = declaration[ 3 ]
        propsMatches = __propertiesRegexp.findall(inputsCode)

        # parser
        inputs = []
        i = 0
        while i< len(propsMatches):

            isConst = propsMatches[i] == 'const'
            if isConst:
                i+=1
            
            qualifier = propsMatches[i]

            if qualifier == 'in' or qualifier == 'out' or qualifier == 'inout':
                i+=1
            else:
                qualifier = ''

            type = propsMatches[i]
            i+=1

                
            count = propsMatches[i]
            if __is_num(count):
                i+=1
                count = int(count)
            else:
                count = None
            
            name = propsMatches[i]
            i+=1
            
            inputs.append( NodeFunctionInput( type, name, count, qualifier, isConst ) )



        blockCode = mainCode[len(match.group()):]

        name = declaration[ 2 ] if declaration[ 2 ] is not None else ''
        type = declaration[ 1 ]

        presicion = declaration[ 0 ] if declaration[ 0 ] is not None else ''

        headerCode = source[:pragmaMainIndex] if has_pragma_main else ''

        return (
			type,
			inputs,
			name,
			presicion,
			inputsCode,
			blockCode,
			headerCode
        )

        # return {
		# 	'type' : type,
		# 	'inputs' : inputs,
		# 	'name' : name,
		# 	'presicion': presicion,
		# 	'inputsCode': inputsCode,
		# 	'blockCode': blockCode,
		# 	'headerCode': headerCode
		# }

    else:
        raise Exception( 'FunctionNode: Function is not a GLSL code.' )


class GLSLNodeFunction(NodeFunction):

    def __init__(self, source) -> None:
        #p = parse(source)
        type, inputs, name, presicion, inputsCode, blockCode, headerCode = __parse( source )
        super().__init__(type, inputs, name=name, presicion=presicion)

        self.inputsCode = inputsCode
        self.blockCode = blockCode
        self.headerCode = headerCode

    def getCode( self, name = None):
        if not name:
            name = self.name
        headerCode = self.headerCode
        presicion = self.presicion

        declarationCode = f"{ self.type } { name } ( { self.inputsCode.strip() } )"

        if presicion != '' :
            declarationCode = f"{ presicion } { declarationCode }"

        return headerCode + declarationCode + self.blockCode
