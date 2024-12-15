// Bootstrap
    @256
    D=A
    @SP
    M=D
	//Call Sys.init 0
    Code assembleur de {'type': 'Call', 'function': 'Sys.init', 'parameter': '0'}


//code de test/test.vm
	// push constant 10
    @ 10
    D=A
    @SP
    A=M
    M=D
    @SP
    M=M+1
