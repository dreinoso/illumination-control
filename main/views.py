# encoding=utf8  

from django.shortcuts import render
from django.shortcuts import render_to_response
from main.models import Bebida
from django.http import HttpResponse
from django.template import RequestContext, loader

from IlluminationControlSystem import processingModule
import threading
import time

def index(request):
    #return HttpResponse("Sistemas de Computación \n     Trabajo Final")
    #template = loader.get_template('main/index.html')
    #return HttpResponse("<p>Sistemas de Computación</p> <p>     Trabajo Final</p>")
    #bebida = Bebida()
    #bebida.contador = 20
    #bebida.sumar()
    print "Estas en el Index"
    return render_to_response('main/index.html')

def startAplication(request):
    global running,eventThread,emailModule,led1State,led2State,backyardState,events
    if not running:
        #eventThread.start()
        processingModule.roomCommand("room01_stats")
        #time.sleep(1)
        processingModule.roomCommand("room02_stats")
        #time.sleep(1)
        processingModule.roomCommand("backyard_stats")
        #time.sleep(1)
        events = ''
        running = True
        waitEvents(request)
    return render_to_response("main/running.html",{"led1State": led1State, "led2State": led2State, "backyardState": backyardState, "events": events})

def switchLed1(request):
    processingModule.roomCommand("room01_toggle")
    #global led1State,led2State,backyardState,events
    #time.sleep(1)
    #return render_to_response("main/running.html",{"led1State": led1State, "led2State": led2State, "backyardState": backyardState, "events": events})
    return render_to_response("main/switchLed1.html")
       
def switchLed2(request):
    processingModule.roomCommand("room02_toggle")
    #global led1State,led2State,backyardState,events
    #time.sleep(1)
    #return render_to_response("main/running.html",{"led1State": led1State, "led2State": led2State, "backyardState": backyardState, "events": events})
    return render_to_response("main/switchLed2.html")
 
def about(request):
    return HttpResponse("<center>Este trabajo corresponde a un desarrollo de domótica para \
    	el control de iluminación de una vivienda <br><br> Autores:<br>&nbsp   \
    	Gonzalez L. Mauricio (mauricio.lg@gmail.com)<br>&nbsp   Reinoso E. Denis \
    	(reinoso.denis@gmail.com)<br><br>Universidad Nacional de Córdoba<br>Facultad\
        de Ciencias Exactas Físicas y Naturales</center>")

def checkState(state):
    if state.find('on')>1:
        return 'prendido'
    else:
        return 'apagado'

def waitEvents(request):
    global emailModule,led1State,led2State,backyardState,events
    while(True):
        print 'Se esta esperando un evento...'
        event = processingModule.microcontrollerInstance.readOutput()
        if event == 'motion_on':
                #modemClass.motionSensor_flag = True
                #emailModule.motionSensor_flag = True
            print time.ctime() + ': Se ha detectado movimiento!'
            events = events + '\n' + time.ctime() + ': Se ha detectado movimiento!'
        elif event == 'motion_off':
            print time.ctime() + ': Ya no hay movimiento!'
            events = events + '\n' + time.ctime() + ': Ya no hay movimiento!'
        elif event == 'light_on':  
            print time.ctime() + ': Oscurecio y la lampara fue encendida!'
            events = events + '\n' + time.ctime() + ': Oscurecio y la lampara fue encendida!'
            backyardState = 'prendido'
        elif event == 'light_off':
            print time.ctime() + ': Hay suficiente luz y la lampara fue apagada!'
            events = events + '\n' + time.ctime() + ': Hay suficiente luz y la lampara fue apagada!'
            backyardState = 'apagado'
        elif event == 'room01_on' or event == 'room01_led_on':
            print time.ctime() + ': La lampara de la Habitacion 01 fue encendida!'
            events = events + '\n' + time.ctime() + ': La lampara de la Habitacion 01 fue encendida!'
            led1State = 'prendido'
        elif event == 'room01_off' or event == 'room01_led_off':
            print time.ctime() + ': La lampara de la Habitacion 01 fue apagada!'
            events = events + '\n' + time.ctime() + ': La lampara de la Habitacion 01 fue apagada!'
            led1State = 'apagado'
        elif event == 'room02_on' or event == 'room02_led_on':
            print time.ctime() + ': La lampara de la Habitacion 02 fue encendida!'
            events = events + '\n' + time.ctime() + ': La lampara de la Habitacion 02 fue encendida!'
            led2State = 'prendido'
        elif event == 'room02_off' or event == 'room02_led_off':
            print time.ctime() + ': La lampara de la Habitacion 02 fue apagada!'
            events = events + '\n' + time.ctime() + ': La lampara de la Habitacion 02 fue apagada!'
            led2State = 'apagado'
        updateRunning(request)
    return render_to_response("main/running.html",{"led1State": led1State, "led2State": led2State, "backyardState": backyardState, "events": events})


def updateRunning(request):
    global led1State,led2State,backyardState,events
    print '------------------------------------------------'
    return render_to_response("main/running.html",{"led1State": led1State, "led2State": led2State, "backyardState": backyardState, "events": events})

def stopAplication(request):
    global eventThread,running
    #eventThread.stop() -- No se pueden parar hilos..
    #running = False
    return render_to_response("main/index.html")

running = False
led1State ='apagado'
led2State ='apagado'
backyardState ='apagado'
events =''
#eventThread = threading.Thread(target = waitEvents)