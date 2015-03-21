"""     Modulo cuya finalidad es proporcionar funciones que se encarguen del envio
        y recepcion de correos electronicos. Tambien se encarga de discriminar la
        fuente del email mediante una lista de confianza, permitiendo o no manipular
        los perifericos del dispositivo Freescale.
	@author: Gonzalez Leonardo Mauricio
	@author: Reinoso Ever Denis
	@organization: UNC - Fcefyn
	@date: Lunes 16 de Febrero de 2015 """

import enums
import timerClass
import contactList
import processingModule

import time
import email
import socket
import smtplib
import imaplib

from email.mime.text import MIMEText

def initializeTimer():
        """ Crea una instancia del Timer que sera local a este modulo. Ademas, la
            pone en ejecucion. """
        global emailTimerInstance
        emailTimerInstance = timerClass.Timer('Temporizador EMAIL') # Creamos una instancia del Timer
        emailTimerInstance.start()                                  # Ponemos en ejecucion la instancia

def initializeEmail():
        """ Configura el protocolo SMTP y el protocolo IMAP. El primero se encargara
            de enviar correos electronicos, mientras que el segungo a recibirlos.
            Ambos disponen de una misma cuenta asociada a GMAIL para tales fines (y
            que esta dada en el archivo 'contactList.py'. """
        global smtpServer, imapServer
	print 'Configurando el modulo EMAIL...'
	smtpServer = smtplib.SMTP(contactList.SMTP_SERVER, contactList.SMTP_PORT)      # Establecemos servidor y puerto SMTP
	smtpServer.starttls()
	smtpServer.ehlo()
	smtpServer.login(contactList.EMAIL_SERVER, contactList.PASS_SERVER)            # Nos logueamos en el servidor SMTP
	imapServer = imaplib.IMAP4_SSL(contactList.IMAP_SERVER, contactList.IMAP_PORT) # Establecemos servidor y puerto IMAP
	imapServer.login(contactList.EMAIL_SERVER, contactList.PASS_SERVER)            # Nos logueamos en el servidor IMAP
	imapServer.select('INBOX')                                                     # Seleccionamos la Bandeja de Entrada
	socket.setdefaulttimeout(10)                                                   # Establecemos tiempo maximo antes de reintentar lectura
	print 'El modo EMAIL esta listo para usarse!'

def closeEmail():
        """ Finaliza la sesion iniciada con ambos servidores, es decir, SMTP e IMAP
            respectivamente. """
	smtpServer.close()  # Cerramos la sesion con el servidor SMTP
	imapServer.logout() # Cerramos la sesion con el servidor IMAP

