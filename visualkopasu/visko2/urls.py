from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^home/?$', views.home, name='home'),
    url(r'^delphin-viz/?$', views.delviz, name='delviz'),
    url(r'^isf/?$', views.isf, name='isf'),
    url(r'^dev/?$', views.dev, name='dev'),
    url(r'^create_collection/?$', views.create_collection, name='create_collection'),
    url(r'^create_corpus/(?P<collection_name>\w+)/?$', views.create_corpus, name='create_corpus'),
    url(r'^create_doc/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/?$', views.create_doc, name='create_doc'),
    url(r'^create_sent/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/?$', views.create_sent, name='create_sent'),
    url(r'^reparse_sent/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/(?P<sent_id>\w+)/?$', views.reparse_sent, name='reparse_sent'),
    url(r'^edit_parse/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/(?P<sent_id>\w+)/(?P<parse_id>\w+)/(?P<mode>\w+)/?$', views.edit_parse, name='edit_parse'),
    url(r'^delete_sent/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/(?P<sent_id>\w+)/?$', views.delete_sent, name='delete_sent'),
    url(r'^corpus/?$', views.list_collection, name='list_collection'),
    url(r'^corpus/(?P<collection_name>\w+)/?$', views.list_corpus, name='list_corpus'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/?$', views.list_doc, name='list_doc'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/?$', views.list_sent, name='list_sent'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/(?P<sent_id>\w+)/?$', views.list_parse, name='list_parse'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/(?P<sent_id>\w+)/(?P<parse_id>\w+)/?$', views.view_parse, name='view_parse')
]
