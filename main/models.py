#as3:/usr/local/lib/python2.7/site-packages# cat sitecustomize.py
# encoding=utf8  

from django.db import models
import sys
reload(sys) # Para que no tire error de codificación
sys.setdefaultencoding('utf8')
#sys.path.append('IlluminationControlSystem')
#from IlluminationControlSystem import contactList, emailModule, enums, frdmClass, modemClass, processingModule, timerClass

class Bebida(models.Model):
#	nombre = models.CharField(max_length=50)
 	ingredientes = models.TextField()
 	preparacion = models.TextField()
 	contador = 0

 	def __init__(self):
 		self.contador = 0

 	def sumar(self):
 		algo = 0
 		for x in xrange(1,10):
 			algo = algo + 1
 		self.contador = self.contador + 1

 	def getContador(self):
 		return contador
# class System(models.Model):
# 	self.led1State = ''
#     self.led2State = ''
#     self.backyardState = ''
#     self.events = ''
#     self.started = True
    
#  	def __init__(self):
#  		self.led1State = 'apagada'
#     	self.led2State = 'apagada'
#     	self.backyardState = 'apagada'
#     	self.events = 'Sin eventos'
#     	self.started = True