def waitEmail():
        """ Funcion que se encarga de consultar el correo electronico asociado al modulo
            por algun EMAIL entrante. Envia al servidor IMAP una peticion de solicitud
            de mensajes no leidos (que por ende seran los nuevos) y que en caso de obtenerlos,
            los enviara de a uno al modulo de procesamiento para su comprobacion. Si el
            remitente del mensaje se encuentra registrado (en el archivo 'contactList.py') se
            procedera a procesar el cuerpo del EMAIL, o en caso contrario, se enviara una
            notificacion al usuario informandole que no es posible realizar la operacion solicitada.
            Tambien cada un cierto tiempo dado por el intervalo de temporizacion del Timer,
            enviara a un correo electronico dado por 'EMAIL_USER_01' un mensaje de actualizacion,
            que estara conformado por el estado de los pines GPIO del dispositivo Freescale (en
            nuestro caso, si las lamparas estan encendidas o apagadas).
            Finalmente, tambien disponemos de un sensor de movimiento y que en caso de activacion,
            este modulo se encargara de enviar una notificacion a 'EMAIL_USER_01' indicando el evento. """
        global processingResponseList, motionSensor_flag
	headerList = list()
	emailIds = list()
	while True:
		emailAmount = 0
		emailIds = ['']
		# Mientras no se haya recibido ningun correo electronico, el temporizador no haya expirado y no se haya detectado movimiento...
		while emailIds[0] == '' and not emailTimerInstance.getTimeExceeded_flag() and not motionSensor_flag:
                        # ... sigo esperando por alguno de los anteriores.
			try:
				imapServer.recent()				       # Actualizamos la Bandeja de Entrada
				result, emailIds = imapServer.search(None, '(UNSEEN)') # Buscamos emails sin leer (nuevos)
				# Ejemplo de emailIds: ['35 36 37']
			except Exception as e:					       # Timeout or something else
				print 'No hay conexion a Internet?'
		# Preguntamos si vencio el temporizador...
		if emailTimerInstance.getTimeExceeded_flag():
			emailTimerInstance.clearTimeExceeded_flag()   # Limpiamos la flag
			reportList = processingModule.reportCommand() # Obtenemos una lista con el estado de los pines GPIO
			emailSubject = 'Mensaje de actualizacion!'    # Establecemos el asunto del email
			emailMessage = time.ctime() + '\n'	      # Agregamos un 'Time Stamp' al comienzo del mensaje
			# Recorremos la lista agregando cada estado de los pines al cuerpo del email...
			for reportElement in reportList:
                                emailMessage = emailMessage + reportElement + '\n'
                        emailMessage = emailMessage[:emailMessage.rfind('\n')]           # Quita la ultima linea en blanco
			#sendEmail(contactList.EMAIL_USER_01, emailSubject, emailMessage) # Enviamos la actualizacion correspondiente
			print time.ctime() + ': Se envio una actualizacion por EMAIL!'
		# ... sino, verificamos si se ha detectado movimiento...
		elif motionSensor_flag:
                        emailSubject = 'Mensaje de deteccion de movimiento!'             # Establecemos el asunto del email
                        emailMessage = time.ctime() + ': Se ha detectado movimiento!'    # Escribimos el contenido del cuerpo del email
                        #sendEmail(contactList.EMAIL_USER_01, emailSubject, emailMessage) # Enviamos la notificacion correspondiente
                        motionSensor_flag = False                                        # Limpiamos la flag
		# ... y sino, leemos el flujo de datos recibidos.
		else:
                        # Ejemplo de emailIds: ['35 36 37']
			emailIdsList = emailIds[0].split()
			emailAmount = len(emailIdsList) # Cantidad de emails no leidos
			print 'Ha(n) llegado ' + str(emailAmount) + ' nuevo(s) mensaje(s) de correo electronico!'
			# Recorremos los emails recibidos...
			for i in emailIdsList:
				result, emailData = imapServer.fetch(i, '(RFC822)')
				rawEmail = emailData[0][1]
				emailReceived = email.message_from_string(rawEmail)
				# message_from_string() devuelve un objeto 'message', y podemos acceder a los items de su cabecera como...
				# ... si fuese un diccionario.
				headerList = processEmailHeader(emailReceived) # Almacenamos una lista con los elementos del email recibido
				sourceName = headerList[0]                     # Almacenamos el nombre del remitente
				sourceEmail = headerList[1]                    # Almacenamos el correo del remitente
				emailSubject = headerList[2]                   # Almacenamos el asunto correspondiente
				print 'Procesando correo electronico de ' + sourceName + ' - ' + sourceEmail
				# Comprobamos si el remitente del mensaje (un correo) esta registrado y tiene permiso de ejecucion...
				if contactList.allowedEmails.has_key(sourceEmail):
					emailBody = processingModule.getDecodedEmailBody(emailReceived) # Obtenemos el cuerpo del email
					processingResponse = processEmailBody(emailBody)                # Procesamos el cuerpo y obtenemos la respuesta
					processingResponseList = processingResponse.split()             # Creamos una lista con la respuesta recibida
					# Ejemplo de processingResponseList: [stemp, 50]
					# Nos fijamos si hay que ejecutar alguna funcion propia del modulo...
					if commandsDictionary.has_key(processingResponseList[0]):
						emailMessage = commandsDictionary[processingResponseList[0]]()
					# ... sino, esa misma respuesta anterior sera el mensaje a enviar.
					else:
						emailMessage = processingResponse
					# Envio el email con el mensaje SUCCESS: Descripcion, ERROR: Descripcion
					sendEmail(sourceEmail, emailSubject, emailMessage)
				# ... sino, comunicamos al usuario desconocido que no es posible realizar la operacion solicitada.
				else:
					print 'Imposible procesar la solicitud. El correo electronico no se encuentra registrado!'
					emailMessage = 'Imposible procesar la solicitud. Usted no se encuentra registrado!'
					sendEmail(sourceEmail, emailSubject, emailMessage)
				emailAmount -= 1 # Decrementamos la cantidad de emails no leidos
				if emailAmount == 0:
					break
	print 'El modo EMAIL ha terminado!'

