import re
from ..core.node_function_input import NodeFunctionInput
from ..core.node_function import NodeFunction

__declarationRegexp = re.compile(r'^[fn]*\s*([a-z_0-9]+)?\s*\(([\s\S]*?)\)\s*[\-\>]*\s*([a-z_0-9]+)?', flags=re.I)

__propertiesRegexp = re.compile(r'[a-z_0-9]+', flags=re.I)

wgslTypeLib = {
	'f32': 'float'
}

def _parse( source: str ):
    ''' wlsl souce code parser

    Parameters:
        source: wlsl source code

    Returns:
        ( type, inputs, name, inputsCode, blockCode )
    '''
    source = source.strip()
    declaration = __declarationRegexp.findall(source)[0]

    match = __declarationRegexp.match(source)

    if match and len(match.groups()) == 3:
        # tokenizer
        inputsCode = declaration[ 1 ]
        propsMatches = __propertiesRegexp.findall(inputsCode)

        # parser

        inputs = []
        i = 0
        while i< len(propsMatches):

            name = propsMatches[ i ]
            i += 1
            type = propsMatches[ i ]
            type = wgslTypeLib[type] or type
            i += 1

            #precision = propsMatches[ i ]

            # precision
            if i< len(propsMatches) and re.compile('^[fui]\d{2}$').match( propsMatches[ i ]):
                i += 1

            inputs.append( NodeFunctionInput( type, name) )

        blockCode = source[len(match.group()):]
        name = declaration[ 0 ] if declaration[ 0 ] is not None else ''
        type = declaration[ 2 ] or 'void'

        return (
            type,
            inputs,
            name,
            inputsCode,
            blockCode
        )
    else:
        raise Exception( 'FunctionNode: Function is not a WGSL code.' )


class WGSLNodeFunction(NodeFunction):

    def __init__(self, source) -> None:
        #p = parse(source)
        type, inputs, name, inputsCode, blockCode = _parse( source )
        super().__init__(type, inputs, name=name)

        self.inputsCode = inputsCode
        self.blockCode = blockCode

    def getCode( self, name = None):
        if not name:
            name = self.name
        
        #return f"fn { name } ( { self.inputsCode.strip() } ) -> { self.type }" + self.blockCode
        type = '-> ' + self.type if self.type != 'void' else ''
        return f"fn { name } ( { self.inputsCode.strip() } ) { type }" + self.blockCode
        #return f"fn { name } ( { self.inputsCode.strip() } ) -> { self.type } {self.blockCode}"