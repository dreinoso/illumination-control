"""	Permite crear una instancia que se encargara de proporcionar funciones
	facilitando el manejo del modem. Entre las funcionalidades basicas con
	las que cuenta, tenemos principalmente el envio y recepcion de mensajes
	SMS.
	@author: Gonzalez Leonardo Mauricio
	@author: Reinoso Ever Denis
	@organization: UNC - Fcefyn
	@date: Lunes 16 de Febrero de 2015 """

import enums
import timerClass
import contactList
import processingModule

import time
import subprocess
import serial

from curses import ascii # Para enviar el Ctrl-Z

class Modem(object):
	""" Clase 'Modem'. Permite la creacion de una instancia del dispositivo. """
	commandsDictionary = dict()
	modemTimerInstance = timerClass.Timer
	
	def __init__(self):
		""" Constructor de la clase 'Modem'. Utiliza la API 'pySerial' de
                    Python para establecer un medio de comunicacion entre el usuario
                    y el puerto donde se encuentra conectado el modem. Establece un
                    'baudrate' y un 'timeout', donde este ultimo indica el intervalo
                    de tiempo en segundos con el cual se hacen lecturas sobre el
                    dispositivo. """
		self.modemInstance = serial.Serial()
		self.modemInstance.port = 'COM7'
		self.modemInstance.baudrate = 9600
		self.modemInstance.timeout = 5
		self.modemInstance.close()
		self.modemInstance.open()
		self.sendAT('ATZ\r')  # Enviamos un reset al modem
		self.sendAT('ATE1\r') # Habilitamos el echo
		
	def __del__(self):
		""" Destructor de la clase 'Modem'. Cierra la conexion establecida
                    con el modem. """
		self.modemInstance.close()
		print 'Objeto ' + self.__class__.__name__ + ' destruido.'
		
	def sendAT(self, atCommand):
		""" Se encarga de enviarle un comando AT el modem. Espera la respuesta
                    a ese comando, antes de continuar.
                    @param atCommand: comando AT que se quiere ejecutar
                    @type atCommand: str
                    @return: respuesta del modem, al comando AT ingresado
                    @rtype: list """
		self.modemInstance.write(atCommand)   # Envio el comando AT al modem
		return self.modemInstance.readlines() # Espero la respuesta, y la devuelvo

