from django.conf.urls import url

from . import views

app_name = "requester"

urlpatterns = [
    url(r'^$', views.RequestView, name='request'),


]