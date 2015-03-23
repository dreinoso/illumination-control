#Archivo de pruebas
cadena = 'hola'

def funcion1():
	global cadena 
	cadena ='no es hola'
	print cadena

def funcion2():
	print cadena
	global cadena
	cadena ='otra cosa'



funcion1()
funcion2()
print cadena