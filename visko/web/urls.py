from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^home/?$', views.home, name='home'),
    url(r'^delphin-viz/?$', views.delviz, name='delviz'),
    url(r'^isf/?$', views.isf, name='isf'),
    # development features
    url(r'^dev/?$', views.dev, name='dev'),
    url(r'^dev/(?P<mode>\w+)?$', views.dev, name='dev'),
    url(r'^devrest/?$', views.dev_rest, name='dev_rest'),
    # search
    url(r'^search/?$', views.search, name='search'),
    url(r'^search/(?P<sid>\d+)/?$', views.search, name='search_results'),
    # corpus management
    url(r'^create_collection/?$', views.create_collection, name='create_collection'),
    url(r'^create_corpus/(?P<collection_name>\w+)/?$', views.create_corpus, name='create_corpus'),
    url(r'^create_doc/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/?$', views.create_doc, name='create_doc'),
    url(r'^create_sent/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/?$', views.create_sent, name='create_sent'),
    url(r'^delete_sent/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/(?P<sent_id>\w+)/?$', views.delete_sent, name='delete_sent'),
    url(r'^corpus/?$', views.list_collection, name='list_collection'),
    url(r'^corpus/(?P<collection_name>\w+)/?$', views.list_corpus, name='list_corpus'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/?$', views.list_doc, name='list_doc'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/?$', views.list_sent, name='list_sent'),
    url(r'^corpus/(?P<collection_name>\w+)/(?P<corpus_name>\w+)/(?P<doc_id>\w+)/(?P<sent_id>\w+)/?$', views.list_parse, name='list_parse'),
    url(r'^corpus/(?P<col>\w+)/(?P<cor>\w+)/(?P<did>\w+)/(?P<sid>\w+)/(?P<pid>\w+)/?$', views.view_parse, name='view_parse'),

    # REST APIs
    url(r'^rest/corpus/(?P<col>\w+)/(?P<cor>\w+)/(?P<did>\w+)/(?P<sid>\w+)/?$', views.rest_fetch, name='rest_fetch_sent'),
    url(r'^rest/corpus/(?P<col>\w+)/(?P<cor>\w+)/(?P<did>\w+)/(?P<sid>\w+)/(?P<pid>\w+)/?$', views.rest_fetch, name='rest_fetch_dmrs'),
    url(r'^rest/corpus/(?P<col>\w+)/(?P<cor>\w+)/(?P<did>\w+)/(?P<sid>\w+)/(?P<pid>\w+)/parse/?$', views.rest_dmrs_parse, name='rest_dmrs_parse'),
    url(r'^rest/corpus/(?P<col>\w+)/(?P<cor>\w+)/(?P<did>\w+)/(?P<sid>\w+)/(?P<pid>\w+)/delete/?$', views.rest_dmrs_delete, name='rest_dmrs_delete'),
    url(r'^rest/corpus/(?P<col>\w+)/(?P<cor>\w+)/(?P<did>\w+)/(?P<sid>\w+)/(?P<pid>\w+)/(?P<action>insert|replace)/?$', views.rest_dmrs_save, name='rest_dmrs_save'),
]
