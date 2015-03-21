"""	Permite crear una instancia que se encargara de proporcionar funciones
	facilitando el manejo del dispositivo Freescale. Entre esas funcionalidades
	con las que cuenta, tenemos la de enviar comandos mediante la UART y la de
	leer la salida del mismo.
	@author: Gonzalez Leonardo Mauricio
	@author: Reinoso Ever Denis
	@organization: UNC - Fcefyn
	@date: Lunes 16 de Febrero de 2015 """

#mport emailModule
#import modemClass

import serial
import time

class Microcontroller(object):
    """ Clase 'Microcontroller'. Permite la creacion de una instancia del dispositivo. """

    def __init__(self):
        """ Constructor de la clase 'Microcontroller'. Utiliza la API 'pySerial' de Python
            para establecer un medio de comunicacion entre el usuario y el puerto donde se
            encuentra conectada la placa. Establece un 'baudrate' y un 'timeout', donde este
            ultimo indica el intervalo de tiempo en segundos con el cual se hacen lecturas
            sobre el dispositivo. """
        self.microcontrollerInstance = serial.Serial()
        self.microcontrollerInstance.port = 'COM9'
        self.microcontrollerInstance.baudrate = 9600
        self.microcontrollerInstance.timeout = 5
        self.microcontrollerInstance.close()
        self.microcontrollerInstance.open()
        self.microcontrollerOutput = ''
        self.microcontrollerOutput_flag = False
        self.microcontrollerInstance.write('@')

    def __del__(self):
    	""" Destructor de la clase 'Microcontroller'. Cierra la conexion establecida
            con el dispositivo. """
        self.microcontrollerInstance.close()
	print 'Objeto ' + self.__class__.__name__ + ' destruido.'

    def sendCMD(self, cmd):
	""" Se encarga de enviarle un comando a la placa.
            @param cmd: comando que se quiere ejecutar
	    @type cmd: str """
        print 'Se envio a la placa el comando: ' + cmd
        self.microcontrollerInstance.write(cmd)

    def readOutput(self):
	""" Lee y devuelve lo que recibe del dispositivo Freescale.
            @return: respuesta del dispositivo, al comando ingresado
            @rtype: str """
	# Mientras la placa no envie ninguna informacion acerca de los pines GPIO...
        while not self.microcontrollerOutput_flag:
            # ... nos quedamos esperando.
            pass
        self.microcontrollerOutput_flag = False
        return self.microcontrollerOutput

    def readOutput2(self):
        print 'Esperando mensaje de kl46Z'
        while self.microcontrollerInstance.inWaiting() <= 0:
            pass
        time.sleep(0.5)
        self.microcontrollerOutput = self.microcontrollerInstance.read(self.microcontrollerInstance.inWaiting()).lower()
        print 'El mensaje recibido fue: ' + self.microcontrollerOutput
        if self.microcontrollerOutput == 'motion_on':
            #modemClass.motionSensor_flag = True
            #emailModule.motionSensor_flag = True
            print time.ctime() + ': Se ha detectado movimiento!'
        elif self.microcontrollerOutput == 'motion_off':
            print time.ctime() + ': Ya no hay movimiento!'
        elif self.microcontrollerOutput == 'light_on':
            print time.ctime() + ': Oscurecio y la lampara fue encendida!'
        elif self.microcontrollerOutput == 'light_off':
            print time.ctime() + ': Hay suficiente luz y la lampara fue apagada!'
        elif self.microcontrollerOutput == 'room01_on':
            print time.ctime() + ': La lampara de la Habitacion 01 fue encendida!'
        elif self.microcontrollerOutput == 'room01_off':
            print time.ctime() + ': La lampara de la Habitacion 01 fue apagada!'
        elif self.microcontrollerOutput == 'room02_on':
            print time.ctime() + ': La lampara de la Habitacion 02 fue encendida!'
        elif self.microcontrollerOutput == 'room02_off':
            print time.ctime() + ': La lampara de la Habitacion 02 fue apagada!'
        return self.microcontrollerOutput

    def waitOutput(self):
        """ Espera mensajes de eventos de la placa, y muestra notificaciones en pantalla
            en base a dichos eventos. En el caso del sensor de movimiento, levanta las
            banderas correspondientes para que luego, las notificaciones sean enviadas
            a los respectivos usuarios mediante algun medio de comunicacion (ya sea SMS
            o EMAIL). """
        while True:
            while self.microcontrollerInstance.inWaiting() <= 0:
                pass
            time.sleep(0.5)
            self.microcontrollerOutput = self.microcontrollerInstance.read(self.microcontrollerInstance.inWaiting()).lower()
            if self.microcontrollerOutput == 'motion_on':
                modemClass.motionSensor_flag = True
                emailModule.motionSensor_flag = True
                print time.ctime() + ': Se ha detectado movimiento!'
            elif self.microcontrollerOutput == 'motion_off':
                print time.ctime() + ': Ya no hay movimiento!'
            elif self.microcontrollerOutput == 'light_on':
                print time.ctime() + ': Oscurecio y la lampara fue encendida!'
            elif self.microcontrollerOutput == 'light_off':
                print time.ctime() + ': Hay suficiente luz y la lampara fue apagada!'
            elif self.microcontrollerOutput == 'room01_on':
                print time.ctime() + ': La lampara de la Habitacion 01 fue encendida!'
            elif self.microcontrollerOutput == 'room01_off':
                print time.ctime() + ': La lampara de la Habitacion 01 fue apagada!'
            elif self.microcontrollerOutput == 'room02_on':
                print time.ctime() + ': La lampara de la Habitacion 02 fue encendida!'
            elif self.microcontrollerOutput == 'room02_off':
                print time.ctime() + ': La lampara de la Habitacion 02 fue apagada!'
            else:
                self.microcontrollerOutput_flag = True
