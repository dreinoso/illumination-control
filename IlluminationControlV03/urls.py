from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from main import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^index', views.index),
    url(r'^running', views.startAplication),
    url(r'^stopAplication', views.stopAplication),
    url(r'^switchLed1', views.switchLed1, name='switchLed1'),
    url(r'^switchLed2', views.switchLed2, name='switchLed2'),
    url(r'^about', views.about, name='about'),
)
