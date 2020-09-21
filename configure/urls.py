from django.conf.urls import url

from . import views

app_name = "configure"

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/delete/$', views.SourceDeleteView.as_view(), name='delete'),
    url(r'^(?P<pk>[0-9]+)/$', views.SourceUpdateView.as_view(), name='update'),
    url(r'^create-source/$', views.SourceCreateView.as_view(), name='create'),
    url(r'^source-list/$', views.SourceListView.as_view(), name='list'),
    url(r'^(?P<pk>[0-9]+)/$', views.SourceDetailView.as_view(), name='detail'),

]
