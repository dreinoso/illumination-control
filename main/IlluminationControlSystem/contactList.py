"""	Contiene los numeros que se van a usar para configurar el modem GSM, como
        asi tambien los parametros necesarios para configurar el servicio de email.
        Tambien se encuentra almacenada una lista de confianza cuyo contenido son
        los numeros telefonicos e emails que tendran autorizacion a operar con el
        programa y el dispositivo Freescale.
	@author: Gonzalez Leonardo Mauricio
	@author: Reinoso Ever Denis
	@organization: UNC - Fcefyn
	@date: Lunes 16 de Febrero de 2015 """

CLARO_MESSAGES_CENTER = 543200000001
CLARO_WEB_PAGE = 876966
DESTINATION_NUMBER = 3512560536

SMTP_SERVER = 'smtp.gmail.com'
IMAP_SERVER = 'imap.gmail.com'
SMTP_PORT = 587
IMAP_PORT = 993

EMAIL_SERVER = 'servidorcentral.datalogger@gmail.com'
PASS_SERVER  = 'servidorcentral1234'

EMAIL_USER_01 = 'mauriciolg.90@gmail.com'
EMAIL_USER_02 = 'deinoso.denis@gmail.com'
EMAIL_USER_03 = 'mauriciolg_90@hotmail.com'

allowedNumbers = dict()
allowedNumbers = {3512560536 : 'Mauricio Gonzalez',
                  3512650513 : 'Denis Reinoso'}

allowedEmails = dict()
allowedEmails = {'mauriciolg.90@gmail.com' : 'Mauricio Gonzalez',
                 'reinoso.denis@gmail.com' : 'Denis Reinoso',
                 'mauriciolg_90@hotmail.com' : 'Mauricio Gonzalez'}