def sendEmail(emailDestination, emailSubject, emailMessage):
        """ Envia un mensaje de correo electronico.
            @param emailDestination: correo electronico del destinatario
            @type emailDestination: str
            @param emailSubject: asunto del mensaje
            @type emailSubject: str
            @param emailMessage: correo electronico a enviar
            @type emailMessage: str """
	# Construimos un mensaje simple
	simpleMessage = MIMEText(emailMessage)
	simpleMessage['From'] = contactList.EMAIL_SERVER
	simpleMessage['To'] = emailDestination
	simpleMessage['Subject'] = emailSubject
	# Enviamos el mensaje, al correo destino correspondiente
	smtpServer.sendmail(simpleMessage['From'], simpleMessage['To'], simpleMessage.as_string())

def processEmailHeader(emailReceived):
        """ Envia a procesar la cabecera del EMAIL. Le indica al modulo de procesamiento que se trata
            de un 'EMAIL_HEADER' para que le aplique a la misma el procesamiento que corresponda. Esta
            funcion espera a que el modulo retorne una lista con los elementos de la cabecera, esto es,
            nombre del remitente, asunto del mensaje y el cuerpo del email.
            @param emailReceived: correo electronico entrante
            @type emailReceived: message
            @return: elementos de la cabecera (nombre del remitente, asunto y cuerpo del email)
            @rtype: list """
	return processingModule.cmdInput(enums.dataType.EMAIL_HEADER, emailReceived)

def processEmailBody(emailBody):
        """ Envia a procesar el cuerpo del EMAIL. Le indica al modulo de procesamiento que se trata
            de un 'EMAIL_BODY' para que le aplique a la misma el procesamiento que corresponda. Esta
            funcion espera a que el modulo retorne la salida de ese procesamiento, que estara constituida
            por un mensaje que indique si los comandos fueron ejecutados exitosamente o si eran erroneos.
            @param emailBody: cuerpo del correo electronico
            @type emailBody: str
            @return: salida del procesamiento sobre el cuerpo del EMAIL
            @rtype: str """
	return processingModule.cmdInput(enums.dataType.EMAIL_BODY, emailBody)

def setTimingInterval():
        """ Cambia el intervalo de temporizacion, es decir, la frecuencia con que el Timer envia mensajes
            de actualizacion.
            @return: mensaje de confirmacion de cambio del intervalo
            @rtype: str """
	emailTimerInstance.timingInterval = int(processingResponseList[1]) # Contiene el nuevo valor del intervalo
	emailTimerInstance.redefineInterval_flag = True			   # Indico al Timer que hay un nuevo valor para el intervalo
	return time.ctime() + ' - SUCCESS: El intervalo se cambio a ' + processingResponseList[1] + ' correctamente!'

processingResponseList = list()

commandsDictionary = dict()
commandsDictionary = {enums.specificCommands.SET_TIMING_INTERVAL : setTimingInterval}

motionSensor_flag = False

smtpServer = smtplib.SMTP
imapServer = imaplib.IMAP4_SSL
emailTimerInstance = timerClass.Timer
