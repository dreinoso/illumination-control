"""	Modulo central cuya funcion principal es procesar las peticiones del Servidor
    para comunicarse con la placa
	@author: Gonzalez Leonardo Mauricio
	@author: Reinoso Ever Denis
	@organization: UNC - Fcefyn
	@date: Lunes 16 de Febrero de 2015 """

import frdmClass
import enums

import time

def reportCommand():
	""" Envia al dispositivo Freescale, los comandos correspondientes que devolveran el estado
            de los pines GPIO.
            @return: lista con el estado de los pines GPIO
            @rtype: list """
        roomStatsList = list()
        roomStatsList.append(roomCommand(enums.specificCommands.ROOM01_STATS))
        roomStatsList.append(roomCommand(enums.specificCommands.ROOM02_STATS))
        roomStatsList.append(roomCommand(enums.specificCommands.BACKYARD_STATS))
        return roomStatsList

def roomCommand(roomCommand):
	""" Envia al dispositivo Freescale, el comando que el usuario solicita ejecutar.
            @param roomCommand: comando que se quiere enviar a la placa
            @type roomCommand: str
            @return: salida devuelta por la placa
            @rtype: str """
        microcontrollerInstance.sendCMD(roomCommand)
        microcontrollerInstance.sendCMD('@')

def initializeMicrocontroller():
	""" Crea una instancia del 'Microcontroller' de Freescale. """
        global microcontrollerInstance
        microcontrollerInstance = frdmClass.Microcontroller()

processingDictionary = dict()
commandsDictionary = dict()

print 'Comenzando ProcessingModule...'
microcontrollerInstance = frdmClass.Microcontroller

#initializeMicrocontroller()
microcontrollerInstance = frdmClass.Microcontroller()

commandsDictionary = {enums.specificCommands.ROOM01_TOGGLE	 : roomCommand,
                        enums.specificCommands.ROOM01_STATS	 : roomCommand,
                        enums.specificCommands.ROOM02_TOGGLE	 : roomCommand,
                        enums.specificCommands.ROOM02_STATS	 : roomCommand}
print 'Todo listo!'