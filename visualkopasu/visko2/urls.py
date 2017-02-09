from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^home/?$', views.home, name='home'),
    url(r'^delphin-viz/?$', views.delviz, name='delviz'),
    url(r'^isf/?$', views.isf, name='isf'),
    url(r'^dev/?$', views.dev, name='dev'),
    url(r'^corpus/?$', views.list_collection, name='list_collection'),
    url(r'^corpus/(?P<collection_name>\w+)/?$', views.list_corpus, name='list_corpus'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/?$', views.list_doc, name='list_doc'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/?$', views.list_sent, name='list_sent'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/(?P<sent_id>\w+)/?$', views.list_parse, name='list_parse')
]
