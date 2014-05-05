from django.conf.urls import patterns, url
from lisa.plugins.Shopping.web import views

urlpatterns = patterns('',
    url(r'^$',views.index),
)
