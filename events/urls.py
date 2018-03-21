from django.conf.urls import url

from . import views

app_name = 'events'

urlpatterns = [
    url(r'^api/', views.all_events, name='all_events'),
    url(r'^(?P<event_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^$', views.index, name='index'),
]