class Sms(Modem):
	""" Subclase de 'Modem' correspondiente al modo de operacion con el que se va
            a trabajar. """
	smsAmount = 0
	smsHeader = ''
	smsBody = ''
	smsMessage = ''
	processingResponse = ''
	telephoneNumber = 1234567890

	receptionList = list()
	smsHeaderList = list()
	smsBodyList = list()
	processingResponseList = list()

	def __init__(self):
		""" Constructor de la clase 'Sms'. Configura el modem para operar en modo mensajes
                    de texto, indica el sitio donde se van a almacenar los mensajes recibidos,
                    habilita notificacion para los SMS entrantes y establece el numero del centro
                    de mensajes CLARO para poder enviar mensajes de texto (este campo puede variar
                    dependiendo de la compania de telefonia de la tarjeta SIM). """
		print 'Configurando el modem GSM...'
		Modem.__init__(self)
		self.sendAT('AT+CMGF=1\r')						   # Modo para Sms
		self.sendAT('AT+CPMS="ME","ME","ME"\r')					   # Lugar de almacenamiento de los mensajes
		self.sendAT('AT+CNMI=1,1,0,0,0\r')					   # Habilito notificacion de mensaje entrante
		self.sendAT('AT+CSCA="+' + str(contactList.CLARO_MESSAGES_CENTER) + '"\r') # Centro de mensajes CLARO
		print 'El modo SMS esta listo para usarse!'
		
	def initializeTimer(self):
                """ Crea una instancia del Timer que sera local a esta clase. Ademas, la
                    pone en ejecucion. """
		self.modemTimerInstance = timerClass.Timer('Temporizador SMS') # Creamos una instancia del Timer
		self.modemTimerInstance.start()				       # Iniciamos el Timer

	def setTimingInterval(self):
                """ Cambia el intervalo de temporizacion, es decir, la frecuencia con que el Timer envia mensajes
                    de actualizacion.
                    @return: mensaje de confirmacion de cambio del intervalo
                    @rtype: str """
		self.modemTimerInstance.timingInterval = int(self.processingResponseList[1]) # Contiene el nuevo valor del intervalo
		self.modemTimerInstance.redefineInterval_flag = True			     # Indico al Timer que hay un nuevo valor para el intervalo
		return time.ctime() + ' - SUCCESS: El intervalo se cambio a ' + self.processingResponseList[1] + ' correctamente!'

	def waitSms(self):
		""" Funcion que se encarga consultar al modem por algun mensaje SMS entrante. Envia al
                    mismo el comando AT que devuelve los mensajes de texto no leidos (que por ende seran
                    los nuevos) y que en caso de obtenerlos, los envia de a uno al modulo de procesamiento
                    para su examen. Si el remitente del mensaje se encuentra registrado (en el archivo
                    'contactList') se procede a procesar el cuerpo del SMS, o en caso contrario, se envia
                    una notificacion informandole que no es posible realizar la operacion solicitada.
                    Tambien cada un cierto tiempo dado por el intervalo de temporizacion del Timer, enviara
                    a un numero de telefono dado por 'DESTINATION_NUMBER' un mensaje de actualizacion, que
                    estara conformado por el estado de los pines GPIO del dispositivo Freescale (en nuestro
                    caso, si las lamparas estan encendidas o apagadas).
                    Finalmente, tambien disponemos de un sensor de movimiento y que en caso de activacion,
                    este modulo se encargara de enviar una notificacion a 'DESTINATION_NUMBER' indicando el
                    evento. """
		global motionSensor_flag
		while True:
			# Mientras no se haya recibido ningun mensaje de texto, el temporizador no haya expirado y no se haya detectado movimiento...
			while self.smsAmount == 0 and not self.modemTimerInstance.getTimeExceeded_flag() and not motionSensor_flag:
				# ... sigo esperando por alguno de los anteriores.
				self.receptionList = self.sendAT('AT+CMGL="REC UNREAD"\r')
				# Ejemplo de receptionList[0]: AT+CMGL="REC UNREAD"\r\r\n
				# Ejemplo de receptionList[1]: +CMGL: 0,"REC UNREAD","+5493512560536",,"14/10/26,17:12:04-12"\r\n
				# Ejemplo de receptionList[2]: primero\r\n
				# Ejemplo de receptionList[3]: +CMGL: 1,"REC UNREAD","+5493512560536",,"14/10/26,17:15:10-12"\r\n
				# Ejemplo de receptionList[4]: segundo\r\n
				# Ejemplo de receptionList[5]: \r\n
				# Ejemplo de receptionList[6]: OK\r\n
				for receptionIndex, receptionElement in enumerate(self.receptionList):
					if receptionElement.startswith('+CMGL'):
						self.smsHeader = self.receptionList[receptionIndex]
						self.smsBody = self.receptionList[receptionIndex + 1]
						self.smsHeaderList.append(self.smsHeader)
						self.smsBodyList.append(self.smsBody)
						self.smsAmount += 1
					elif receptionElement.startswith('OK'):
						break
				# Ejemplo de smsHeaderList[0]: +CMGL: 0,"REC UNREAD","+5493512560536",,"14/10/26,17:12:04-12"\r\n
				# Ejemplo de smsBodyList[0]  : primero\r\n
				# Ejemplo de smsHeaderList[1]: +CMGL: 1,"REC UNREAD","+5493512560536",,"14/10/26,17:15:10-12"\r\n
				# Ejemplo de smsBodyList[1]  : segundo\r\n
			# Preguntamos si vencio el temporizador...
			if self.modemTimerInstance.timeExceeded_flag:
				self.modemTimerInstance.clearTimeExceeded_flag()   # Limpiamos la flag
				self.reportList = processingModule.reportCommand() # Obtenemos una lista con el estado de los pines GPIO
				self.smsMessage = time.ctime() + '\n'		   # Agregamos un 'Time Stamp' al comienzo del mensaje
				# Recorremos la lista agregando cada estado de los pines al cuerpo del Sms...
				for reportElement in self.reportList:
                                        self.smsMessage = self.smsMessage + reportElement + '\n'
                                self.smsMessage = self.smsMessage[:self.smsMessage.rfind('\n')] # Quita la ultima linea en blanco
				#self.sendSms(contactList.DESTINATION_NUMBER, self.smsMessage)   # Enviamos la actualizacion correspondiente
				print time.ctime() + ': Se envio una actualizacion por SMS!'
			# ... sino, verificamos si se ha detectado movimiento...
                        elif motionSensor_flag:
                                self.smsMessage = time.ctime() + ': Se ha detectado movimiento!' # Escribimos el contenido del cuerpo del Sms
                                #self.sendSms(contactList.DESTINATION_NUMBER, self.smsMessage)    # Enviamos la notificacion correspondiente
                                motionSensor_flag = False                                        # Limpiamos la flag
			# ... sino, leemos los mensajes de texto recibidos.
			else:
				print 'Ha(n) llegado ' + str(self.smsAmount) + ' nuevo(s) mensaje(s) de texto!'
				for self.smsHeader, self.smsBody in zip(self.smsHeaderList, self.smsBodyList):
					# Ejemplo smsHeader: +CMGL: 0,"REC UNREAD","+5493512560536",,"14/10/26,17:12:04-12"\r\n
					# Ejemplo smsBody  : primero\r\n
					self.telephoneNumber = self.processSmsHeader() # Obtenemos el numero de telefono
					print 'Procesando mensaje de texto de ' + str(self.telephoneNumber)
					# Comprobamos si el remitente del mensaje (un telefono) esta registrado y tiene permiso de ejecucion...
					if contactList.allowedNumbers.has_key(self.telephoneNumber):
						print 'El numero telefonico pertenece a ' + contactList.allowedNumbers.get(self.telephoneNumber)
						self.processingResponse = self.processSmsBody() # Procesamos el cuerpo del Sms y obtenemos la respuesta
						self.processingResponseList = self.processingResponse.split()
						# Ejemplo de processingResponseList: [stemp, 50]
						# Nos fijamos si hay que ejecutar alguna funcion del modem...
						if self.commandsDictionary.has_key(self.processingResponseList[0]):
							self.smsMessage = self.commandsDictionary[self.processingResponseList[0]](self)
						# ... sino recibo la respuesta del comando que fue enviado a procesar.
						else:
							self.smsMessage = self.processingResponse
						# Envio el Sms con el mensaje SUCCESS: Descripcion, ERROR: Descripcion
						#self.sendSms(self.telephoneNumber, self.smsMessage)
					# ... caso contrario, verificamos si el mensaje proviene de la pagina web de CLARO...
					elif contactList.CLARO_WEB_PAGE == self.telephoneNumber:
						print 'No es posible procesar mensajes enviados desde la pagina web!'
					# ... sino, comunicamos al usuario desconocido que no es posible realizar la operacion solicitada.
					else:
						print 'Imposible procesar la solicitud. El numero no se encuentra registrado!'
						self.smsMessage = 'Imposible procesar la solicitud. Usted no se encuentra registrado!'
						#self.sendSms(self.telephoneNumber, self.smsMessage)
					self.smsAmount -= 1 # Decrementamos la cantidad de Sms no leidos
					if self.smsAmount == 0:
						self.smsHeaderList = []
						self.smsBodyList = []
						self.removeSms()
						break
		print 'El modo SMS ha terminado!'

	def sendSms(self, telephoneNumber, smsMessage):
		""" Envia el comando AT correspondiente para enviar un mensaje de texto.
                    @param telephoneNumber: numero de telefono del destinatario
                    @type telephoneNumber: int
                    @param smsMessage: mensaje de texto a enviar
                    @type smsMessage: str """
		self.sendAT('AT+CMGS="' + str(telephoneNumber) + '"\r') # Numero al cual enviar el Sms  
		self.sendAT(smsMessage + ascii.ctrl('z'))               # Mensaje de texto terminado en Ctrl+Z

	def removeSms(self):
		""" Envia el comando AT correspondiente para elimiar todos los mensajes del dispositivo.
                    El comando AT tiene una serie de parametros, que dependiendo de cada uno de ellos
                    indicara cual de los mensajes se quiere eliminar. En nuestro caso le indicaremos
                    que elimine los mensajes leidos y los mensajes enviados, ya que fueron procesados
                    y no los requerimos mas (ademas necesitamos ahorrar memoria, debido a que la misma
                    es muy limitada). """
		self.sendAT('AT+CMGD=1,2\r') # Elimina todos los mensajes leidos y enviados

	def processSmsHeader(self):
		""" Envia a procesar la cabecera del SMS. Le indica al modulo de procesamiento que se trata
                    de un 'SMS_HEADER' para que le aplique a la misma el procesamiento que corresponda. Esta
                    funcion espera a que el modulo retorne el numero de telefono del usuario remitente, para
                    asi verificar si el mismo se encuentra registrado o no.
                    @return: numero de telefono del usuario remitente
                    @rtype: int """
		return processingModule.cmdInput(enums.dataType.SMS_HEADER, self.smsHeader)

	def processSmsBody(self):
		""" Envia a procesar el cuerpo del SMS. Le indica al modulo de procesamiento que se trata de
                    un 'SMS_BODY' para que le aplique al mismo el procesamiento que corresponda. Esta funcion
                    espera a que el modulo retorne la salida de ese procesamiento, que estara constituida por
                    un mensaje de texto que indique si los comandos fueron ejecutados exitosamente o si eran
                    erroneos.
                    @return: salida del procesamiento sobre el cuerpo del SMS
                    @rtype: str """
		return processingModule.cmdInput(enums.dataType.SMS_BODY, self.smsBody)

	commandsDictionary = {enums.specificCommands.SET_TIMING_INTERVAL : setTimingInterval}

motionSensor_flag = False
