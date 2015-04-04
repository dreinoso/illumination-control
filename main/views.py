# encoding=utf8  

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext, loader

from IlluminationControlSystem import processingModule, emailModule
import threading
import time

running = False
led1State ='apagado'
led2State ='apagado'
backyardState ='apagado'
global events
events = list()
emailModule.initializeEmail()
print 'Vistas Configuradas'

def index(request):
    """Esta es la vista del Indice solo carga el html"""
    print "Estas en el Index"
    return render_to_response('main/index.html')

def startAplication(request):
    """Se inicia la aplicación es decir se llama a la función waitEvents, dicha función
    no retorna por lo que se queda en ese estado esperando eventos. Al hacer click de nuevo
    ya no llama a waitEvents, solo retorna el html de la aplicación corriendo."""
    global running,eventThread,emailModule,led1State,led2State,backyardState,events
    if not running:
        processingModule.roomCommand("room01_stats")
        processingModule.roomCommand("room02_stats")
        processingModule.roomCommand("backyard_stats")
        running = True
        waitEvents(request)
    return render_to_response("main/running.html",{"led1State": led1State, "led2State": led2State, "backyardState": backyardState, "events": events})

def switchLed1(request):
    """Se cambia el Led 1 mandandole el comando a la placa, y se levanta una pagina que
    informa justamente esto. Luego en la pagina se redirige despues de un segundo a la 
    plantilla running que muestra el estado del sistema"""
    processingModule.roomCommand("room01_toggle")
    return render_to_response("main/switchLed1.html")
       
def switchLed2(request):
    """Se cambia el Led 2 mandandole el comando a la placa, y se levanta una pagina que
    informa justamente esto. Luego en la pagina se redirige despues de un segundo a la 
    plantilla running que muestra el estado del sistema"""
    processingModule.roomCommand("room02_toggle")
    return render_to_response("main/switchLed2.html")
 
def about(request):
    """Solo muestra información de la página"""
    return HttpResponse("<center>Este trabajo corresponde a un desarrollo de domótica para \
    	el control de iluminación de una vivienda <br><br> Autores:<br>&nbsp   \
    	Gonzalez L. Mauricio (mauricio.lg@gmail.com)<br>&nbsp   Reinoso E. Denis \
    	(reinoso.denis@gmail.com)<br><br>Universidad Nacional de Córdoba<br>Facultad\
        de Ciencias Exactas Físicas y Naturales</center>")

def waitEvents(request):
    """Se esperan eventos o mensajes de la Placa para realizar acciones según corresponda"""
    global emailModule,led1State,led2State,backyardState,events
    while(True):
        print 'Se esta esperando un evento...'
        event = processingModule.microcontrollerInstance.readOutput()
        newEvent = ''
        if event == 'motion_on':
            print time.ctime() + ': Se ha detectado movimiento!'
            newEvent = time.ctime() + ': Se ha detectado movimiento!'
            #emailModule.sendEmail('reinoso.denis@gmail.com', 'Notificación - Sistema de ontrol', newEvent)
        elif event == 'motion_off':
            print time.ctime() + ': Ya no hay movimiento!'
            newEvent = time.ctime() + ': Ya no hay movimiento!'
        elif event == 'light_on':  
            print time.ctime() + ': Oscurecio y la lampara fue encendida!'
            newEvent = time.ctime() + ': Oscurecio y la lampara fue encendida!'
            backyardState = 'prendido'
            #emailModule.sendEmail('reinoso.denis@gmail.com', 'Notificación - Sistema de ontrol', newEvent)
        elif event == 'light_off':
            print time.ctime() + ': Hay suficiente luz y la lampara fue apagada!'
            newEvent = time.ctime() + ': Hay suficiente luz y la lampara fue apagada!'
            backyardState = 'apagado'
        elif event == 'room01_on' or event == 'room01_led_on':
            print time.ctime() + ': La lampara de la Habitacion 01 fue encendida!'
            newEvent = time.ctime() + ': La lampara de la Habitacion 01 fue encendida!'
            led1State = 'prendido'
        elif event == 'room01_off' or event == 'room01_led_off':
            print time.ctime() + ': La lampara de la Habitacion 01 fue apagada!'
            newEvent = time.ctime() + ': La lampara de la Habitacion 01 fue apagada!'
            led1State = 'apagado'
        elif event == 'room02_on' or event == 'room02_led_on':
            print time.ctime() + ': La lampara de la Habitacion 02 fue encendida!'
            newEvent = time.ctime() + ': La lampara de la Habitacion 02 fue encendida!'
            led2State = 'prendido'
        elif event == 'room02_off' or event == 'room02_led_off':
            print time.ctime() + ': La lampara de la Habitacion 02 fue apagada!'
            newEvent = time.ctime() + ': La lampara de la Habitacion 02 fue apagada!'
            led2State = 'apagado'
        addEvent(newEvent)

def stopAplication(request):
    """Se para la aplicación, se reinicia la lista de eventos y se vuelvo a Index"""
    global eventThread,running,events
    for i in events[:]:
        events.remove(i)
    print 'ho pero si la aplicación se ha aprado'
    #eventThread.stop() -- No se pueden parar hilos..
    #running = False
    return render_to_response("main/index.html")

def addEvent(newEvent):
    """Para añadir un evento de modo que el ultimo añadido sea el primero y solo se
    almacenen hasta 10 eventos"""
    global events
    events.insert(0,newEvent)
    if len(events)>10:
        events.pop()