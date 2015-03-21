# encoding=utf8  

from django.shortcuts import render
from django.shortcuts import render_to_response
from main.models import Bebida
from django.http import HttpResponse
from django.template import RequestContext, loader

from IlluminationControlSystem import processingModule

def index(request):
    #return HttpResponse("Sistemas de Computación \n     Trabajo Final")
    #template = loader.get_template('main/index.html')
    #return HttpResponse("<p>Sistemas de Computación</p> <p>     Trabajo Final</p>")
    #bebida = Bebida()
    #bebida.contador = 20
    #bebida.sumar()
    print "Estas en el Index"
    return render_to_response('main/index.html')

def showState(request):
    stateList = processingModule.reportCommand()
    #stateList = ["prendido", "apagado", "stat de backyard?"]
    stateList0 = checkState(stateList[0])
    stateList1 = checkState(stateList[1])
    stateList2 = checkState(stateList[2])
    return render_to_response("main/showState.html",{"stateList0": stateList0, "stateList1": stateList1, "stateList2": stateList2})

def switchLed1(request):
    stateLed1 = processingModule.roomCommand("room01_toggle")
    stateLed1 = checkState(stateLed1)
    #stateLed1 = "prendido"
    return render_to_response("main/switchLed1.html",{"stateLed1": stateLed1})
   
def switchLed2(request):
    stateLed2 = processingModule.roomCommand("room02_toggle")
    stateLed2 = checkState(stateLed2)
    #stateLed2 = "apagado"
    return render_to_response("main/switchLed2.html",{"stateLed2": stateLed2})

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