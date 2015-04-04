#as3:/usr/local/lib/python2.7/site-packages# cat sitecustomize.py
# encoding=utf8  

from django.db import models
import sys
reload(sys) # Para que no tire error de codificación
sys.setdefaultencoding('utf8')
#sys.path.append('IlluminationControlSystem')
#from IlluminationControlSystem import contactList, emailModule, enums, frdmClass, modemClass, processingModule, timerClass

