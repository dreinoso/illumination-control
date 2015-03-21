"""	Programa principal, que brinda al usuario la posibilidad de elegir
	el modo de operacion (ya sea Sms o Email, o ambos). Se encarga de
	generar la instancia del microcontrolador Freescale, como asi tambien
	los objetos que hagan falta para el correcto funcionamiento de la
	aplicacion.
	@author: Gonzalez Leonardo Mauricio
	@author: Reinoso Ever Denis
	@organization: UNC - Fcefyn
	@date: Lunes 16 de Febrero de 2015 """

import modemClass
import timerClass
import emailModule
import processingModule

import os
import sys
import time
import threading
import multiprocessing

def smsMode():
	""" Crea una instancia del modem, ademas de una instancia de temporizacion.
            Pone en ejecucion el temporizador, y envia al modem a esperar un SMS. """
        modemInstance = modemClass.Sms()
        modemInstance.initializeTimer()
        modemInstance.waitSms()

def emailMode():
	""" Configura el modulo de manejo de email, ademas de una instancia de temporizacion.
            Pone en ejecucion el temporizador, y envia al modulo a esperar un EMAIL. """
        emailModule.initializeEmail()
        emailModule.initializeTimer()
        emailModule.waitEmail()

def doubleMode():
	""" Crea dos hilos, que se encargaran de ejecutar las funciones de manejo de SMS y de
            EMAIL. Una vez creados, los pone en ejecucion. """
        smsThread = threading.Thread(name = 'smsThread', target = smsMode)
        emailThread = threading.Thread(name = 'emailThread', target = emailMode)
        smsThread.start()
        emailThread.start()
        smsThread.join()
        emailThread.join()

def microcontrollerMode():
	""" Envia al microcontrolador a esperar eventos de los perifericos conectados. """
        processingModule.microcontrollerInstance.waitOutput()

def main():
	""" Presenta al usuario una interfaz que le permitira seleccionar el
            modo de operacion. """
        smsThread = threading.Thread(name = 'smsThread', target = smsMode)
        emailThread = threading.Thread(name = 'emailThread', target = emailMode)
        doubleThread = threading.Thread(name = 'doubleThread', target = doubleMode)
        microcontrollerThread = threading.Thread(name = 'microcontrollerThread', target = microcontrollerMode)
	processingModule.initializeMicrocontroller()
	try:
		#os.system('cls')
		print '----------- MODULO DE COMUNICACION -----------\n'
		print '\t\t1 - Modo SMS'
		print '\t\t2 - Modo EMAIL'
		print '\t\t3 - Modo doble'
		print '\t\t4 - Salir'
		selectedMode = raw_input('\n\t\tOpcion: ')
		#os.system('cls')
		if selectedMode == '1':
                        smsThread.start()
                        microcontrollerThread.start()
			microcontrollerThread.join()
                        smsThread.join()
		elif selectedMode == '2':
			emailThread.start()
			microcontrollerThread.start()
			microcontrollerThread.join()
			emailThread.join()
		elif selectedMode == '3':
                        microcontrollerThread.start()
                        doubleThread.start()
                        microcontrollerThread.join()
                        doubleThread.join()
		elif selectedMode == '4':
			sys.exit()
	except KeyboardInterrupt:
                pass
        time.sleep(0.5)
	print '\n---------------- UNC - Fcefyn ----------------'
	print '---------- Ingenieria en Computacion ---------'
	sys.exit()

if __name__ == '__main__':
	main()
