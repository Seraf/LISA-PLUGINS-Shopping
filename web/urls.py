from django.conf.urls import patterns, url
from Shopping.web import views

urlpatterns = patterns('',
    url(r'^$',views.index),
)
